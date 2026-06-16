#!/usr/bin/env python3
"""Generate register random configuration from reg_data.h and selection JSON.

The tool parses all registers under t_reg_vcpi from reg_data.h, filters active
registers via register_selection.json, generates random values, then writes cmd.cfg.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ERR_SELECTION_FILE_MISSING = "E_SELECTION_FILE_MISSING"
ERR_SELECTION_JSON_INVALID = "E_SELECTION_JSON_INVALID"
ERR_SELECTION_SCHEMA_INVALID = "E_SELECTION_SCHEMA_INVALID"
ERR_SELECTION_TARGET_NOT_FOUND = "E_SELECTION_TARGET_NOT_FOUND"
ERR_SELECTION_EMPTY_ACTIVE_SET = "E_SELECTION_EMPTY_ACTIVE_SET"
ERR_HEADER_STRUCT_NOT_FOUND = "E_HEADER_STRUCT_NOT_FOUND"
ERR_SELECTION_ARRAY_MISSING_INDICES = "E_SELECTION_ARRAY_MISSING_INDICES"
ERR_SELECTION_ARRAY_INDEX_OUT_OF_RANGE = "E_SELECTION_ARRAY_INDEX_OUT_OF_RANGE"

# ---------------------------------------------------------------------------
# Field constraint table extracted from vcpi.xlsx (2026-06-12).
# Keys: (register_name, field_name)
# Values: dict with optional keys:
#   "c": ('fixed', value) | ('range', lo, hi)  -- column J constraint
#   "r": int                                    -- column H reset value
#   "d": str                                    -- column I description snippet
#   "w": int                                    -- column G bit-width (validated)
#   "a": dict                                   -- column I alignment constraints
#                                                  e.g. {'hevc': 8, 'h264': 16}
#                                                  or {'default': 4}
#   "m": True                                   -- minus1 config (actual_value = config_value + 1)
#                                                  Alignment applies to actual value, not config value
# Fields absent from this table are randomised over their full bit-width range.
# Fields with only "r" (no "c") use the reset value as randomisation baseline.
# Fields with "a" use aligned random generation (see pick_aligned).
# Fields with "m": True use minus1 storage format (e.g., ve_pic_width/height).
# ---------------------------------------------------------------------------
VCPI_FIELD_CONSTRAINTS = {
    ("VCPI_BITBUF_ADDR_HI", "ve_bitbuf_addr_hi"): {"d": 'Higher 7bit Address\nBitbuf base addr for parser_core0 to store bitstream,when wr', "w": 7},
    ("VCPI_BITBUF_ADDR_LO", "ve_bitbuf_addr_lo"): {"d": 'Lower 32bit Address\nBitbuf base addr for parser_core0 to store bitstream,when wr', "w": 32},
    ("VCPI_BITBUF_LEN", "ve_bitbuf_len"): {"d": 'Byte length for BIT_buf0,16byte align', "w": 31},
    ("VCPI_BND_BUF_SIZE", "ve_bnd_buf_size"): {"d": 'The buf size of row buffer in external memory,16byte align', "w": 32},
    ("VCPI_BND_ROW_ADDR_HI", "ve_bnd_row_addr_hi"): {"d": 'Higher 7bit Address,Row base addr for bnd_ctrl', "w": 7},
    ("VCPI_BND_ROW_ADDR_LO", "ve_bnd_row_addr_lo"): {"d": 'Lower 32bit Address\nRow base addr for bnd_ctrl,16byte align', "w": 32},
    ("VCPI_BUS_CTRL", "ve_bus_ctrl"): {"r": 3, "d": 'This field configures how the video processor performs AXI burst accesses. The v', "w": 2},
    ("VCPI_CLK_FORCE0", "ve_bndctrl_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'BND_CTRL', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_cpixdmov_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'CPIX_DMOV', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_curld_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'CURLD', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_dbk_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'DBK', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_dsctrl_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'DS_CTRL', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_fme_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'FME', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_ime_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'IME', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_intra_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'INTRA', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_l2c_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'L2C', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_mmu_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'MMU', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_mvp_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'MVP', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_nbi_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'NBI', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_optdmov_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'OPTDMOV', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pack_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'ALFENC', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pintra_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'PINTRA', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pipe_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Pipe Engine', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pixctrl_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'PIX_CTRL', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pme_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'PME', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pmest_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'PMEST', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_pmf_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'PMF', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_qpg_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'QPG', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_recst_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'ALFDEC', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_refld_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'REFLD', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_rpixctrl_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'RPIX_DMOV', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_saodec_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'SAODEC', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_saoenc_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'SAOENC', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_sel_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'SEL', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_tqitq_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'TQITQ', "w": 1},
    ("VCPI_CLK_FORCE0", "ve_vctrl_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'VCTRL', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_bsdma_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'BS_DMA', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_h4cabac_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'CABAC', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_h4cabad_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'CABAD', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_h5cabac_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'HCABAC', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_h5cabad_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'HCABAD', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_jvlc_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'JVLC', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_jvld_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'JVLD', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_parser_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Parser Engine', "w": 1},
    ("VCPI_CLK_FORCE1", "ve_sed_clkforce_en"): {"c": ('range', 0, 1), "r": 0, "d": 'SED', "w": 1},
    ("VCPI_COL_LOAD_ADDR_HI", "ve_col_load_addr_hi"): {"d": 'Higher 7bit Address,Col load base addr for bnd_ctrl', "w": 7},
    ("VCPI_COL_LOAD_ADDR_LO", "ve_col_load_addr_lo"): {"d": 'Lower 32bit Address\nCol load base addr for bnd_ctrl,16byte align', "w": 32},
    ("VCPI_COL_STORE_ADDR_HI", "ve_col_store_addr_hi"): {"d": 'Higher 7bit Address,Col store base addr for bnd_ctrl', "w": 7},
    ("VCPI_COL_STORE_ADDR_LO", "ve_col_store_addr_lo"): {"d": 'Lower 32bit Address\nCol store base addr for bnd_ctrl,16byte align', "w": 32},
    ("VCPI_COL_TOTAL_WORD", "ve_col_total_word"): {"d": 'HEVC:\n\nA= (((IMG_WIDTH_Align64/64)*16) x 48bit/8)/4\nB= IMG_HEIGHT_Align64/64\ntot', "w": 21},
    ("VCPI_DOWNSAMPLE_STRIDE_0", "ve_ds_stride0"): {"d": 'Distance between two quad rows for PMEST/DS_CTRL to fetch list0 ds_data\n16bytes ', "w": 32},
    ("VCPI_DOWNSAMPLE_STRIDE_1", "ve_ds_stride0"): {"d": 'Distance between two quad rows for PMEST/DS_CTRL to fetch list1 ds_data\n16bytes ', "w": 32},
    ("VCPI_DS_LOAD_ADDR_HI", "ve_ds_load_addr_hi"): {"d": 'Higher 7bit Address\nDS load base addr for ds_ctrl', "w": 7},
    ("VCPI_DS_LOAD_ADDR_LO", "ve_ds_load_addr_lo"): {"d": 'Lower 32bit Address\nDS load base addr for ds_ctrl,16byte align', "w": 32},
    ("VCPI_DS_LOAD_BASE_HI_0", "ve_ds_load0_base_hi"): {"d": 'High 7bit Base address for ds_load to load downsample data for L0', "w": 7},
    ("VCPI_DS_LOAD_BASE_HI_1", "ve_ds_load1_base_hi"): {"d": 'High 7bit Base address for ds_load to load downsample data for L1', "w": 7},
    ("VCPI_DS_LOAD_BASE_LO_0", "ve_ds_load0_base_lo"): {"d": 'Lowe 32bit Base address for ds_load to load downsample data for L0,16bytes align', "w": 32},
    ("VCPI_DS_LOAD_BASE_LO_1", "ve_ds_load1_base_lo"): {"d": 'Lowe 32bit Base address for ds_load to load downsample data for L1,16bytes align', "w": 32},
    ("VCPI_DS_STORE_ADDR_HI", "ve_ds_store_addr_hi"): {"d": 'Higher 7bit Address\nDS store base addr for ds_ctrl', "w": 7},
    ("VCPI_DS_STORE_ADDR_LO", "ve_ds_store_addr_lo"): {"d": 'Lower 32bit Address\nDS store base addr for ds_ctrl,16byte align', "w": 32},
    ("VCPI_EOP_IND", "ve_frame_eop"): {"d": 'The Signal indicate that the whole frame configrataion is finish', "w": 1},
    ("VCPI_FBC_LUT_BASE_HI", "ve_fbc_lut_base_hi"): {"d": 'Base High32 address of virtual 39bit address for FBC headers from the FBC encode', "w": 32},
    ("VCPI_FBC_LUT_BASE_LO", "ve_fbc_lut_base_lo"): {"d": 'Base Lower32 address for FBC headers from the FBC encoder.\nFBC LUT base address.', "w": 32},
    ("VCPI_FBC_SLICE_BUF_BASE_HI", "ve_fbc_slice_buffer_base_hi"): {"d": 'High 32bt address\nFBC SLICE Buffer base address.', "w": 32},
    ("VCPI_FBC_SLICE_BUF_BASE_LO", "ve_fbc_slice_buffer_base_lo"): {"d": 'Lower 32bit address\nFBC SLICE Buffer base address. Must be 256 bytes aligned and', "w": 32},
    ("VCPI_FBC_SLICE_BUF_SIZE", "ve_fbc_slice_bufsize"): {"d": 'FBC SLICE Buffer memory space size in byte in ring buffer mode. \nSLICE_BUF_SIZE ', "w": 32},
    ("VCPI_FBC_SLICE_RING_OFFSET", "ve_fbc_slice_ring_buffer_offset"): {"d": 'FBC SLICE Buffer CURRENT frame base address offset from SLICE_BUF_BASE in ring b', "w": 32},
    ("VCPI_FBC_SLICE_STRIDE", "ve_fbc_slice_stride"): {"d": 'FBC SLICE stride. Uncompressed size of an 8-pixel height row (SLICE). Must be 25', "w": 18},
    ("VCPI_FORCE_PERIOD_INTRA", "ve_force_intra_ctu_period"): {"d": 'Force intra prediction every N CTUs for cyclic intra refresh', "w": 15},
    ("VCPI_FORCE_PERIOD_INTRA", "ve_force_intra_ctu_row"): {"d": 'Force consecutive CTU rows to intra for GDR', "w": 10},
    ("VCPI_FRO_AC_0", "ve_ac_luma_iii_16x16"): {"c": ('range', 0, 255), "r": 255, "d": 'ac_luma_iii_16x16:\nquant parameter，HEVC :AC luma intra in I frame, 16x16\nH264 :A', "w": 8},
    ("VCPI_FRO_AC_0", "ve_ac_luma_iii_32x32"): {"c": ('range', 0, 255), "r": 255, "d": 'ac_luma_iii_32x32:\nquant parameter，HEVC :AC luma intra in I frame, 32x32\nH264 :A', "w": 8},
    ("VCPI_FRO_AC_0", "ve_ac_luma_iii_64x64"): {"c": ('range', 0, 255), "r": 255, "d": 'ac_luma_iii_64x64:\nquant parameter，HEVC :AC luma intra in I frame, 64x64(ony use', "w": 8},
    ("VCPI_FRO_AC_0", "ve_ac_luma_iii_8x8"): {"c": ('range', 0, 255), "r": 255, "d": 'ac_luma_iii_8x8:\nquant parameter，HEVC :AC luma intra in I frame, 8x8\nH264 :AC lu', "w": 8},
    ("VCPI_FRO_AC_1", "ve_ac_luma_iip_16x16"): {"c": ('range', 0, 255), "r": 164, "d": 'ac_luma_iip_16x16:\nquant parameter，HEVC :AC luma intra in P/B frame, 16x16\nH264 ', "w": 8},
    ("VCPI_FRO_AC_1", "ve_ac_luma_iip_32x32"): {"c": ('range', 0, 255), "r": 192, "d": 'ac_luma_iip_32x32:\nquant parameter，HEVC :AC luma intra in P/B frame, 32x32\nH264 ', "w": 8},
    ("VCPI_FRO_AC_1", "ve_ac_luma_iip_64x64"): {"c": ('range', 0, 255), "r": 192, "d": 'ac_luma_iip_64x64:\nquant parameter，HEVC :AC luma intra in P/B frame, 64x64(ony u', "w": 8},
    ("VCPI_FRO_AC_1", "ve_ac_luma_iip_8x8"): {"c": ('range', 0, 255), "r": 156, "d": 'ac_luma_iip_8x8:\nquant parameter，HEVC :AC luma intra in P/B frame, 8x8\nH264 :AC ', "w": 8},
    ("VCPI_FRO_AC_2", "ve_ac_luma_eip_16x16"): {"c": ('range', 0, 255), "r": 132, "d": 'ac_luma_eip_16x16:\nquant parameter，HEVC :AC luma inter in P/B frame, 16x16\nH264 ', "w": 8},
    ("VCPI_FRO_AC_2", "ve_ac_luma_eip_32x32"): {"c": ('range', 0, 255), "r": 140, "d": 'ac_luma_eip_32x32:\nquant parameter，HEVC :AC luma inter in P/B frame, 32x32\nH264 ', "w": 8},
    ("VCPI_FRO_AC_2", "ve_ac_luma_eip_64x64"): {"c": ('range', 0, 255), "r": 140, "d": 'ac_luma_eip_64x64:\nquant parameter，HEVC :AC luma inter in P/B frame, 64x64(ony u', "w": 8},
    ("VCPI_FRO_AC_2", "ve_ac_luma_eip_8x8"): {"c": ('range', 0, 255), "r": 124, "d": 'ac_luma_eip_8x8:\nquant parameter，HEVC :AC luma inter in P/B frame, 8x8\nH264 :AC ', "w": 8},
    ("VCPI_FRO_AC_3", "ve_ac_chroma_iii_16x16"): {"c": ('range', 0, 255), "r": 250, "d": 'ac_chroma_iii_16x16:\nquant parameter，HEVC :AC chroma intra in I frame, 16x16\nH26', "w": 8},
    ("VCPI_FRO_AC_3", "ve_ac_chroma_iii_32x32"): {"c": ('range', 0, 255), "r": 250, "d": 'ac_chroma_iii_32x32:\nquant parameter，HEVC :AC chroma intra in I frame, 32x32(unu', "w": 8},
    ("VCPI_FRO_AC_3", "ve_ac_chroma_iii_4x4"): {"c": ('range', 0, 255), "r": 240, "d": 'ac_chroma_iii_4x4:\nquant parameter，HEVC :AC chroma intra in I frame, 4x4\nH264 :A', "w": 8},
    ("VCPI_FRO_AC_3", "ve_ac_chroma_iii_8x8"): {"c": ('range', 0, 255), "r": 245, "d": 'ac_chroma_iii_8x8:\nquant parameter，HEVC :AC chroma intra in I frame, 8x8\nH264 :A', "w": 8},
    ("VCPI_FRO_AC_4", "ve_ac_chroma_iip_16x16"): {"c": ('range', 0, 255), "r": 160, "d": 'ac_chroma_iip_16x16:\nquant parameter，HEVC :AC chroma intra in P/B frame, 16x16\nH', "w": 8},
    ("VCPI_FRO_AC_4", "ve_ac_chroma_iip_32x32"): {"c": ('range', 0, 255), "r": 160, "d": 'ac_chroma_iip_32x32:\nquant parameter，HEVC :AC chroma intra in P/B frame, 32x32(u', "w": 8},
    ("VCPI_FRO_AC_4", "ve_ac_chroma_iip_4x4"): {"r": 132, "d": 'ac_chroma_iip_4x4:\nquant parameter，HEVC :AC chroma intra in P/B frame, 4x4\nH264 ', "w": 8},
    ("VCPI_FRO_AC_4", "ve_ac_chroma_iip_8x8"): {"c": ('range', 0, 255), "r": 140, "d": 'ac_chroma_iip_8x8:\nquant parameter，HEVC :AC chroma intra in P/B frame, 8x8\nH264 ', "w": 8},
    ("VCPI_FRO_AC_5", "ve_ac_chroma_eip_16x16"): {"r": 126, "d": 'ac_chroma_eip_16x16:\nquant parameter，HEVC :AC chroma inter in P/B frame, 16x16\nH', "w": 8},
    ("VCPI_FRO_AC_5", "ve_ac_chroma_eip_32x32"): {"c": ('range', 0, 63), "r": 126, "d": 'ac_chroma_eip_32x32:\nquant parameter，HEVC :AC chroma inter in P/B frame, 32x32(u', "w": 8},
    ("VCPI_FRO_AC_5", "ve_ac_chroma_eip_4x4"): {"r": 114, "d": 'ac_chroma_eip_4x4:\nquant parameter，HEVC :AC chroma inter in P/B frame, 4x4\nH264 ', "w": 8},
    ("VCPI_FRO_AC_5", "ve_ac_chroma_eip_8x8"): {"c": ('range', 0, 63), "r": 120, "d": 'ac_chroma_eip_8x8:\nquant parameter，HEVC :AC chroma inter in P/B frame, 8x8\nH264 ', "w": 8},
    ("VCPI_FRO_DC_0", "ve_dc_luma_iii_16x16"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_luma_iii_16x16:\nquant parameter，HEVC :DC luma intra in I frame, 16x16\nH264 :D', "w": 8},
    ("VCPI_FRO_DC_0", "ve_dc_luma_iii_32x32"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_luma_iii_32x32:\nquant parameter，HEVC :DC luma intra in I frame, 32x32\nH264 :D', "w": 8},
    ("VCPI_FRO_DC_0", "ve_dc_luma_iii_64x64"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_luma_iii_64x64:\nquant parameter，DC luma intra in I frame, 64x64(ony use in VV', "w": 8},
    ("VCPI_FRO_DC_0", "ve_dc_luma_iii_8x8"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_luma_iii_8x8:\nquant parameter，HEVC :DC luma intra in I frame, 8x8\nH264 :DC lu', "w": 8},
    ("VCPI_FRO_DC_1", "ve_dc_luma_iip_16x16"): {"c": ('range', 0, 255), "r": 192, "d": 'dc_luma_iip_16x16:\nquant parameter，HEVC :DC luma intra in P/B frame, 16x16\nH264 ', "w": 8},
    ("VCPI_FRO_DC_1", "ve_dc_luma_iip_32x32"): {"c": ('range', 0, 255), "r": 200, "d": 'dc_luma_iip_32x32:\nquant parameter，HEVC :DC luma intra in P/B frame, 32x32\nH264 ', "w": 8},
    ("VCPI_FRO_DC_1", "ve_dc_luma_iip_64x64"): {"c": ('range', 0, 255), "r": 200, "d": 'dc_luma_iip_64x64:\nquant parameter，DC luma intra in P/B frame, 64x64(ony use in ', "w": 8},
    ("VCPI_FRO_DC_1", "ve_dc_luma_iip_8x8"): {"c": ('range', 0, 255), "r": 184, "d": 'dc_luma_iip_8x8:\nquant parameter，HEVC :DC luma intra in P/B frame, 8x8\nH264 :DC ', "w": 8},
    ("VCPI_FRO_DC_2", "ve_dc_luma_eip_16x16"): {"c": ('range', 0, 255), "r": 160, "d": 'dc_luma_eip_16x16:\nquant parameter，HEVC :DC luma inter in P/B frame, 16x16\nH264 ', "w": 8},
    ("VCPI_FRO_DC_2", "ve_dc_luma_eip_32x32"): {"c": ('range', 0, 255), "r": 168, "d": 'dc_luma_eip_32x32:\nquant parameter，HEVC :DC luma inter in P/B frame, 32x32\nH264 ', "w": 8},
    ("VCPI_FRO_DC_2", "ve_dc_luma_eip_64x64"): {"c": ('range', 0, 255), "r": 168, "d": 'dc_luma_eip_64x64:\nquant parameter，DC luma inter in P/B frame, 64x64(ony use in ', "w": 8},
    ("VCPI_FRO_DC_2", "ve_dc_luma_eip_8x8"): {"c": ('range', 0, 255), "r": 152, "d": 'dc_luma_eip_8x8:\nquant parameter，HEVC :DC luma inter in P/B frame, 8x8\nH264 :DC ', "w": 8},
    ("VCPI_FRO_DC_3", "ve_dc_chroma_iii_16x16"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_chroma_iii_16x16:\nquant parameter，HEVC :DC chroma intra in I frame, 16x16\nH26', "w": 8},
    ("VCPI_FRO_DC_3", "ve_dc_chroma_iii_32x32"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_chroma_iii_32x32:\nquant parameter，HEVC :DC chroma intra in I frame, 32x32(unu', "w": 8},
    ("VCPI_FRO_DC_3", "ve_dc_chroma_iii_4x4"): {"c": ('range', 0, 255), "r": 243, "d": 'dc_chroma_iii_4x4:\nquant parameter，HEVC :DC chroma intra in I frame, 4x4\nH264 :D', "w": 8},
    ("VCPI_FRO_DC_3", "ve_dc_chroma_iii_8x8"): {"c": ('range', 0, 255), "r": 255, "d": 'dc_chroma_iii_8x8:\nquant parameter，HEVC :DC chroma intra in I frame, 8x8\nH264 :D', "w": 8},
    ("VCPI_FRO_DC_4", "ve_dc_chroma_iip_16x16"): {"c": ('range', 0, 255), "r": 175, "d": 'dc_chroma_iip_16x16:\nquant parameter，HEVC :DC chroma intra in P/B frame, 16x16\nH', "w": 8},
    ("VCPI_FRO_DC_4", "ve_dc_chroma_iip_32x32"): {"c": ('range', 0, 255), "r": 175, "d": 'dc_chroma_iip_32x32:\nquant parameter，HEVC :DC chroma intra in P/B frame, 32x32(u', "w": 8},
    ("VCPI_FRO_DC_4", "ve_dc_chroma_iip_4x4"): {"c": ('range', 0, 255), "r": 156, "d": 'dc_chroma_iip_4x4:\nquant parameter，HEVC :DC chroma intra in P/B frame, 4x4\nH264 ', "w": 8},
    ("VCPI_FRO_DC_4", "ve_dc_chroma_iip_8x8"): {"c": ('range', 0, 255), "r": 164, "d": 'dc_chroma_iip_8x8:\nquant parameter，HEVC :DC chroma intra in P/B frame, 8x8\nH264 ', "w": 8},
    ("VCPI_FRO_DC_5", "ve_dc_chroma_eip_16x16"): {"c": ('range', 0, 255), "r": 154, "d": 'dc_chroma_eip_16x16:\nquant parameter，HEVC :DC chroma inter in P/B frame, 16x16\nH', "w": 8},
    ("VCPI_FRO_DC_5", "ve_dc_chroma_eip_32x32"): {"c": ('range', 0, 255), "r": 154, "d": 'dc_chroma_eip_32x32:\nquant parameter，HEVC :DC chroma inter in P/B frame, 32x32(u', "w": 8},
    ("VCPI_FRO_DC_5", "ve_dc_chroma_eip_4x4"): {"c": ('range', 0, 255), "r": 142, "d": 'dc_chroma_eip_4x4:\nquant parameter，HEVC :DC chroma inter in P/B frame, 4x4\nH264 ', "w": 8},
    ("VCPI_FRO_DC_5", "ve_dc_chroma_eip_8x8"): {"c": ('range', 0, 255), "r": 148, "d": 'dc_chroma_eip_8x8:\nquant parameter，HEVC :DC chroma inter in P/B frame, 8x8\nH264 ', "w": 8},
    ("VCPI_FRO_MX_0", "ve_mx_luma_iii_16x16"): {"r": 14, "d": 'mx_luma_iii_16x16:\nquant parameter，HEVC :last luma intra in I frame, 16x16\nH264 ', "w": 6},
    ("VCPI_FRO_MX_0", "ve_mx_luma_iii_32x32"): {"r": 30, "d": 'mx_luma_iii_32x32:\nquant parameter，HEVC :last luma intra in I frame, 32x32\nH264 ', "w": 6},
    ("VCPI_FRO_MX_0", "ve_mx_luma_iii_64x64"): {"r": 30, "d": 'mx_luma_iii_64x64:\nquant parameter，HEVC :last luma intra in I frame, 64x64(ony u', "w": 6},
    ("VCPI_FRO_MX_0", "ve_mx_luma_iii_8x8"): {"r": 6, "d": 'mx_luma_iii_8x8:\nquant parameter，HEVC :last luma intra in I frame, 8x8\nH264 :las', "w": 6},
    ("VCPI_FRO_MX_1", "ve_mx_luma_iip_16x16"): {"r": 14, "d": 'mx_luma_iip_16x16:\nquant parameter，HEVC :last luma intra in P/B frame, 16x16\nH26', "w": 6},
    ("VCPI_FRO_MX_1", "ve_mx_luma_iip_32x32"): {"r": 30, "d": 'mx_luma_iip_32x32:\nquant parameter，HEVC :last luma intra in P/B frame, 32x32\nH26', "w": 6},
    ("VCPI_FRO_MX_1", "ve_mx_luma_iip_64x64"): {"r": 30, "d": 'mx_luma_iip_64x64:\nquant parameter，HEVC :last luma intra in P/B frame, 64x64(ony', "w": 6},
    ("VCPI_FRO_MX_1", "ve_mx_luma_iip_8x8"): {"r": 6, "d": 'mx_luma_iip_8x8:\nquant parameter，HEVC :last luma intra in P/B frame, 8x8\nH264 :l', "w": 6},
    ("VCPI_FRO_MX_2", "ve_mx_luma_eip_16x16"): {"r": 14, "d": 'mx_luma_eip_16x16:\nquant parameter，HEVC :last luma inter in P/B frame, 16x16\nH26', "w": 6},
    ("VCPI_FRO_MX_2", "ve_mx_luma_eip_32x32"): {"r": 30, "d": 'mx_luma_eip_32x32:\nquant parameter，HEVC :last luma inter in P/B frame, 32x32\nH26', "w": 6},
    ("VCPI_FRO_MX_2", "ve_mx_luma_eip_64x64"): {"r": 30, "d": 'mx_luma_eip_64x64:\nquant parameter，HEVC :last luma inter in P/B frame, 64x64(ony', "w": 6},
    ("VCPI_FRO_MX_2", "ve_mx_luma_eip_8x8"): {"r": 6, "d": 'mx_luma_eip_8x8:\nquant parameter，HEVC :last luma inter in P/B frame, 8x8\nH264 :l', "w": 6},
    ("VCPI_FRO_MX_3", "ve_mx_chma_iii_16x16"): {"r": 14, "d": 'mx_chroma_iii_16x16:\nquant parameter，HEVC :last chroma intra in I frame, 16x16\nH', "w": 6},
    ("VCPI_FRO_MX_3", "ve_mx_chma_iii_32x32"): {"r": 14, "d": 'mx_chroma_iii_32x32:\nquant parameter，HEVC :last chroma intra in I frame, 32x32(u', "w": 6},
    ("VCPI_FRO_MX_3", "ve_mx_chma_iii_4x4"): {"r": 2, "d": 'mx_chroma_iii_4x4:\nquant parameter，HEVC :last chroma intra in I frame, 4x4\nH264 ', "w": 6},
    ("VCPI_FRO_MX_3", "ve_mx_chma_iii_8x8"): {"r": 6, "d": 'mx_chroma_iii_8x8:\nquant parameter，HEVC :last chroma intra in I frame, 8x8\nH264 ', "w": 6},
    ("VCPI_FRO_MX_4", "ve_mx_chma_iip_16x16"): {"r": 14, "d": 'mx_chroma_iip_16x16:\nquant parameter，HEVC :last chroma intra in P/B frame, 16x16', "w": 6},
    ("VCPI_FRO_MX_4", "ve_mx_chma_iip_32x32"): {"r": 14, "d": 'mx_chroma_iip_32x32:\nquant parameter，HEVC :last chroma intra in P/B frame, 32x32', "w": 6},
    ("VCPI_FRO_MX_4", "ve_mx_chma_iip_4x4"): {"r": 2, "d": 'mx_chroma_iip_4x4:\nquant parameter，HEVC :last chroma intra in P/B frame, 4x4\nH26', "w": 6},
    ("VCPI_FRO_MX_4", "ve_mx_chma_iip_8x8"): {"r": 6, "d": 'mx_chroma_iip_8x8:\nquant parameter，HEVC :last chroma intra in P/B frame, 8x8\nH26', "w": 6},
    ("VCPI_FRO_MX_5", "ve_mx_chma_eip_16x16"): {"r": 14, "d": 'mx_chroma_eip_16x16:\nquant parameter，HEVC :last chroma inter in P/B frame, 16x16', "w": 6},
    ("VCPI_FRO_MX_5", "ve_mx_chma_eip_32x32"): {"r": 14, "d": 'mx_chroma_eip_32x32:\nquant parameter，HEVC :last chroma inter in P/B frame, 32x32', "w": 6},
    ("VCPI_FRO_MX_5", "ve_mx_chma_eip_4x4"): {"c": ('range', 0, 63), "r": 2, "d": 'mx_chroma_eip_4x4:\nquant parameter，HEVC :last chroma inter in P/B frame, 4x4\nH26', "w": 6},
    ("VCPI_FRO_MX_5", "ve_mx_chma_eip_8x8"): {"c": ('range', 0, 63), "r": 6, "d": 'mx_chroma_eip_8x8:\nquant parameter，HEVC :last chroma inter in P/B frame, 8x8\nH26', "w": 6},
    ("VCPI_FRO_ST_0", "ve_st_luma_iii_16x16"): {"r": 6, "d": 'st_luma_iii_16x16:\nquant parameter，HEVC :step luma intra in I frame, 16x16\nH264 ', "w": 6},
    ("VCPI_FRO_ST_0", "ve_st_luma_iii_32x32"): {"r": 3, "d": 'st_luma_iii_32x32:\nquant parameter，HEVC :step luma intra in I frame, 32x32\nH264 ', "w": 6},
    ("VCPI_FRO_ST_0", "ve_st_luma_iii_64x64"): {"r": 3, "d": 'st_luma_iii_64x64:\nquant parameter，HEVC :step luma intra in I frame, 64x64(ony u', "w": 6},
    ("VCPI_FRO_ST_0", "ve_st_luma_iii_8x8"): {"r": 12, "d": 'st_luma_iii_8x8:\nquant parameter，HEVC :step luma intra in I frame, 8x8\nH264 :ste', "w": 6},
    ("VCPI_FRO_ST_1", "ve_st_luma_iip_16x16"): {"r": 8, "d": 'st_luma_iip_16x16:\nquant parameter，HEVC :step luma intra in P/B frame, 16x16\nH26', "w": 6},
    ("VCPI_FRO_ST_1", "ve_st_luma_iip_32x32"): {"r": 4, "d": 'st_luma_iip_32x32:\nquant parameter，HEVC :step luma intra in P/B frame, 32x32', "w": 6},
    ("VCPI_FRO_ST_1", "ve_st_luma_iip_64x64"): {"r": 4, "d": 'st_luma_iip_64x64:\nquant parameter，HEVC :step luma intra in P/B frame, 64x64(ony', "w": 6},
    ("VCPI_FRO_ST_1", "ve_st_luma_iip_8x8"): {"r": 16, "d": 'st_luma_iip_8x8:\nquant parameter，HEVC :step luma intra in P/B frame, 8x8\nH264 :s', "w": 6},
    ("VCPI_FRO_ST_2", "ve_st_luma_eip_16x16"): {"r": 8, "d": 'st_luma_eip_16x16:\nquant parameter，HEVC :step luma inter in P/B frame, 16x16\nH26', "w": 6},
    ("VCPI_FRO_ST_2", "ve_st_luma_eip_32x32"): {"r": 4, "d": 'st_luma_eip_32x32:\nquant parameter，HEVC :step luma inter in P/B frame, 32x32\nH26', "w": 6},
    ("VCPI_FRO_ST_2", "ve_st_luma_eip_64x64"): {"r": 4, "d": 'st_luma_eip_64x64:\nquant parameter，HEVC :step luma inter in P/B frame, 64x64(ony', "w": 6},
    ("VCPI_FRO_ST_2", "ve_st_luma_eip_8x8"): {"r": 16, "d": 'st_luma_eip_8x8:\nquant parameter，HEVC :step luma inter in P/B frame, 8x8\nH264 :s', "w": 6},
    ("VCPI_FRO_ST_3", "ve_st_chma_iii_16x16"): {"r": 6, "d": 'st_chroma_iii_16x16:\nquant parameter，HEVC :step chroma intra in I frame, 16x16\nH', "w": 6},
    ("VCPI_FRO_ST_3", "ve_st_chma_iii_32x32"): {"r": 6, "d": 'st_chroma_iii_32x32:\nquant parameter，HEVC :step chroma intra in I frame, 32x32(u', "w": 6},
    ("VCPI_FRO_ST_3", "ve_st_chma_iii_4x4"): {"r": 24, "d": 'st_chroma_iii_4x4:\nquant parameter，HEVC :step chroma intra in I frame, 4x4\nH264 ', "w": 6},
    ("VCPI_FRO_ST_3", "ve_st_chma_iii_8x8"): {"r": 12, "d": 'st_chroma_iii_8x8:\nquant parameter，HEVC :step chroma intra in I frame, 8x8\nH264 ', "w": 6},
    ("VCPI_FRO_ST_4", "ve_st_chma_iip_16x16"): {"r": 8, "d": 'st_chroma_iip_16x16:\nquant parameter，HEVC :step chroma intra in P/B frame, 16x16', "w": 6},
    ("VCPI_FRO_ST_4", "ve_st_chma_iip_32x32"): {"r": 8, "d": 'st_chroma_iip_32x32:\nquant parameter，HEVC :step chroma intra in P/B frame, 32x32', "w": 6},
    ("VCPI_FRO_ST_4", "ve_st_chma_iip_4x4"): {"r": 32, "d": 'st_chroma_iip_4x4:\nquant parameter，HEVC :step chroma intra in P/B frame, 4x4\nH26', "w": 6},
    ("VCPI_FRO_ST_4", "ve_st_chma_iip_8x8"): {"r": 16, "d": 'st_chroma_iip_8x8:\nquant parameter，HEVC :step chroma intra in P/B frame, 8x8\nH26', "w": 6},
    ("VCPI_FRO_ST_5", "ve_st_chma_eip_16x16"): {"r": 8, "d": 'st_chroma_eip_16x16:\nquant parameter，HEVC :step chroma inter in P/B frame, 16x16', "w": 6},
    ("VCPI_FRO_ST_5", "ve_st_chma_eip_32x32"): {"r": 8, "d": 'st_chroma_eip_32x32:\nquant parameter，HEVC :step chroma inter in P/B frame, 32x32', "w": 6},
    ("VCPI_FRO_ST_5", "ve_st_chma_eip_4x4"): {"r": 32, "d": 'st_chroma_eip_4x4:\nquant parameter，HEVC :step chroma inter in P/B frame, 4x4\nH26', "w": 6},
    ("VCPI_FRO_ST_5", "ve_st_chma_eip_8x8"): {"r": 16, "d": 'st_chroma_eip_8x8:\nquant parameter，HEVC :step chroma inter in P/B frame, 8x8\nH26', "w": 6},
    ("VCPI_LAMBDA_SCALING", "ve_lambda_scale_inter"): {"d": 'lambda scale value for inter P/B frame', "w": 10},
    ("VCPI_LAMBDA_SCALING", "ve_lambda_scale_intra"): {"d": 'lambda scale value for i frame', "w": 10},
    ("VCPI_LAMBDA_SQRT_SCALING", "ve_lambda_sq_scale_inter"): {"c": ('range', 0, 127), "d": 'sqrt lambda scale value for inter P/B frame', "w": 10},
    ("VCPI_LAMBDA_SQRT_SCALING", "ve_lambda_sq_scale_intra"): {"d": 'sqrt lambda scale value for I frame', "w": 10},
    ("VCPI_MCTF_TF_THRESHOLD", "ve_diff_threshold"): {"r": 500, "d": 'directly determine weight if extreme diff, default value is 500', "w": 10},
    ("VCPI_MCTF_TF_THRESHOLD", "ve_error_threshold1"): {"r": 50, "d": 'distinguish error type, default value is 50', "w": 7},
    ("VCPI_MCTF_TF_THRESHOLD", "ve_error_threshold2"): {"r": 100, "d": 'distinguish error type, default value is 100', "w": 7},
    ("VCPI_MCTF_TF_THRESHOLD", "ve_noise_threshold"): {"r": 25, "d": 'distinguish noise type, default value is 25.   (6 bit-width)', "w": 6},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_chma_factor"): {"d": 'Adjust chroma filter weight, range= 0, 15', "w": 4},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_luma_factor"): {"d": 'Adjust luma filter weight, range= 0, 15', "w": 4},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_ww_int_weight0"): {"d": 'Adjust filter weight based on error type and noise type classification, range= 0', "w": 5},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_ww_int_weight1"): {"d": 'Adjust filter weight based on error type and noise type classification, range= 0', "w": 5},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_ww_int_weight2"): {"d": 'Adjust filter weight based on error type and noise type classification, range= 0', "w": 4},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_ww_int_weight3"): {"d": 'Adjust filter weight based on error type and noise type classification, range= 0', "w": 4},
    ("VCPI_MCTF_TF_WEIGHT1", "ve_ww_int_weight4"): {"d": 'Adjust filter weight based on error type and noise type classification, range= 0', "w": 4},
    ("VCPI_MCTF_TF_WEIGHT2", "ve_chroma_sigma_sq_factor"): {"d": 'Adjust filter weight based on chroma QP, but default to fixed value 73, range= 0', "w": 8},
    ("VCPI_MCTF_TF_WEIGHT2", "ve_luma_sigma_sq_factor"): {"d": 'Adjust filter weight based on luma QP, range= 0, 255', "w": 8},
    ("VCPI_MCTF_TF_WEIGHT2", "ve_ref0_strengths"): {"d": 'Adjust filter weight based on the POC distance between past reference picture an', "w": 7},
    ("VCPI_MCTF_TF_WEIGHT2", "ve_ref1_strengths"): {"d": 'Adjust filter weight based on the POC distance between future reference picture ', "w": 7},
    ("VCPI_ME_COST_PENALTY", "ve_accum16_inter_penalty"): {"c": ('range', 0, 31), "r": 0, "d": 'for inter16x16 cost judge penalty', "w": 5},
    ("VCPI_ME_COST_PENALTY", "ve_accum32_inter_penalty"): {"c": ('range', 0, 31), "r": 0, "d": 'for inter32x32 cost judge penalty', "w": 5},
    ("VCPI_ME_COST_PENALTY", "ve_accum8_inter_penalty"): {"c": ('range', 0, 31), "r": 0, "d": 'for inter8x8 cost judge penalty', "w": 5},
    ("VCPI_ME_COST_PENALTY", "ve_intra_penalty"): {"c": ('range', 0, 63), "r": 0, "d": 'intra cost judge penalty', "w": 6},
    ("VCPI_ME_CST0", "ve_skip0"): {"c": ('range', 0, 127), "r": 0, "d": 'SKIP0\nCABAC context for the skip flag in cases of no up/left neighbor is skipped', "w": 7},
    ("VCPI_ME_CST0", "ve_skip1"): {"c": ('range', 0, 127), "r": 0, "d": 'SKIP1\nCABAC context for the skip flag in cases of one up/left neighbor is skippe', "w": 7},
    ("VCPI_ME_CST0", "ve_skip2"): {"c": ('range', 0, 127), "r": 0, "d": 'SKIP2\nCABAC context for the skip flag in cases of two up/left neighbor are skipp', "w": 7},
    ("VCPI_ME_CST0", "ve_split0_intra16"): {"c": ('range', 0, 127), "r": 0, "d": 'SPLIT0:\nCABAC context for the split flag in cases of no up/left neighbor is spli', "w": 7},
    ("VCPI_ME_CST1", "ve_mrg_inter8"): {"c": ('range', 0, 127), "r": 0, "d": 'MRG:\nCABAC context for the merge flag\nINTER8:\nFractional bit cost for choosing a', "w": 7},
    ("VCPI_ME_CST1", "ve_pred_inter16"): {"c": ('range', 0, 127), "r": 0, "d": 'PRED:\nCABAC context for the pred mode flag with 0 being intra and 1 inter\nINTER1', "w": 7},
    ("VCPI_ME_CST1", "ve_split1_intra8"): {"c": ('range', 0, 127), "r": 0, "d": 'SPLIT1:\nC context for the split flag in cases of one up/left neighbor is splitte', "w": 7},
    ("VCPI_ME_CST1", "ve_split2_intra4"): {"c": ('range', 0, 127), "r": 0, "d": 'SPLIT2:\nCABAC context for the split flag in cases of two up/left neighbor are sp', "w": 7},
    ("VCPI_ME_CST2", "ve_bdirect8"): {"c": ('range', 0, 127), "r": 0, "d": 'BDIRECT8:\nFractional bit cost for choosing a B direct 8x8 macroblock.', "w": 7},
    ("VCPI_ME_CST2", "ve_bipred"): {"c": ('range', 0, 7), "r": 0, "d": 'BIPRED:\nBit cost for choosing a bipredicted (both L0 and L1) mode in the FME (on', "w": 3},
    ("VCPI_ME_CST2", "ve_mrg_idx_birect16"): {"c": ('range', 0, 127), "r": 0, "d": 'MRG_IDX:\nCABAC context for choosing the first merge mode, with 0 choosing the fi', "w": 7},
    ("VCPI_ME_CST2", "ve_unipred"): {"c": ('range', 0, 7), "r": 0, "d": 'UNIPRED:\nBit cost for choosing a unipredicted (only L0 or only L1) mode in the F', "w": 3},
    ("VCPI_ME_CU_EN", "ve_disable_bskip"): {"c": ('range', 0, 1), "r": 0, "d": 'BSKIP: Disable skip macroblocks for B-frame.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter16x16"): {"c": ('range', 0, 1), "r": 0, "d": 'P16x16: Disable inter 16x16 blocks', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter16x8"): {"c": ('range', 0, 1), "r": 0, "d": 'P16x8: Disable inter 16x8 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter32x32"): {"c": ('range', 0, 1), "r": 0, "d": 'P32x32: Disable inter 32x32 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter4x4"): {"c": ('range', 0, 1), "r": 0, "d": 'P4x4: Disable inter 4x4 blocks. NB. The ME cannot generate this block size even ', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter4x8"): {"c": ('range', 0, 1), "r": 0, "d": 'P4x8: Disable inter 4x8 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter64x64"): {"c": ('range', 0, 1), "r": 0, "d": 'P64x64: Disable inter 64x64 blocks', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter8x16"): {"c": ('range', 0, 1), "r": 0, "d": 'P8x16: Disable inter 8x16 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter8x4"): {"c": ('range', 0, 1), "r": 0, "d": 'P8x4: Disable inter 8x4 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_inter8x8"): {"c": ('range', 0, 1), "r": 0, "d": 'P8x8: Disable inter 8x8 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_intra16x16"): {"c": ('range', 0, 1), "r": 0, "d": 'I16x16: Disable intra 16x16 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_intra32x32"): {"c": ('range', 0, 1), "r": 0, "d": 'I32x32: Disable intra 32x32 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_intra4x4"): {"c": ('range', 0, 1), "r": 0, "d": 'I4x4: Disable intra 4x4 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_intra8x8"): {"c": ('range', 0, 1), "r": 0, "d": 'I8x8: Disable intra 8x8 blocks.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_pskip"): {"c": ('range', 0, 1), "r": 0, "d": 'PSKIP: Disable skip macroblocks for P-frame.', "w": 1},
    ("VCPI_ME_CU_EN", "ve_disable_tu8"): {"c": ('range', 0, 1), "r": 0, "d": 'T8x8: Disable tu size 8x8 block (only used for 264, H264-high 8x8 TU enable, H26', "w": 1},
    ("VCPI_ME_INFO0", "ve_breject_en"): {"c": ('range', 0, 1), "r": 0, "d": 'B-reject enabled', "w": 1},
    ("VCPI_ME_INFO0", "ve_dzc"): {"c": ('range', 0, 1), "r": 0, "d": 'DZC\nDisable zero coefficient cut thresholds', "w": 1},
    ("VCPI_ME_INFO0", "ve_ir"): {"c": ('range', 0, 1), "r": 0, "d": 'IR\nI-reject enabled', "w": 1},
    ("VCPI_ME_INFO0", "ve_mrg2_en"): {"c": ('range', 0, 1), "r": 0, "d": 'MRG2\nEnabling 2 merge modes, only works together with I-reject', "w": 1},
    ("VCPI_ME_INFO0", "ve_preject_en"): {"c": ('range', 0, 1), "r": 0, "d": 'P-reject enabled', "w": 1},
    ("VCPI_ME_INFO0", "ve_preject_threshold"): {"c": ('range', 0, 1), "r": 0, "d": 'P-reject threshold divided by 128', "w": 1},
    ("VCPI_ME_INFO0", "ve_rgmp"): {"c": ('range', 0, 15), "r": 0, "d": 'RGMP:\nPME grid minimum penalty divided by 1024', "w": 4},
    ("VCPI_ME_INFO0", "ve_rgp"): {"c": ('range', 0, 7), "r": 0, "d": 'RGP\nPME grid penalty divided by 8, multiplicative penalty (cost=(1+pen/8)*cost)', "w": 3},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_ir_th"): {"c": ('range', 0, 63), "r": 0, "d": 'ME_FRMCFG2_IR_TH', "w": 6},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_pr_th2"): {"c": ('range', 0, 31), "r": 0, "d": 'ME_FRMCFG2_PR_TH2', "w": 5},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_pr_thca"): {"c": ('range', 0, 7), "r": 0, "d": 'ME_FRMCFG2_PR_THCA', "w": 3},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_pr_thcb"): {"c": ('range', 0, 3), "r": 0, "d": 'ME_FRMCFG2_PR_THCB', "w": 2},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_pr_thcnt"): {"c": ('range', 0, 7), "r": 0, "d": 'ME_FRMCFG2_PR_THCNT', "w": 3},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_pr_thdx"): {"c": ('range', 0, 63), "r": 0, "d": 'ME_FRMCFG2_PR_THDX', "w": 6},
    ("VCPI_ME_INFO1", "ve_me_frmcfg2_pr_thdy"): {"c": ('range', 0, 15), "r": 0, "d": 'ME_FRMCFG2_PR_THDY', "w": 4},
    ("VCPI_ME_INFO2", "ve_pme_area_height"): {"c": ('range', 10, 14), "r": 112, "d": 'pme data window width,unit in 8pixel', "w": 4},
    ("VCPI_ME_INFO2", "ve_pme_area_width"): {"c": ('range', 10, 14), "r": 112, "d": 'pme data window width,unit in 8pixel', "w": 4},
    ("VCPI_ME_IPENALTY", "ve_accum16_penaty"): {"c": ('range', 0, 31), "r": 0, "d": '16ACCUM:\nPenalty applied to intra 16 accumulate', "w": 5},
    ("VCPI_ME_IPENALTY", "ve_accum8_penaty"): {"c": ('range', 0, 31), "r": 0, "d": '8ACCUM:\nPenalty applied to intra 8 accumulate', "w": 5},
    ("VCPI_ME_IPENALTY", "ve_angular_penaty"): {"c": ('range', 0, 31), "r": 0, "d": 'ANGULAR:\nPenalty applied to angular modes.', "w": 5},
    ("VCPI_ME_IPENALTY", "ve_dc_penaty"): {"c": ('range', 0, 31), "r": 0, "d": 'DC:\nPenalty applied to dc mode.', "w": 5},
    ("VCPI_ME_IPENALTY", "ve_full32_penaty"): {"c": ('range', 0, 31), "r": 0, "d": '32FULL:\nPenalty applied to intra 32', "w": 5},
    ("VCPI_ME_IPENALTY", "ve_planar_penaty"): {"c": ('range', 0, 31), "r": 0, "d": 'PLANAR:\nPenalty applied to planar mode.', "w": 5},
    ("VCPI_ME_MVLIMIT", "ve_pme_mvlimit_down"): {"c": ('range', 16, 64), "r": 64, "d": 'pme mv limit for down boundary,range 16~64', "w": 8},
    ("VCPI_ME_MVLIMIT", "ve_pme_mvlimit_left"): {"c": ('range', 16, 128), "r": 128, "d": 'pme mv limit for left boundary,range 16~128', "w": 8},
    ("VCPI_ME_MVLIMIT", "ve_pme_mvlimit_right"): {"c": ('range', 16, 128), "r": 128, "d": 'pme mv limit for right boundary,range 16~128', "w": 8},
    ("VCPI_ME_MVLIMIT", "ve_pme_mvlimit_up"): {"c": ('range', 16, 64), "r": 64, "d": 'pme mv limit for up boundary,range 16~64', "w": 8},
    ("VCPI_ME_TMVPENALTY", "ve_div8_penaty"): {"d": 'PENALTY_DIV8:\nPenalty\xa0divides\xa08', "w": 3},
    ("VCPI_ME_TMVPENALTY", "ve_min_penaty"): {"d": 'PENALTY_MIN:\nMinimum penalty', "w": 4},
    ("VCPI_ME_TMVPENALTY", "ve_reject_thx"): {"d": 'REJECT_THX: \nReject threshold in x direction', "w": 6},
    ("VCPI_ME_TMVPENALTY", "ve_reject_thy"): {"d": 'REJECT_THY: \nReject threshold in y direction', "w": 6},
    ("VCPI_ME_WIGHT", "ve_me_frmwgt0"): {"c": ('range', 0, 255), "d": 'ME_FRMWGT0\nbi-pred weight for h264, refidx0', "w": 8},
    ("VCPI_ME_WIGHT", "ve_me_frmwgt1"): {"c": ('range', 0, 255), "d": 'ME_FRMWGT1\nbi-pred weight for h264, refidx1', "w": 8},
    ("VCPI_ME_WIGHT", "ve_me_frmwgt2"): {"c": ('range', 0, 255), "d": 'ME_FRMWGT2', "w": 8},
    ("VCPI_ME_WIGHT", "ve_me_frmwgt3"): {"c": ('range', 0, 255), "d": 'ME_FRMWGT3', "w": 8},
    ("VCPI_ME_ZERO_CUT", "ve_zerocut_16"): {"c": ('range', 0, 15), "r": 0, "d": 'zero cut threshold for inter 16', "w": 4},
    ("VCPI_ME_ZERO_CUT", "ve_zerocut_32"): {"c": ('range', 0, 15), "r": 0, "d": 'zero cut threshold for inter 32', "w": 4},
    ("VCPI_ME_ZERO_CUT", "ve_zerocut_64"): {"c": ('range', 0, 31), "r": 0, "d": 'zero cut threshold for inter 64', "w": 5},
    ("VCPI_ME_ZERO_CUT", "ve_zerocut_8"): {"c": ('range', 0, 15), "r": 0, "d": 'zero cut threshold for inter 8', "w": 4},
    ("VCPI_MMU_CHN_BYPASS", "ve_bnd_bypass"): {"r": 0, "d": 'boundary load channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_bs_st_bypass"): {"r": 0, "d": 'Bitstream store channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_ds_ld_bypass"): {"r": 0, "d": 'ds load channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_pks_ld_bypass"): {"r": 0, "d": 'pks load channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_pks_st_bypass"): {"r": 0, "d": 'pks store channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_pme_st_bypass"): {"r": 0, "d": 'pme store channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_postsrc_ld_bypass"): {"r": 0, "d": 'post src load channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_presrc_ld_bypass"): {"r": 0, "d": 'pre src load channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_qpg_bypass"): {"r": 0, "d": 'Bitstream store channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_recst_bypass"): {"r": 0, "d": 'recst channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_refld_bypass"): {"r": 0, "d": 'ref load channel', "w": 1},
    ("VCPI_MMU_CHN_BYPASS", "ve_src_ld_bypass"): {"r": 0, "d": 'src load channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_bnd_priority"): {"r": 0, "d": 'boundary load channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_bs_st_priority"): {"r": 0, "d": 'Bitstream store channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_ds_ld_priority"): {"r": 0, "d": 'ds load channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_master11_priority"): {"r": 0, "d": 'pks load channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_pks_st_priority"): {"r": 0, "d": 'pks store channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_pme_st_priority"): {"r": 0, "d": 'pme store channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_postsrc_ld_priority"): {"r": 0, "d": 'post src load channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_presrc_ld_priority"): {"r": 0, "d": 'pre src load channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_qpg_priority"): {"r": 0, "d": 'Qpg channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_recst_priority"): {"r": 0, "d": 'recst channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_refld_priority"): {"r": 0, "d": 'ref channel', "w": 1},
    ("VCPI_MMU_CHN_PRIO", "ve_src_ld_priority"): {"r": 0, "d": 'src load channel', "w": 1},
    ("VCPI_MMU_EVTSEL0", "ve_master0_evtsel"): {"c": ('range', 0, 7), "r": 0, "d": 'ref load channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master1_evtsel"): {"c": ('range', 0, 7), "r": 0, "d": 'boundary load channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master2_evtsel"): {"r": 0, "d": 'boundary store channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master3_evtsel"): {"r": 0, "d": 'current src load channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master4_evtsel"): {"r": 0, "d": 'pre src load channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master5_evtsel"): {"r": 0, "d": 'post src load channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master6_evtsel"): {"r": 0, "d": 'downsample load channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master7_evtsel"): {"r": 0, "d": 'downsample store channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master8_evtsel"): {"r": 0, "d": 'pks store channel', "w": 3},
    ("VCPI_MMU_EVTSEL0", "ve_master9_evtsel"): {"r": 0, "d": 'recst channel', "w": 3},
    ("VCPI_MMU_EVTSEL1", "ve_master10_evtsel"): {"c": ('range', 0, 7), "r": 0, "d": 'Bitstream store channel', "w": 3},
    ("VCPI_MMU_EVTSEL1", "ve_master11_evtsel"): {"c": ('range', 0, 7), "r": 0, "d": 'pks load channel', "w": 3},
    ("VCPI_MVP_COLREF_POC", "ve_mvp_colref0_poc"): {"d": 'VCPI_MVP_COLREF0_POC', "w": 16},
    ("VCPI_MVP_COLREF_POC", "ve_mvp_colref1_poc"): {"d": 'VCPI_MVP_COLREF1_POC', "w": 16},
    ("VCPI_MVP_PIC_INFO", "ve_col_l0_longterm_flag"): {"d": 'The long term flag for collocated pic in L0 ref List', "w": 1},
    ("VCPI_MVP_PIC_INFO", "ve_col_l1_longterm_flag"): {"d": 'The long term flag for collocated pic in L1 ref List', "w": 1},
    ("VCPI_MVP_PIC_INFO", "ve_mvp_l0_longterm_flag"): {"d": 'The long term flag for current pic in L0 ref List', "w": 1},
    ("VCPI_MVP_PIC_INFO", "ve_mvp_l1_longterm_flag"): {"d": 'The long term flag for current pic in L1 ref List', "w": 1},
    ("VCPI_MVP_PIC_INFO", "ve_num_ref_idx_l0"): {"d": 'reference picture num in L1 List,minus1 config', "w": 2},
    ("VCPI_MVP_PIC_INFO", "ve_num_ref_idx_l1"): {"d": 'reference picture num in L0 List,minus1 config', "w": 2},
    ("VCPI_MVP_POC", "ve_mvp_col_poc"): {"d": 'VCPI_MVP_COL_POC', "w": 16},
    ("VCPI_MVP_POC", "ve_mvp_curr_poc"): {"d": 'VCPI_MVP_CURR_POC', "w": 16},
    ("VCPI_MVP_REF_POC", "ve_mvp_ref0_poc"): {"d": 'VCPI_MVP_REF0_POC', "w": 16},
    ("VCPI_MVP_REF_POC", "ve_mvp_ref1_poc"): {"d": 'VCPI_MVP_REF1_POC', "w": 16},
    ("VCPI_PIC_INFO0", "ve_chroma_format"): {"c": ('range', 0, 2), "r": 0, "d": 'Chroma_Format:\n0:400\n1:420\n2:422 \n3:444 \nIn Wudang,the YUV444 is not supported', "w": 2},
    ("VCPI_PIC_INFO0", "ve_collocated_l0_flag"): {"c": ('range', 0, 1), "r": 0, "d": 'Used in mvp for temporal prediction for select L0 or L1', "w": 1},
    ("VCPI_PIC_INFO0", "ve_constrain_intra"): {"c": ('range', 0, 1), "r": 0, "d": 'CI:Constrained Intra prediction enabled', "w": 1},
    ("VCPI_PIC_INFO0", "ve_dbl_bypass_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Deblock_Bypass\ndisable de-blocking filter', "w": 1},
    ("VCPI_PIC_INFO0", "ve_direct_8x8_inference_flag"): {"c": ('range', 0, 1), "r": 0, "d": 'Used in H264 direct 8x8', "w": 1},
    ("VCPI_PIC_INFO0", "ve_direct_spatial_mv_pred_flag"): {"c": ('range', 0, 1), "r": 0, "d": 'H264 spatial or temporal direct', "w": 1},
    ("VCPI_PIC_INFO0", "ve_enc_bitdepth"): {"c": ('range', 0, 1), "r": 0, "d": 'Enc BitDepth\n0:8bit 1:10bit', "w": 1},
    ("VCPI_PIC_INFO0", "ve_fbc_en"): {"c": ('range', 0, 1), "r": 1, "d": 'Reference Frame Buffer Compression\n1:enable 0:disable\nEffective only when ve_rec', "w": 1},
    ("VCPI_PIC_INFO0", "ve_frame_type"): {"c": ('range', 0, 3), "r": 0, "d": 'Frame Type\n0:I \n1:P \n2:B\n3:Noref B', "w": 2},
    ("VCPI_PIC_INFO0", "ve_log2parmrglevel"): {"c": ('fixed', 3), "r": 3, "d": 'The Pu parallel level used in mvp for mrg model candidate generation', "w": 3},
    ("VCPI_PIC_INFO0", "ve_nobackwardpredflag"): {"c": ('range', 0, 1), "r": 0, "d": 'Used in mvp for temporal prediction', "w": 1},
    ("VCPI_PIC_INFO0", "ve_protocol"): {"c": ('range', 0, 2), "r": 0, "d": 'Codec\n0:HEVC\n1:H264\n2:JPGE\n3:Reserved', "w": 2},
    ("VCPI_PIC_INFO0", "ve_recst_disable"): {"c": ('range', 0, 1), "r": 0, "d": 'Reference Frame Store\n1:disable 0:enable', "w": 1},
    ("VCPI_PIC_INFO0", "ve_recst_ringbuf_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Reference Frame Store - Ring Buffer Mode\n1:enable 0: disable\nThe ring buffer mod', "w": 1},
    ("VCPI_PIC_INFO0", "ve_sao_chma_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Sao_chroma_enable,Only used in HEVC', "w": 1},
    ("VCPI_PIC_INFO0", "ve_sao_luma_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Sao_luma_enable,Only used in HEVC', "w": 1},
    ("VCPI_PIC_INFO0", "ve_strong_intra_smooth_en"): {"c": ('range', 0, 1), "r": 0, "d": 'SI:Strong INTRA smoothing, HEVC strong_intra_smoothing_enable_flag', "w": 1},
    ("VCPI_PIC_INFO0", "ve_tmv_en"): {"c": ('range', 0, 1), "r": 0, "d": 'TMVP_EN\n1:Temporal motion vector enabled\n0: Temporal motion vector disabled', "w": 1},
    ("VCPI_PIC_SIZE", "ve_pic_height"): {"c": ('range', 63, 1920), "r": 127, "d": 'the picture height for enc view,it may be different from the src picture height\n', "w": 16, "a": {'hevc': 8, 'h264': 16, 'jpeg': 16}, "m": True},
    ("VCPI_PIC_SIZE", "ve_pic_width"): {"c": ('range', 63, 1080), "r": 127, "d": 'the picture width for enc view,it may be different from the src picture width\nHE', "w": 16, "a": {'hevc': 8, 'h264': 16, 'jpeg': 16}, "m": True},
    ("VCPI_PKS_BUF0_ADDR_HI", "ve_pks_buf0_addr_hi"): {"d": 'Higher 7bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 7},
    ("VCPI_PKS_BUF0_ADDR_LO", "ve_pks_buf0_addr_lo"): {"d": 'Lower 32bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 32},
    ("VCPI_PKS_BUF0_LEN", "ve_pks_buf0_len"): {"d": 'The byte length for PKS_BUF0,16byte align', "w": 32},
    ("VCPI_PKS_BUF1_ADDR_HI", "ve_pks_buf1_addr_hi"): {"d": 'Higher 7bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 7},
    ("VCPI_PKS_BUF1_ADDR_LO", "ve_pks_buf1_addr_lo"): {"d": 'Lower 32bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 32},
    ("VCPI_PKS_BUF1_LEN", "ve_pks_buf1_len"): {"d": 'The byte length for PKS_BUF1,16byte align', "w": 32},
    ("VCPI_PKS_BUF2_ADDR_HI", "ve_pks_buf2_addr_hi"): {"d": 'Higher 7bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 7},
    ("VCPI_PKS_BUF2_ADDR_LO", "ve_pks_buf2_addr_lo"): {"d": 'Lower 32bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 32},
    ("VCPI_PKS_BUF2_LEN", "ve_pks_buf2_len"): {"d": 'The byte length for PKS_BUF2,16byte align', "w": 32},
    ("VCPI_PKS_BUF3_ADDR_HI", "ve_pks_buf3_addr_hi"): {"d": 'Higher 7bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 7},
    ("VCPI_PKS_BUF3_ADDR_LO", "ve_pks_buf3_addr_lo"): {"d": 'Lower 32bit Address\nIntermediate base addr for pipe_core0 to store the pack comp', "w": 32},
    ("VCPI_PKS_BUF3_LEN", "ve_pks_buf3_len"): {"d": 'The byte length for PKS_BUF3,16byte align', "w": 32},
    ("VCPI_PMEST_BASE_HI", "ve_pmest_base_hi"): {"d": 'High 7bit Base address for pmest to store downsample data', "w": 7},
    ("VCPI_PMEST_BASE_LO", "ve_pmest_base_lo"): {"d": 'Lowe 32bit Base address for pmest to store downsample data,16bytes align', "w": 32},
    ("VCPI_PMEST_STRIDE", "ve_pmest_stride"): {"d": 'Distance between two quad rows for PMEST to store ds_data to external memory\n16b', "w": 32},
    ("VCPI_PPS_INFO0", "ve_beta_offset_div2"): {"c": ('range', 0, 6), "r": 0, "d": 'the deblocking parameter offsets for B (divided by 2)\nfor the current slice. in ', "w": 4},
    ("VCPI_PPS_INFO0", "ve_cabac_init_idc"): {"c": ('range', 0, 2), "r": 0, "d": 'Used for cabac context initialization\nRange 0~2', "w": 2},
    ("VCPI_PPS_INFO0", "ve_cb_qp_offset"): {"c": ('range', 0, 12), "r": 0, "d": 'In hevc ,this field meaning pps_cb_qp_offset,5bit is valid range\nIn h264, this f', "w": 6},
    ("VCPI_PPS_INFO0", "ve_chma_qp_adjustment_enabled_flag"): {"r": 0, "d": 'chma_qp_adjustment_enabled_flag,only used in HEVC', "w": 1},
    ("VCPI_PPS_INFO0", "ve_cr_qp_offset"): {"c": ('range', 0, 12), "r": 0, "d": 'In hevc ,this field meaning pps_cr_qp_offset,5bit is valid range\nIn h264, this f', "w": 6},
    ("VCPI_PPS_INFO0", "ve_entropy_sync_enable_flag"): {"r": 0, "d": 'entropy_coding_sync_enabled_flag,only used in HEVC', "w": 1},
    ("VCPI_PPS_INFO0", "ve_loop_filter_cross_slice_enable_flag"): {"r": 0, "d": 'enable flag for loop filter cross slice boundary,only for HEVC', "w": 1},
    ("VCPI_PPS_INFO0", "ve_loop_filter_cross_tile_enable_flag"): {"r": 0, "d": 'enable flag for loop filter cross tile boundary,only for HEVC', "w": 1},
    ("VCPI_PPS_INFO0", "ve_mvd_l1_zero_flag"): {"r": 0, "d": 'mvd_l1_zero_flag,only used in HEVC', "w": 1},
    ("VCPI_PPS_INFO0", "ve_pcm_loop_filter_disabled_flag"): {"r": 0, "d": 'pcm_loop_filter_disabled_flag,,only used in HEVC', "w": 1},
    ("VCPI_PPS_INFO0", "ve_tc_offset_div2"): {"c": ('range', 0, 6), "r": 0, "d": 'the deblocking parameter offsets for tC (divided by 2)\nfor the current slice. in', "w": 4},
    ("VCPI_PPS_INFO0", "ve_trans_8x8_mode_flag"): {"r": 1, "d": 'mean the 8x8 transform decoding process may be in use,only used in H.264', "w": 1},
    ("VCPI_PPS_INFO1", "ve_amp_enable_flag"): {"c": ('fixed', 0), "r": 0, "d": 'amp enable,only used in H.265', "w": 1},
    ("VCPI_PPS_INFO1", "ve_ctb_log2_size_y"): {"c": ('fixed', 6), "r": 6, "d": 'ctu size,range 4~6,In Wudang This value will be forcely 6', "w": 3},
    ("VCPI_PPS_INFO1", "ve_cu_qp_delta_enabled"): {"c": ('fixed', 1), "r": 1, "d": 'cu_qp_delta_enabled,only used in H.265', "w": 1},
    ("VCPI_PPS_INFO1", "ve_log2_max_trafo_size"): {"c": ('fixed', 5), "r": 5, "d": 'log2_max_trafo_size,only used in H.265', "w": 4},
    ("VCPI_PPS_INFO1", "ve_log2_min_cu_chroma_qp_adjust_size"): {"c": ('fixed', 3), "r": 3, "d": 'log2_min_cu_chroma_qp_adjust_size,only used in H.265', "w": 4},
    ("VCPI_PPS_INFO1", "ve_log2_min_cu_qp_delta_size"): {"c": ('fixed', 5), "r": 5, "d": 'log2_min_cu_qp_delta_size,only used in H.265', "w": 4},
    ("VCPI_PPS_INFO1", "ve_log2_min_trafo_size"): {"c": ('fixed', 2), "r": 2, "d": 'log2_min_trafo_size,only used in H.265', "w": 4},
    ("VCPI_PPS_INFO1", "ve_max_num_merge_cand"): {"c": ('fixed', 5), "r": 5, "d": 'max_num_merge_cand,only used in H.265', "w": 3},
    ("VCPI_PPS_INFO1", "ve_max_transform_depth_inter"): {"c": ('fixed', 1), "r": 1, "d": 'max_transform_depth_inter,only used in H.265', "w": 2},
    ("VCPI_PPS_INFO1", "ve_max_transform_depth_intra"): {"c": ('fixed', 0), "r": 0, "d": 'max_transform_depth_intra,only used in H.265', "w": 2},
    ("VCPI_PPS_INFO1", "ve_sign_data_hiding_enabled"): {"c": ('range', 0, 1), "r": 0, "d": 'sign_data_hiding_enabled,only used in H.265', "w": 1},
    ("VCPI_PPS_INFO1", "ve_transform_skip_enabled"): {"c": ('range', 0, 1), "r": 0, "d": 'transform_skip_enabled,only used in H.265', "w": 1},
    ("VCPI_PPS_INFO1", "ve_transquant_bypass_enabled"): {"c": ('range', 0, 1), "r": 0, "d": 'transquant_bypass_enabled,only used in H.265', "w": 1},
    ("VCPI_QPG_AQ_GDR_PARA", "ve_aq_qp_max"): {"c": ('range', 0, 51), "d": 'aq_qp_max', "w": 6},
    ("VCPI_QPG_AQ_GDR_PARA", "ve_aq_qp_min"): {"c": ('range', 0, 51), "d": 'aq_qp_min', "w": 6},
    ("VCPI_QPG_AQ_GDR_PARA", "ve_gdr_number"): {"d": '0 is disable,the max range is frame_height_align64/64', "w": 8},
    ("VCPI_QPG_AQ_GDR_PARA", "ve_gdr_pos"): {"d": 'the stripe pos for gdr start refresh', "w": 8},
    ("VCPI_QPG_AVG_INFO0", "ve_qpg_avg_mv0"): {"d": 'quad average mv0', "w": 9},
    ("VCPI_QPG_AVG_INFO0", "ve_qpg_avg_mv1"): {"d": 'quad average mv1', "w": 9},
    ("VCPI_QPG_AVG_INFO0", "ve_qpg_avg_svar"): {"d": 'quad average svar', "w": 8},
    ("VCPI_QPG_AVG_INFO1", "ve_qpg_avg_ssd0"): {"d": 'quad average ssd0', "w": 20},
    ("VCPI_QPG_AVG_INFO2", "ve_qpg_avg_ssd1"): {"d": 'quad average ssd1', "w": 20},
    ("VCPI_QPG_AVG_INFO3", "ve_qpg_avg_bim_err"): {"d": 'quad average bim err', "w": 21},
    ("VCPI_QPG_CYCLIC_INFO", "ve_qpg_cyclic_internal"): {"d": 'the internal for CTU/MB to force intra', "w": 16},
    ("VCPI_QPG_CYCLIC_INFO", "ve_qpg_cyclic_pos"): {"d": 'the start pos for for intra in one frame', "w": 16},
    ("VCPI_QPG_INFO0", "ve_change_lambda_en"): {"d": 'change_lambda_en', "w": 1},
    ("VCPI_QPG_INFO0", "ve_change_qp_en"): {"d": 'change_qp_en', "w": 1},
    ("VCPI_QPG_INFO0", "ve_frame_level"): {"d": '0【I frame】\n1【P frame】\n2【refB frame】\n3【no-refB frame】', "w": 2},
    ("VCPI_QPG_INFO0", "ve_num_of_lcu_inreg_m1"): {"d": 'num_of_lcu_in_reg, max is stripe64 H.264 8192/16*4 -1 =2047', "w": 11},
    ("VCPI_QPG_INFO0", "ve_qpg_aq_en"): {"d": 'aq_en', "w": 1},
    ("VCPI_QPG_INFO0", "ve_qpg_bim_en"): {"d": 'bim_en', "w": 1},
    ("VCPI_QPG_INFO0", "ve_qpg_bimaq_en"): {"d": 'bimaq_en', "w": 1},
    ("VCPI_QPG_INFO0", "ve_rc_en"): {"d": '0: disable QPG_RC\n1: enable QPG_RC', "w": 1},
    ("VCPI_QPG_INFO0", "ve_rc_init"): {"c": ('range', 0, 1), "d": 'QPG RC param init, reset =1 when session changed, also can be enable when new fr', "w": 1},
    ("VCPI_QPG_INFO0", "ve_rc_max_dqp_range"): {"d": 'The range of change of REG compared to frame QP,0-31', "w": 5},
    ("VCPI_QPG_INFO0", "ve_rc_max_dqp_step"): {"d": 'Neighbored REG QPstep  0-31', "w": 5},
    ("VCPI_QPG_INFO0", "ve_rc_mode"): {"d": '0: LCU_LEVEL RC\n1: ROW_LEVEL RC', "w": 1},
    ("VCPI_QPG_INFO0", "ve_sep_mode_en"): {"d": 'separate mode enable', "w": 1},
    ("VCPI_QPG_INFO1", "ve_ba_method"): {"d": '0：same weight 【TODO】\n1：HM default\n2：optimized BA【TODO】\n3：Customer designated BA【', "w": 2},
    ("VCPI_QPG_INFO1", "ve_bitrate_window"): {"d": 'The number limit of the qpg-rc remaining REG', "w": 7},
    ("VCPI_QPG_INFO1", "ve_frm_qp"): {"d": 'frame-level qp', "w": 6},
    ("VCPI_QPG_INFO1", "ve_qp_max"): {"d": 'max frame-level qp', "w": 6},
    ("VCPI_QPG_INFO1", "ve_qp_min"): {"d": 'min frame-level qp', "w": 6},
    ("VCPI_QPG_INFO1", "ve_rc_force_bitrate_en"): {"d": 'RC force accurate bitrate flag', "w": 1},
    ("VCPI_QPG_LAMBDA_0", "ve_sel_lambda0"): {"d": 'lambda select for QP== 0', "w": 16},
    ("VCPI_QPG_LAMBDA_0", "ve_sqrt_lambda0"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 0', "w": 8},
    ("VCPI_QPG_LAMBDA_1", "ve_sel_lambda1"): {"d": 'lambda select for QP==1', "w": 16},
    ("VCPI_QPG_LAMBDA_1", "ve_sqrt_lambda1"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 1', "w": 8},
    ("VCPI_QPG_LAMBDA_10", "ve_sel_lambda10"): {"d": 'lambda select for QP==10', "w": 16},
    ("VCPI_QPG_LAMBDA_10", "ve_sqrt_lambda10"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 10', "w": 8},
    ("VCPI_QPG_LAMBDA_11", "ve_sel_lambda11"): {"d": 'lambda select for QP==11', "w": 16},
    ("VCPI_QPG_LAMBDA_11", "ve_sqrt_lambda11"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 11', "w": 8},
    ("VCPI_QPG_LAMBDA_12", "ve_sel_lambda12"): {"d": 'lambda select for QP==12', "w": 16},
    ("VCPI_QPG_LAMBDA_12", "ve_sqrt_lambda12"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 12', "w": 8},
    ("VCPI_QPG_LAMBDA_13", "ve_sel_lambda13"): {"d": 'lambda select for QP==13', "w": 16},
    ("VCPI_QPG_LAMBDA_13", "ve_sqrt_lambda13"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 13', "w": 8},
    ("VCPI_QPG_LAMBDA_14", "ve_sel_lambda14"): {"d": 'lambda select for QP==14', "w": 16},
    ("VCPI_QPG_LAMBDA_14", "ve_sqrt_lambda14"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 14', "w": 8},
    ("VCPI_QPG_LAMBDA_15", "ve_sel_lambda15"): {"d": 'lambda select for QP==15', "w": 16},
    ("VCPI_QPG_LAMBDA_15", "ve_sqrt_lambda15"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 15', "w": 8},
    ("VCPI_QPG_LAMBDA_16", "ve_sel_lambda16"): {"d": 'lambda select for QP==16', "w": 16},
    ("VCPI_QPG_LAMBDA_16", "ve_sqrt_lambda16"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 16', "w": 8},
    ("VCPI_QPG_LAMBDA_17", "ve_sel_lambda17"): {"d": 'lambda select for QP==17', "w": 16},
    ("VCPI_QPG_LAMBDA_17", "ve_sqrt_lambda17"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 17', "w": 8},
    ("VCPI_QPG_LAMBDA_18", "ve_sel_lambda18"): {"d": 'lambda select for QP==18', "w": 16},
    ("VCPI_QPG_LAMBDA_18", "ve_sqrt_lambda18"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 18', "w": 8},
    ("VCPI_QPG_LAMBDA_19", "ve_sel_lambda19"): {"d": 'lambda select for QP==19', "w": 16},
    ("VCPI_QPG_LAMBDA_19", "ve_sqrt_lambda19"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 19', "w": 8},
    ("VCPI_QPG_LAMBDA_2", "ve_sel_lambda2"): {"d": 'lambda select for QP==2', "w": 16},
    ("VCPI_QPG_LAMBDA_2", "ve_sqrt_lambda2"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 2', "w": 8},
    ("VCPI_QPG_LAMBDA_20", "ve_sel_lambda20"): {"d": 'lambda select for QP==20', "w": 16},
    ("VCPI_QPG_LAMBDA_20", "ve_sqrt_lambda20"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 20', "w": 8},
    ("VCPI_QPG_LAMBDA_21", "ve_sel_lambda21"): {"d": 'lambda select for QP==21', "w": 16},
    ("VCPI_QPG_LAMBDA_21", "ve_sqrt_lambda21"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 21', "w": 8},
    ("VCPI_QPG_LAMBDA_22", "ve_sel_lambda22"): {"d": 'lambda select for QP==22', "w": 16},
    ("VCPI_QPG_LAMBDA_22", "ve_sqrt_lambda22"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 22', "w": 8},
    ("VCPI_QPG_LAMBDA_23", "ve_sel_lambda23"): {"d": 'lambda select for QP==23', "w": 16},
    ("VCPI_QPG_LAMBDA_23", "ve_sqrt_lambda23"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 23', "w": 8},
    ("VCPI_QPG_LAMBDA_24", "ve_sel_lambda24"): {"d": 'lambda select for QP==24', "w": 16},
    ("VCPI_QPG_LAMBDA_24", "ve_sqrt_lambda24"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 24', "w": 8},
    ("VCPI_QPG_LAMBDA_25", "ve_sel_lambda25"): {"d": 'lambda select for QP==25', "w": 16},
    ("VCPI_QPG_LAMBDA_25", "ve_sqrt_lambda25"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 25', "w": 8},
    ("VCPI_QPG_LAMBDA_26", "ve_sel_lambda26"): {"d": 'lambda select for QP==26', "w": 16},
    ("VCPI_QPG_LAMBDA_26", "ve_sqrt_lambda26"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 26', "w": 8},
    ("VCPI_QPG_LAMBDA_27", "ve_sel_lambda27"): {"d": 'lambda select for QP==27', "w": 16},
    ("VCPI_QPG_LAMBDA_27", "ve_sqrt_lambda27"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 27', "w": 8},
    ("VCPI_QPG_LAMBDA_28", "ve_sel_lambda28"): {"d": 'lambda select for QP==28', "w": 16},
    ("VCPI_QPG_LAMBDA_28", "ve_sqrt_lambda28"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 28', "w": 8},
    ("VCPI_QPG_LAMBDA_29", "ve_sel_lambda29"): {"d": 'lambda select for QP==29', "w": 16},
    ("VCPI_QPG_LAMBDA_29", "ve_sqrt_lambda29"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 29', "w": 8},
    ("VCPI_QPG_LAMBDA_3", "ve_sel_lambda3"): {"d": 'lambda select for QP==3', "w": 16},
    ("VCPI_QPG_LAMBDA_3", "ve_sqrt_lambda3"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 3', "w": 8},
    ("VCPI_QPG_LAMBDA_30", "ve_sel_lambda30"): {"d": 'lambda select for QP==30', "w": 16},
    ("VCPI_QPG_LAMBDA_30", "ve_sqrt_lambda30"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 30', "w": 8},
    ("VCPI_QPG_LAMBDA_31", "ve_sel_lambda31"): {"d": 'lambda select for QP==31', "w": 16},
    ("VCPI_QPG_LAMBDA_31", "ve_sqrt_lambda31"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 31', "w": 8},
    ("VCPI_QPG_LAMBDA_32", "ve_sel_lambda32"): {"d": 'lambda select for QP==32', "w": 16},
    ("VCPI_QPG_LAMBDA_32", "ve_sqrt_lambda32"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 32', "w": 8},
    ("VCPI_QPG_LAMBDA_33", "ve_sel_lambda33"): {"d": 'lambda select for QP==33', "w": 16},
    ("VCPI_QPG_LAMBDA_33", "ve_sqrt_lambda33"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 33', "w": 8},
    ("VCPI_QPG_LAMBDA_34", "ve_sel_lambda34"): {"d": 'lambda select for QP==34', "w": 16},
    ("VCPI_QPG_LAMBDA_34", "ve_sqrt_lambda34"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 34', "w": 8},
    ("VCPI_QPG_LAMBDA_35", "ve_sel_lambda35"): {"d": 'lambda select for QP==35', "w": 16},
    ("VCPI_QPG_LAMBDA_35", "ve_sqrt_lambda35"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 35', "w": 8},
    ("VCPI_QPG_LAMBDA_36", "ve_sel_lambda36"): {"d": 'lambda select for QP==36', "w": 16},
    ("VCPI_QPG_LAMBDA_36", "ve_sqrt_lambda36"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 36', "w": 8},
    ("VCPI_QPG_LAMBDA_37", "ve_sel_lambda37"): {"d": 'lambda select for QP==37', "w": 16},
    ("VCPI_QPG_LAMBDA_37", "ve_sqrt_lambda37"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 37', "w": 8},
    ("VCPI_QPG_LAMBDA_38", "ve_sel_lambda38"): {"d": 'lambda select for QP==38', "w": 16},
    ("VCPI_QPG_LAMBDA_38", "ve_sqrt_lambda38"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 38', "w": 8},
    ("VCPI_QPG_LAMBDA_39", "ve_sel_lambda39"): {"d": 'lambda select for QP==39', "w": 16},
    ("VCPI_QPG_LAMBDA_39", "ve_sqrt_lambda39"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 39', "w": 8},
    ("VCPI_QPG_LAMBDA_4", "ve_sel_lambda4"): {"d": 'lambda select for QP==4', "w": 16},
    ("VCPI_QPG_LAMBDA_4", "ve_sqrt_lambda4"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 4', "w": 8},
    ("VCPI_QPG_LAMBDA_40", "ve_sel_lambda40"): {"d": 'lambda select for QP==40', "w": 16},
    ("VCPI_QPG_LAMBDA_40", "ve_sqrt_lambda40"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 40', "w": 8},
    ("VCPI_QPG_LAMBDA_41", "ve_sel_lambda41"): {"d": 'lambda select for QP==41', "w": 16},
    ("VCPI_QPG_LAMBDA_41", "ve_sqrt_lambda41"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 41', "w": 8},
    ("VCPI_QPG_LAMBDA_42", "ve_sel_lambda42"): {"d": 'lambda select for QP==42', "w": 16},
    ("VCPI_QPG_LAMBDA_42", "ve_sqrt_lambda42"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 42', "w": 8},
    ("VCPI_QPG_LAMBDA_43", "ve_sel_lambda43"): {"d": 'lambda select for QP==43', "w": 16},
    ("VCPI_QPG_LAMBDA_43", "ve_sqrt_lambda43"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 43', "w": 8},
    ("VCPI_QPG_LAMBDA_44", "ve_sel_lambda44"): {"d": 'lambda select for QP==44', "w": 16},
    ("VCPI_QPG_LAMBDA_44", "ve_sqrt_lambda44"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 44', "w": 8},
    ("VCPI_QPG_LAMBDA_45", "ve_sel_lambda45"): {"d": 'lambda select for QP==45', "w": 16},
    ("VCPI_QPG_LAMBDA_45", "ve_sqrt_lambda45"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 45', "w": 8},
    ("VCPI_QPG_LAMBDA_46", "ve_sel_lambda46"): {"d": 'lambda select for QP==46', "w": 16},
    ("VCPI_QPG_LAMBDA_46", "ve_sqrt_lambda46"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 46', "w": 8},
    ("VCPI_QPG_LAMBDA_47", "ve_sel_lambda47"): {"d": 'lambda select for QP==47', "w": 16},
    ("VCPI_QPG_LAMBDA_47", "ve_sqrt_lambda47"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 47', "w": 8},
    ("VCPI_QPG_LAMBDA_48", "ve_sel_lambda48"): {"d": 'lambda select for QP==48', "w": 16},
    ("VCPI_QPG_LAMBDA_48", "ve_sqrt_lambda48"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 48', "w": 8},
    ("VCPI_QPG_LAMBDA_49", "ve_sel_lambda49"): {"d": 'lambda select for QP==49', "w": 16},
    ("VCPI_QPG_LAMBDA_49", "ve_sqrt_lambda49"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 49', "w": 8},
    ("VCPI_QPG_LAMBDA_5", "ve_sel_lambda5"): {"d": 'lambda select for QP==5', "w": 16},
    ("VCPI_QPG_LAMBDA_5", "ve_sqrt_lambda5"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 5', "w": 8},
    ("VCPI_QPG_LAMBDA_50", "ve_sel_lambda50"): {"d": 'lambda select for QP==50', "w": 16},
    ("VCPI_QPG_LAMBDA_50", "ve_sqrt_lambda50"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 50', "w": 8},
    ("VCPI_QPG_LAMBDA_51", "ve_sel_lambda51"): {"d": 'lambda select for QP==51', "w": 16},
    ("VCPI_QPG_LAMBDA_51", "ve_sqrt_lambda51"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 51', "w": 8},
    ("VCPI_QPG_LAMBDA_6", "ve_sel_lambda6"): {"d": 'lambda select for QP==6', "w": 16},
    ("VCPI_QPG_LAMBDA_6", "ve_sqrt_lambda6"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 6', "w": 8},
    ("VCPI_QPG_LAMBDA_7", "ve_sel_lambda7"): {"d": 'lambda select for QP==7', "w": 16},
    ("VCPI_QPG_LAMBDA_7", "ve_sqrt_lambda7"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 7', "w": 8},
    ("VCPI_QPG_LAMBDA_8", "ve_sel_lambda8"): {"d": 'lambda select for QP==8', "w": 16},
    ("VCPI_QPG_LAMBDA_8", "ve_sqrt_lambda8"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 8', "w": 8},
    ("VCPI_QPG_LAMBDA_9", "ve_sel_lambda9"): {"d": 'lambda select for QP==9', "w": 16},
    ("VCPI_QPG_LAMBDA_9", "ve_sqrt_lambda9"): {"c": ('range', 0, 255), "d": 'sqrt lambda select for QP== 9', "w": 8},
    ("VCPI_QPG_LOAD_ADDR_HI", "ve_qpg_load_addr_hi"): {"d": 'Higher 7bit Address for qpgld', "w": 7},
    ("VCPI_QPG_LOAD_ADDR_LO", "ve_qpg_load_addr_lo"): {"d": 'Lower 32bit Address for qpgld,16byte align', "w": 32},
    ("VCPI_QPG_MAX_FRAME_SIZE", "ve_qpg_max_frame_size"): {"d": 'if 0 is disable,else when the actual bits is exceed this value,the qp will be \ns', "w": 32},
    ("VCPI_QPG_NUM_REG", "ve_qpg_num_reg"): {"d": 'The number of REGs in the entire frame of QPG rc', "w": 16},
    ("VCPI_QPG_TT_BITWEIGHT", "ve_qpg_tt_bitweight"): {"d": 'the total sum for the bitweight in this frame', "w": 32},
    ("VCPI_RC_ALPHA", "ve_rc_alpha"): {"d": 'frame-level alpha, 32bit', "w": 32},
    ("VCPI_RC_ALPHA_MAX", "ve_rc_alpha_max"): {"d": 'frame-level alpha max, 32bit', "w": 32},
    ("VCPI_RC_ALPHA_MIN", "ve_rc_alpha_min"): {"d": 'frame-level alpha min, 32bit', "w": 32},
    ("VCPI_RC_BETA", "ve_rc_beta"): {"d": 'frame-level beta, 32bit', "w": 32},
    ("VCPI_RC_BETA_MAX", "ve_rc_beta_max"): {"d": 'frame-level beta max, 32bit', "w": 32},
    ("VCPI_RC_BETA_MIN", "ve_rc_beta_min"): {"d": 'frame-level beta min, 32bit', "w": 32},
    ("VCPI_RC_LAMBDA", "ve_rc_lambda"): {"d": 'frame-level lambda, 32bit', "w": 32},
    ("VCPI_RC_LAMBDA_MAX", "ve_rc_lambda_max"): {"d": 'frame-level lambda max, 32bit', "w": 32},
    ("VCPI_RC_LAMBDA_MIN", "ve_rc_lambda_min"): {"d": 'frame-level lambda min, 32bit', "w": 32},
    ("VCPI_RC_TARGET_BITS", "ve_rc_target_bits"): {"d": 'frame-level target bits', "w": 32},
    ("VCPI_READ_OSTD_NUM", "ve_bnd_rd_otsd"): {"r": 0, "d": 'BOUNDARY_LD,0~7', "w": 3},
    ("VCPI_READ_OSTD_NUM", "ve_ds_rd_otsd"): {"r": 0, "d": 'DS_LD,0~31', "w": 5},
    ("VCPI_READ_OSTD_NUM", "ve_mctf_rd_otsd"): {"r": 0, "d": 'MCTF_LD,0~63', "w": 6},
    ("VCPI_READ_OSTD_NUM", "ve_pks_rd_otsd"): {"r": 0, "d": 'MBINFO_LD ,0~15', "w": 4},
    ("VCPI_READ_OSTD_NUM", "ve_ref_rd_otsd"): {"r": 0, "d": 'REF_LD,0~63', "w": 6},
    ("VCPI_READ_OSTD_NUM", "ve_src_rd_otsd"): {"r": 0, "d": 'SRC_LD,0~63', "w": 6},
    ("VCPI_REF0_LUT_BASE_HI", "ve_ref0_lut_base_hi"): {"d": 'High 32bit for the reference L0 lut base addr', "w": 32},
    ("VCPI_REF0_LUT_BASE_LO", "ve_ref0_lut_base_lo"): {"d": 'Low 32bit for the reference L0 lut base addr，need to be aligned 128Bytes', "w": 32},
    ("VCPI_REF0_SLICE_BASE_HI", "ve_ref0_slice_base_hi"): {"d": 'High 32bit for the reference L0 slice base addr', "w": 32},
    ("VCPI_REF0_SLICE_BASE_LO", "ve_ref0_slice_base_lo"): {"d": 'Low 32bit for the reference L0 slice base addr，need to be aligned 256Bytes', "w": 32},
    ("VCPI_REF1_LUT_BASE_HI", "ve_ref1_lut_base_hi"): {"d": 'High 32bit for the reference L1 lut base addr', "w": 32},
    ("VCPI_REF1_LUT_BASE_LO", "ve_ref1_lut_base_lo"): {"d": 'Low 32bit for the reference L1 lut base addr，need to be aligned 128Bytes', "w": 32},
    ("VCPI_REF1_SLICE_BASE_HI", "ve_ref1_slice_base_hi"): {"d": 'High 32bit for the reference L1 slice base addr', "w": 32},
    ("VCPI_REF1_SLICE_BASE_LO", "ve_ref1_slice_base_lo"): {"d": 'Low 32bit for the reference L1 slice base addr，need to be aligned 256Bytes', "w": 32},
    ("VCPI_RGB2YUV_COEF0", "ve_rgb2yuv_coeff0_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF1", "ve_rgb2yuv_coeff1_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF2", "ve_rgb2yuv_coeff2_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF3", "ve_rgb2yuv_coeff3_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF4", "ve_rgb2yuv_coeff4_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF5", "ve_rgb2yuv_coeff5_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF6", "ve_rgb2yuv_coeff6_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF7", "ve_rgb2yuv_coeff7_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_COEF8", "ve_rgb2yuv_coeff8_matrix"): {"c": ('range', 0, 65535), "r": 0, "d": 'RGB2YUV_COEF: Rgb2yuv coef matrix', "w": 16},
    ("VCPI_RGB2YUV_RGB_VAL_RANGE", "ve_rgb_max"): {"d": 'RGB_MAX: Clip before rgb2yuv.', "w": 8},
    ("VCPI_RGB2YUV_RGB_VAL_RANGE", "ve_rgb_min"): {"d": 'RGB_MIN: Clip before rgb2yuv.', "w": 8},
    ("VCPI_RGB2YUV_YUV_VAL_RANGE", "ve_chma_max"): {"d": 'CHMA_MAX:Clip after rgb2yuv.', "w": 8},
    ("VCPI_RGB2YUV_YUV_VAL_RANGE", "ve_chma_min"): {"d": 'CHMA_MIN:Clip after rgb2yuv.', "w": 8},
    ("VCPI_RGB2YUV_YUV_VAL_RANGE", "ve_luma_max"): {"d": 'LUMA_MAX:Clip after rgb2yuv.', "w": 8},
    ("VCPI_RGB2YUV_YUV_VAL_RANGE", "ve_luma_min"): {"d": 'LUMA_MIN:Clip after rgb2yuv.', "w": 8},
    ("VCPI_ROI_ENABLE", "ve_roi_en"): {"c": ('range', 0, 65535), "r": 0, "d": 'Roi Enable,16个ROI区域使能信号', "w": 16},
    ("VCPI_ROI_POS_0", "ve_roi_0_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_0_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_0", "ve_roi_0_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_0_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_1", "ve_roi_1_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_1_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_1", "ve_roi_1_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_1_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_10", "ve_roi_10_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_10_START_X,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_10", "ve_roi_10_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_10_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_11", "ve_roi_11_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_11_START_X,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_11", "ve_roi_11_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_11_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_12", "ve_roi_12_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_12_START_X,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_12", "ve_roi_12_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_12_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_13", "ve_roi_13_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_13_START_X,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_13", "ve_roi_13_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_13_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_14", "ve_roi_14_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_14_START_X,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_14", "ve_roi_14_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_14_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_15", "ve_roi_15_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_15_START_X,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_15", "ve_roi_15_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_15_START_Y,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_2", "ve_roi_2_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_2_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_2", "ve_roi_2_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_2_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_3", "ve_roi_3_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_3_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_3", "ve_roi_3_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_3_START_Y,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_4", "ve_roi_4_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_4_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_4", "ve_roi_4_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_4_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_5", "ve_roi_5_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_5_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_5", "ve_roi_5_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_5_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_6", "ve_roi_6_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_6_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_6", "ve_roi_6_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_6_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_7", "ve_roi_7_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_7_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_POS_7", "ve_roi_7_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_7_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_8", "ve_roi_8_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_8_START_X,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_8", "ve_roi_8_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_8_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_9", "ve_roi_9_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'ROI_9_START_X,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_POS_9", "ve_roi_9_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'ROI_9_START_Y,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_0", "ve_roi_0_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_0_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_0", "ve_roi_0_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_0_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_1", "ve_roi_1_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_1_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_1", "ve_roi_1_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_1_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_10", "ve_roi_10_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_10_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_10", "ve_roi_10_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_10_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_11", "ve_roi_11_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_11_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_11", "ve_roi_11_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_11_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_12", "ve_roi_12_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_12_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_12", "ve_roi_12_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_12_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_13", "ve_roi_13_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_13_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_13", "ve_roi_13_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_13_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_14", "ve_roi_14_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_14_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_14", "ve_roi_14_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_14_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_15", "ve_roi_15_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_15_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_15", "ve_roi_15_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_15_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_2", "ve_roi_2_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_2_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_2", "ve_roi_2_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_2_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_3", "ve_roi_3_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_3_HEIGHT,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_3", "ve_roi_3_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_3_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_4", "ve_roi_4_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_4_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_4", "ve_roi_4_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_4_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_5", "ve_roi_5_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_5_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_5", "ve_roi_5_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_5_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_6", "ve_roi_6_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_6_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_6", "ve_roi_6_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_6_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_7", "ve_roi_7_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_7_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_7", "ve_roi_7_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_7_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_8", "ve_roi_8_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_8_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_8", "ve_roi_8_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_8_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_SIZE_9", "ve_roi_9_height"): {"c": ('range', 2, 8192), "r": 16, "d": 'ROI_9_HEIGHT,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_ROI_SIZE_9", "ve_roi_9_width"): {"c": ('range', 4, 8192), "r": 16, "d": 'ROI_9_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_ROI_VALUE_0", "vcpi_roi_0_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_0", "vcpi_roi_0_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_0", "vcpi_roi_0_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_0", "vcpi_roi_0_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_0", "vcpi_roi_0_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_1", "vcpi_roi_1_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_1", "vcpi_roi_1_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_1", "vcpi_roi_1_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_1", "vcpi_roi_1_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_1", "vcpi_roi_1_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_10", "vcpi_roi_10_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_10", "vcpi_roi_10_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_10", "vcpi_roi_10_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_10", "vcpi_roi_10_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_10", "vcpi_roi_10_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_11", "vcpi_roi_11_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_11", "vcpi_roi_11_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_11", "vcpi_roi_11_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_11", "vcpi_roi_11_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_11", "vcpi_roi_11_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_12", "vcpi_roi_12_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_12", "vcpi_roi_12_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_12", "vcpi_roi_12_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_12", "vcpi_roi_12_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_12", "vcpi_roi_12_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_13", "vcpi_roi_13_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_13", "vcpi_roi_13_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_13", "vcpi_roi_13_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_13", "vcpi_roi_13_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_13", "vcpi_roi_13_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_14", "vcpi_roi_14_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_14", "vcpi_roi_14_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_14", "vcpi_roi_14_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_14", "vcpi_roi_14_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_14", "vcpi_roi_14_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_15", "vcpi_roi_15_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_15", "vcpi_roi_15_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_15", "vcpi_roi_15_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_15", "vcpi_roi_15_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_15", "vcpi_roi_15_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_2", "vcpi_roi_2_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_2", "vcpi_roi_2_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_2", "vcpi_roi_2_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_2", "vcpi_roi_2_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_2", "vcpi_roi_2_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_3", "vcpi_roi_3_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_3", "vcpi_roi_3_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_3", "vcpi_roi_3_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_3", "vcpi_roi_3_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_3", "vcpi_roi_3_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_4", "vcpi_roi_4_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_4", "vcpi_roi_4_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_4", "vcpi_roi_4_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_4", "vcpi_roi_4_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_4", "vcpi_roi_4_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_5", "vcpi_roi_5_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_5", "vcpi_roi_5_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_5", "vcpi_roi_5_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_5", "vcpi_roi_5_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_5", "vcpi_roi_5_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_6", "vcpi_roi_6_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_6", "vcpi_roi_6_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_6", "vcpi_roi_6_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_6", "vcpi_roi_6_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_6", "vcpi_roi_6_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_7", "vcpi_roi_7_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_7", "vcpi_roi_7_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_7", "vcpi_roi_7_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_7", "vcpi_roi_7_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_7", "vcpi_roi_7_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_8", "vcpi_roi_8_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_8", "vcpi_roi_8_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_8", "vcpi_roi_8_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_8", "vcpi_roi_8_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_8", "vcpi_roi_8_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_ROI_VALUE_9", "vcpi_roi_9_DQP"): {"c": ('range', 0, 51), "d": 'DeltaQP', "w": 8},
    ("VCPI_ROI_VALUE_9", "vcpi_roi_9_FI"): {"c": ('range', 0, 1), "d": 'Force intra', "w": 1},
    ("VCPI_ROI_VALUE_9", "vcpi_roi_9_FS"): {"c": ('range', 0, 1), "d": 'Force skip', "w": 1},
    ("VCPI_ROI_VALUE_9", "vcpi_roi_9_QPF"): {"c": ('range', 0, 51), "d": 'QP 0-51', "w": 7},
    ("VCPI_ROI_VALUE_9", "vcpi_roi_9_priority"): {"c": ('range', 0, 15), "d": 'Priority 0-15', "w": 4},
    ("VCPI_SAO_LAMBDA_GROUP_0", "ve_sao_lambda0"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==0', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_0", "ve_sao_lambda1"): {"d": 'sao lambda for QP==1', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_1", "ve_sao_lambda2"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==2', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_1", "ve_sao_lambda3"): {"d": 'sao lambda for QP==3', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_10", "ve_sao_lambda20"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==20', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_10", "ve_sao_lambda21"): {"d": 'sao lambda for QP==21', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_11", "ve_sao_lambda22"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==22', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_11", "ve_sao_lambda23"): {"d": 'sao lambda for QP==23', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_12", "ve_sao_lambda24"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==24', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_12", "ve_sao_lambda25"): {"d": 'sao lambda for QP==25', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_13", "ve_sao_lambda26"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==26', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_13", "ve_sao_lambda27"): {"d": 'sao lambda for QP==27', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_14", "ve_sao_lambda28"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==28', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_14", "ve_sao_lambda29"): {"d": 'sao lambda for QP==29', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_15", "ve_sao_lambda30"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==30', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_15", "ve_sao_lambda31"): {"d": 'sao lambda for QP==31', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_16", "ve_sao_lambda32"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==32', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_16", "ve_sao_lambda33"): {"d": 'sao lambda for QP==33', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_17", "ve_sao_lambda34"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==34', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_17", "ve_sao_lambda35"): {"d": 'sao lambda for QP==35', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_18", "ve_sao_lambda36"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==36', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_18", "ve_sao_lambda37"): {"d": 'sao lambda for QP==37', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_19", "ve_sao_lambda38"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==38', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_19", "ve_sao_lambda39"): {"d": 'sao lambda for QP==39', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_2", "ve_sao_lambda4"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==4', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_2", "ve_sao_lambda5"): {"d": 'sao lambda for QP==5', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_20", "ve_sao_lambda40"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==40', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_20", "ve_sao_lambda41"): {"d": 'sao lambda for QP==41', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_21", "ve_sao_lambda42"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==42', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_21", "ve_sao_lambda43"): {"d": 'sao lambda for QP==43', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_22", "ve_sao_lambda44"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==44', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_22", "ve_sao_lambda45"): {"d": 'sao lambda for QP==45', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_23", "ve_sao_lambda46"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==46', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_23", "ve_sao_lambda47"): {"d": 'sao lambda for QP==47', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_24", "ve_sao_lambda48"): {"c": ('range', 0, 1023), "d": 'sao lambda for QP==48', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_24", "ve_sao_lambda49"): {"d": 'sao lambda for QP==49', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_25", "ve_sao_lambda50"): {"c": ('range', 0, 1023), "d": 'sao lambda for QP==50', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_25", "ve_sao_lambda51"): {"d": 'sao lambda for QP==51', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_3", "ve_sao_lambda6"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==6', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_3", "ve_sao_lambda7"): {"d": 'sao lambda for QP==7', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_4", "ve_sao_lambda8"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==8', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_4", "ve_sao_lambda9"): {"d": 'sao lambda for QP==9', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_5", "ve_sao_lambda10"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==10', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_5", "ve_sao_lambda11"): {"d": 'sao lambda for QP==11', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_6", "ve_sao_lambda12"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==12', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_6", "ve_sao_lambda13"): {"d": 'sao lambda for QP==13', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_7", "ve_sao_lambda14"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==14', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_7", "ve_sao_lambda15"): {"d": 'sao lambda for QP==15', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_8", "ve_sao_lambda16"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==16', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_8", "ve_sao_lambda17"): {"d": 'sao lambda for QP==17', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_9", "ve_sao_lambda18"): {"c": ('range', 0, 16383), "d": 'sao lambda for QP==18', "w": 14},
    ("VCPI_SAO_LAMBDA_GROUP_9", "ve_sao_lambda19"): {"d": 'sao lambda for QP==19', "w": 14},
    ("VCPI_SLICE_SPLIT_CFG", "ve_slice_size"): {"c": ('range', 0, 127), "r": 0, "d": 'Stripe number allocation in a slice,used in HEVC and H.264', "w": 8},
    ("VCPI_SLICE_SPLIT_CFG", "ve_slice_split_en"): {"c": ('range', 0, 1), "r": 0, "d": 'Slice Split Enable ,used in HEVC and H.264', "w": 1},
    ("VCPI_SRC_AQ_PRE_FRM_AVG_SVAR", "ve_aq_avg_svar"): {"d": 'aq pre frame avg_svar （range 0~255）', "w": 8},
    ("VCPI_SRC_AQ_PRE_FRM_AVG_SVAR", "ve_aq_frm_svar_method"): {"d": 'aq frame svar method', "w": 1},
    ("VCPI_SRC_AQ_PRE_FRM_AVG_SVAR", "ve_aq_max_frm_error"): {"d": 'MAX_FRM_ERROR（range 0~31）  : aq max frame error = （1<<MAX_FRM_SSD）-1    控制ssd累加到', "w": 5},
    ("VCPI_SRC_AQ_PRE_FRM_AVG_SVAR", "ve_aq_max_frm_ssd"): {"d": 'MAX_FRM_SSD（range 0~31） :  aq max frame ssd = （1<<MAX_FRM_ERROR）-1    控制error累加到', "w": 5},
    ("VCPI_SRC_AQ_PRE_FRM_AVG_SVAR", "ve_aq_svar_method"): {"d": 'aq svar method (range 0~2)', "w": 2},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_aq_neg_ratio"): {"d": 'aq neg ratio （range 0~63）', "w": 6},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_aq_pos_ratio"): {"d": 'aq pos ratio （range 0~63）', "w": 6},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_aq_qpdelta_limit"): {"d": 'aq qpdelta limit （range 0~15）', "w": 4},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_aq_src"): {"d": 'aq src（range 0~63）', "w": 6},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_aq_weight"): {"d": 'aq weight （range 0~15)', "w": 4},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_bim_aq_neg_ratio"): {"r": 1, "d": 'bim aq neg ratio  控制bim aq减qp的力度，range 0~7', "w": 3},
    ("VCPI_SRC_AQ_STRIPE_QPDELTA_PARA", "ve_bim_aq_pos_ratio"): {"r": 1, "d": 'bim aq pos ratio  控制bim aq加qp的力度，range 0~7', "w": 3},
    ("VCPI_SRC_BIM_AQ_TH", "ve_bim_aq_th0"): {"d": 'bim aq th0\xa0（range 0~255）', "w": 8},
    ("VCPI_SRC_BIM_AQ_TH", "ve_bim_aq_th1"): {"d": 'bim aq th1\xa0（range 0~255）', "w": 8},
    ("VCPI_SRC_BIM_AQ_TH", "ve_bim_aq_th2"): {"d": 'bim aq th2\xa0（range 0~255）', "w": 8},
    ("VCPI_SRC_BIM_AQ_TH", "ve_bim_aq_th3"): {"d": 'bim aq th3\xa0（range 0~255）', "w": 8},
    ("VCPI_SRC_BIM_AQ_WEIGHT", "ve_bim_aq_sa_center"): {"r": 45, "d": 'bim aq sa center :  (range 0~255)', "w": 8},
    ("VCPI_SRC_BIM_AQ_WEIGHT", "ve_bim_aq_sa_coeff"): {"r": 3, "d": 'bim aq sa coeff :(range 0~15)', "w": 4},
    ("VCPI_SRC_BIM_AQ_WEIGHT", "ve_bim_aq_sa_weight"): {"r": 6, "d": 'bim aq sa weight :  (range 0~10)', "w": 4},
    ("VCPI_SRC_BIM_AQ_WEIGHT", "ve_bim_aq_tf_weight0"): {"r": 20, "d": 'bim aq tf weight0 :  controlling error calculation，range 0~255', "w": 8},
    ("VCPI_SRC_BIM_AQ_WEIGHT", "ve_bim_aq_tf_weight1"): {"r": 50, "d": 'bim aq tf weight1 : controlling error calculation，range 0~255', "w": 8},
    ("VCPI_SRC_CTRL_INFO", "ve_bim_aq_en"): {"r": 0, "d": 'BIM AQ ON/OFF \nif(yuv_is_422==1 || yuv_is_440==1 || mctf mode==0 || (ref0_valid=', "w": 1},
    ("VCPI_SRC_CTRL_INFO", "ve_bim_mode"): {"d": 'BIM MODE:\xa0 0: OFF. 1: MAX, 2:MIN, 3: ref0, 4: ref1\nif(yuv_is_422==1 || yuv_is_44', "w": 3},
    ("VCPI_SRC_CTRL_INFO", "ve_chroma_convert_en"): {"d": '422_TO_420\n0 = No chroma conversion.\n1= Enable chroma conversion from YUV422 to ', "w": 1},
    ("VCPI_SRC_CTRL_INFO", "ve_memc_tf_swtich"): {"d": '0: bypass mode, bypass MEMC & TF， only current is processed (current source stat', "w": 3},
    ("VCPI_SRC_CTRL_INFO", "ve_mvrot_memc"): {"d": 'zero MV ration for MEMC', "w": 3},
    ("VCPI_SRC_CTRL_INFO", "ve_pme_en"): {"r": 0, "d": 'PMV_EN\npme_mv\xa0 on/off\nif(mctf mode==0 || (ref0_valid==0 && ref1_valid==0))； pme_', "w": 1},
    ("VCPI_SRC_CTRL_INFO", "ve_ref0_valid"): {"r": 0, "d": 'REF0_V:Indicate that the reference source 0 is valid', "w": 1},
    ("VCPI_SRC_CTRL_INFO", "ve_ref1_valid"): {"r": 0, "d": 'REF1_V:Indicate that the reference source 1 is valid', "w": 1},
    ("VCPI_SRC_CTRL_INFO", "ve_src_aq_en"): {"d": 'AQ_EN\nAQ ON/OFF\nif(yuv_is_422==1 || yuv_is_440==1);AQ_EN=0', "w": 1},
    ("VCPI_SRC_CTRL_INFO", "ve_stripe_height"): {"d": 'Stripe_H\n0:stripe 32\n1:stripe 64\n2:stripe 128 \n3:reserved\nIn WuDang this value m', "w": 2},
    ("VCPI_SRC_CTRL_INFO", "ve_uv_pad"): {"d": 'UV Pad,For SRC process', "w": 1},
    ("VCPI_SRC_EXT_BASE_HI_0", "ve_src_ext_base_hi_0"): {"d": 'Higher 7bit Base address for the first plane(Y)', "w": 7},
    ("VCPI_SRC_EXT_BASE_HI_1", "ve_src_ext_base_hi_1"): {"d": 'Higher 7bit Base address for the second plane or the UV plane', "w": 7},
    ("VCPI_SRC_EXT_BASE_HI_2", "ve_src_ext_base_hi_2"): {"d": 'Higher 7bit Base address for the 3th plane (only used for 3-plane formats).', "w": 7},
    ("VCPI_SRC_EXT_BASE_LO_0", "ve_src_ext_base_lo_0"): {"d": 'Lower 32bit Base address for the first plane(Y)，为旋转之后的，编码图像的左上角的点；如果crop，则为corp+', "w": 32},
    ("VCPI_SRC_EXT_BASE_LO_1", "ve_src_ext_base_lo_1"): {"d": 'Lower 32bit Base address for the second plane or the UV plane为旋转之后的，编码图像的左上角的点，c', "w": 32},
    ("VCPI_SRC_EXT_BASE_LO_2", "ve_src_ext_base_lo_2"): {"d": 'Lower 32bit Base address for the 3th plane (only used for 3-plane formats).为旋转之后', "w": 32},
    ("VCPI_SRC_FORMAT", "ve_msb_aligned_flag"): {"d": 'Only used for 10bit format, 10 bit in 16 bit. 0-LSB aligned, 1-MSB aligned.', "w": 1},
    ("VCPI_SRC_FORMAT", "ve_src_format"): {"r": 2, "d": 'SRC input Data format:\n0 = Y_1P, luma only.\n1 = YUV420_3P. 3-plane YUV420.\n2 = Y', "w": 6},
    ("VCPI_SRC_MOSAIC_POS_0", "ve_mosaic_0_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_0_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_0", "ve_mosaic_0_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_0_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_1", "ve_mosaic_1_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_1_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_1", "ve_mosaic_1_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_1_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_10", "ve_mosaic_10_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_10_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_10", "ve_mosaic_10_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_10_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_11", "ve_mosaic_11_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_11_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_11", "ve_mosaic_11_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_11_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_12", "ve_mosaic_12_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_12_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_12", "ve_mosaic_12_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_12_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_13", "ve_mosaic_13_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_13_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_13", "ve_mosaic_13_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_13_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_14", "ve_mosaic_14_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_14_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_14", "ve_mosaic_14_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_14_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_15", "ve_mosaic_15_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_15_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_15", "ve_mosaic_15_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_15_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_2", "ve_mosaic_2_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_2_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_2", "ve_mosaic_2_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_2_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_3", "ve_mosaic_3_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_3_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_3", "ve_mosaic_3_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_3_START_Y,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_4", "ve_mosaic_4_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_4_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_4", "ve_mosaic_4_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_4_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_5", "ve_mosaic_5_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_5_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_5", "ve_mosaic_5_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_5_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_6", "ve_mosaic_6_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_6_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_6", "ve_mosaic_6_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_6_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_7", "ve_mosaic_7_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_7_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_7", "ve_mosaic_7_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_7_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_8", "ve_mosaic_8_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_8_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_8", "ve_mosaic_8_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_8_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_POS_9", "ve_mosaic_9_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'Mosaic_9_START_X,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_POS_9", "ve_mosaic_9_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'Mosaic_9_START_Y,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_0", "ve_mosaic_0_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_0_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_0", "ve_mosaic_0_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_0_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_1", "ve_mosaic_1_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_1_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_1", "ve_mosaic_1_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_1_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_10", "ve_mosaic_10_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_10_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_10", "ve_mosaic_10_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_10_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_11", "ve_mosaic_11_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_11_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_11", "ve_mosaic_11_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_11_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_12", "ve_mosaic_12_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_12_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_12", "ve_mosaic_12_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_12_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_13", "ve_mosaic_13_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_13_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_13", "ve_mosaic_13_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_13_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_14", "ve_mosaic_14_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_14_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_14", "ve_mosaic_14_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_14_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_15", "ve_mosaic_15_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_15_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_15", "ve_mosaic_15_width"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_15_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_2", "ve_mosaic_2_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_2_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_2", "ve_mosaic_2_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_2_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_3", "ve_mosaic_3_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_3_HEIGHT,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_3", "ve_mosaic_3_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_3_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_4", "ve_mosaic_4_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_4_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_4", "ve_mosaic_4_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_4_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_5", "ve_mosaic_5_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_5_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_5", "ve_mosaic_5_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_5_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_6", "ve_mosaic_6_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_6_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_6", "ve_mosaic_6_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_6_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_7", "ve_mosaic_7_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_7_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_7", "ve_mosaic_7_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_7_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_8", "ve_mosaic_8_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_8_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_8", "ve_mosaic_8_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_8_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_MOSAIC_SIZE_9", "ve_mosaic_9_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'Mosaic_9_HEIGHT,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_MOSAIC_SIZE_9", "ve_mosaic_9_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'Mosaic_9_WIDTH,4pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_OSD0_ADDR_BASE_HI", "ve_src_osd0_addr_hi"): {"d": 'osd 0 external memory base addr high 7bits', "w": 7},
    ("VCPI_SRC_OSD0_ADDR_BASE_LO", "ve_src_osd0_addr_lo"): {"d": 'osd 0 external memory base addr low 32bits,16byte align', "w": 32},
    ("VCPI_SRC_OSD1_ADDR_BASE_HI", "ve_src_osd1_addr_hi"): {"d": 'osd 1 external memory base addr high 7bits', "w": 7},
    ("VCPI_SRC_OSD1_ADDR_BASE_LO", "ve_src_osd1_addr_lo"): {"d": 'osd 1 external memory base addr low 32bits,16byte align', "w": 32},
    ("VCPI_SRC_OSD_0_COLOR_PARAM", "ve_osd_0_cvt_colol_th"): {"d": 'OSD_0_CVT_COLOR_TH', "w": 10},
    ("VCPI_SRC_OSD_0_COLOR_PARAM", "ve_osd_0_cvt_color_en"): {"d": 'OSD_0_CVT_COLOR_ENABLE', "w": 1},
    ("VCPI_SRC_OSD_0_COLOR_PARAM", "ve_osd_0_format"): {"d": 'OSD_0_FORMAT\n0:1555, 1: 4444, 2: 56', "w": 2},
    ("VCPI_SRC_OSD_0_COLOR_PARAM", "ve_osd_0_init_alpha"): {"d": 'OSD_0_INIT_ALPHA', "w": 5},
    ("VCPI_SRC_OSD_0_COLOR_PARAM", "ve_osd_0_init_alpha_en"): {"d": 'OSD_0_INIT_ALPHA_ENABLE', "w": 1},
    ("VCPI_SRC_OSD_0_COLOR_PARAM", "ve_osd_0_rgb2yuv_coeff_mode"): {"d": 'OSD_0_RGB2YUV_COEF_MODE\n0--601 limit, 1--601 full, 2--709 limit 3--709 full', "w": 2},
    ("VCPI_SRC_OSD_0_SIZE", "ve_osd_0_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'OSD_0_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_OSD_0_SIZE", "ve_osd_0_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'OSD_0_WIDTH,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_OSD_0_START_POS", "ve_osd_0_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'OSD_0_START_X,4 pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_OSD_0_START_POS", "ve_osd_0_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'OSD_0_START_Y,2 pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_OSD_1_COLOR_PARAM", "ve_osd_1_cvt_colol_th"): {"d": 'OSD_1_CVT_COLOR_TH', "w": 10},
    ("VCPI_SRC_OSD_1_COLOR_PARAM", "ve_osd_1_cvt_color_en"): {"d": 'OSD_1_CVT_COLOR_ENABLE', "w": 1},
    ("VCPI_SRC_OSD_1_COLOR_PARAM", "ve_osd_1_format"): {"d": 'OSD_1_FORMAT\n0:1555, 1: 4444, 2: 56', "w": 2},
    ("VCPI_SRC_OSD_1_COLOR_PARAM", "ve_osd_1_init_alpha"): {"d": 'OSD_1_INIT_ALPHA', "w": 5},
    ("VCPI_SRC_OSD_1_COLOR_PARAM", "ve_osd_1_init_alpha_en"): {"d": 'OSD_1_INIT_ALPHA_ENABLE', "w": 1},
    ("VCPI_SRC_OSD_1_COLOR_PARAM", "ve_osd_1_rgb2yuv_coeff_mode"): {"d": 'OSD_1_RGB2YUV_COEF_MODE\n0--601 limit, 1--601 full, 2--709 limit 3--709 full', "w": 2},
    ("VCPI_SRC_OSD_1_SIZE", "ve_osd_1_height"): {"c": ('range', 2, 8192), "r": 4, "d": 'OSD_1_HEIGHT,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_OSD_1_SIZE", "ve_osd_1_width"): {"c": ('range', 4, 8192), "r": 4, "d": 'OSD_1_WIDTH,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_OSD_1_START_POS", "ve_osd_1_st_x"): {"c": ('range', 0, 8188), "r": 0, "d": 'OSD_1_START_X,4 pixel align', "w": 16, "a": {'default': 4}},
    ("VCPI_SRC_OSD_1_START_POS", "ve_osd_1_st_y"): {"c": ('range', 0, 8190), "r": 0, "d": 'OSD_1_START_Y,2pixel align', "w": 16, "a": {'default': 2}},
    ("VCPI_SRC_OSD_MOSAIC_CTRL", "ve_mosaic_en"): {"r": 0, "d": 'MOSAIC Enable for 16 mosaic area', "w": 16},
    ("VCPI_SRC_OSD_MOSAIC_CTRL", "ve_osd_0_en"): {"r": 0, "d": 'OSD_0_Enable', "w": 1},
    ("VCPI_SRC_OSD_MOSAIC_CTRL", "ve_osd_1_en"): {"r": 0, "d": 'OSD_1_Enable', "w": 1},
    ("VCPI_SRC_OSD_STRIDE", "ve_src_osd0_stride"): {"d": 'osd 0 external memory stride,16byte', "w": 16},
    ("VCPI_SRC_OSD_STRIDE", "ve_src_osd1_stride"): {"d": 'osd 1 external memory stride,16byte', "w": 16},
    ("VCPI_SRC_PIC_SIZE", "ve_src_pic_height"): {"c": ('range', 64, 1920),"d": 'the src picture height need to be 2 pixel pixel align\nPicture pixel width,minus1', "w": 16, "m": True},
    ("VCPI_SRC_PIC_SIZE", "ve_src_pic_width"): {"c": ('range', 64, 1080),"d": 'the src picture width need to be 2 pixel pixel align\nPicture pixel width,minus1 ', "w": 16, "m": True},
    ("VCPI_SRC_POST_EXT_BASE_HI_0", "ve_src_post_ext_base_hi_0"): {"d": 'Higher 7bit Base address for the first plane(Y)', "w": 7},
    ("VCPI_SRC_POST_EXT_BASE_HI_1", "ve_src_post_ext_base_hi_1"): {"d": 'Higher 7bit Base address for the second plane or the UV plane', "w": 7},
    ("VCPI_SRC_POST_EXT_BASE_HI_2", "ve_src_post_ext_base_hi_2"): {"d": 'Higher 7bit Base address for the 3th plane (only used for 3-plane formats).', "w": 7},
    ("VCPI_SRC_POST_EXT_BASE_LO_0", "ve_src_post_ext_base_lo_0"): {"d": 'Lower 32bit Base address for the first plane(Y)', "w": 32},
    ("VCPI_SRC_POST_EXT_BASE_LO_1", "ve_src_post_ext_base_lo_1"): {"d": 'Lower 32bit Base address for the second plane or the UV plane', "w": 32},
    ("VCPI_SRC_POST_EXT_BASE_LO_2", "ve_src_post_ext_base_lo_2"): {"d": 'Lower 32bit Base address for the 3th plane (only used for 3-plane formats).', "w": 32},
    ("VCPI_SRC_POST_STRIDE_0", "ve_src_post_stride0"): {"d": 'Distance between two rows for the Y plane (if SRC, also refers to RGB plane).', "w": 32},
    ("VCPI_SRC_POST_STRIDE_1", "ve_src_post_stride1"): {"d": 'Distance between two rows for the U plane or the UV plane.', "w": 32},
    ("VCPI_SRC_POST_STRIDE_2", "ve_src_post_stride2"): {"d": 'Distance between two rows for the V plane (only used for 3-plane formats).', "w": 32},
    ("VCPI_SRC_PRE_EXT_BASE_HI_0", "ve_src_pre_ext_base_hi_0"): {"d": 'Higher 7bit Base address for the first plane(Y)', "w": 7},
    ("VCPI_SRC_PRE_EXT_BASE_HI_1", "ve_src_pre_ext_base_hi_1"): {"d": 'Higher 7bit Base address for the second plane or the UV plane', "w": 7},
    ("VCPI_SRC_PRE_EXT_BASE_HI_2", "ve_src_pre_ext_base_hi_2"): {"d": 'Higher 7bit Base address for the 3th plane (only used for 3-plane formats).', "w": 7},
    ("VCPI_SRC_PRE_EXT_BASE_LO_0", "ve_src_pre_ext_base_lo_0"): {"d": 'Lower 32bit Base address for the first plane(Y)，同src，为编码图像左上角', "w": 32},
    ("VCPI_SRC_PRE_EXT_BASE_LO_1", "ve_src_pre_ext_base_lo_1"): {"d": 'Lower 32bit Base address for the second plane or the UV plane，同src，为编码图像左上角', "w": 32},
    ("VCPI_SRC_PRE_EXT_BASE_LO_2", "ve_src_pre_ext_base_lo_2"): {"d": 'Lower 32bit Base address for the 3th plane (only used for 3-plane formats).同src，', "w": 32},
    ("VCPI_SRC_PRE_STRIDE_0", "ve_src_pre_stride0"): {"d": 'Distance between two rows for the Y plane (if SRC, also refers to RGB plane).', "w": 32},
    ("VCPI_SRC_PRE_STRIDE_1", "ve_src_pre_stride1"): {"d": 'Distance between two rows for the U plane or the UV plane.', "w": 32},
    ("VCPI_SRC_PRE_STRIDE_2", "ve_src_pre_stride2"): {"d": 'Distance between two rows for the V plane (only used for 3-plane formats).', "w": 32},
    ("VCPI_SRC_ROTATION", "ve_mirror_x_en"): {"r": 0, "d": 'Enable mirroring on X axis', "w": 1},
    ("VCPI_SRC_ROTATION", "ve_mirror_y_en"): {"r": 0, "d": 'Enable mirroring on Y axis', "w": 1},
    ("VCPI_SRC_ROTATION", "ve_rotation_degree"): {"r": 0, "d": 'ROTATION\nSRC counter clockwise rotation:\n0 = 0 degrees.\n1 = 90 degrees.\n2 = 180 ', "w": 2},
    ("VCPI_SRC_SA_TH", "ve_aq_svar_th0"): {"d": 'aq svar th0\xa0（range 0~15）', "w": 4},
    ("VCPI_SRC_SA_TH", "ve_aq_svar_th1"): {"d": 'aq svar th1\xa0（range 0~15）', "w": 4},
    ("VCPI_SRC_SA_TH", "ve_sa_mv_th0"): {"d": 'sa mv th0\xa0（range 0~31）', "w": 5},
    ("VCPI_SRC_SA_TH", "ve_sa_mv_th1"): {"d": 'sa mv th0\xa0（range 0~31）', "w": 5},
    ("VCPI_SRC_SA_TH", "ve_sa_ssd_th0"): {"d": 'sa ssd th0\xa0（range 0~127）', "w": 7},
    ("VCPI_SRC_SA_TH", "ve_sa_ssd_th1"): {"d": 'sa ssd th1\xa0（range 0~127）', "w": 7},
    ("VCPI_SRC_STRIDE_0", "ve_src_stride0"): {"d": 'Distance between two rows for the Y plane (if SRC, also refers to RGB plane).', "w": 32},
    ("VCPI_SRC_STRIDE_1", "ve_src_stride1"): {"d": 'Distance between two rows for the U plane or the UV plane.', "w": 32},
    ("VCPI_SRC_STRIDE_2", "ve_src_stride2"): {"d": 'Distance between two rows for the V plane (only used for 3-plane formats).', "w": 32},
    ("VCPI_SRC_UV_PAD_VALUE", "ve_user_chma_value"): {"d": 'User defined chroma value to pad or replace real chroma.', "w": 10},
    ("VCPI_TOTAL_COSTINTRA0", "ve_total_costintra0"): {"d": 'frame-level intracost sum,low 32bit', "w": 32},
    ("VCPI_TOTAL_COSTINTRA1", "ve_total_costintra1"): {"d": 'frame-levelintracost sum,high32bit', "w": 32},
    ("VCPI_TQ_QBIAS", "ve_tq_qbias"): {"d": 'Bias used in quantization；only used in jpge in calculate offset', "w": 7},
    ("VCPI_WRITE_OSTD_NUM", "ve_bnd_wr_otsd"): {"r": 0, "d": 'BOUNDARY_ST, 0~15', "w": 4},
    ("VCPI_WRITE_OSTD_NUM", "ve_ds_wr_otsd"): {"r": 0, "d": 'DS_ST,0~31', "w": 6},
    ("VCPI_WRITE_OSTD_NUM", "ve_pks_wr_otsd"): {"r": 0, "d": 'PKS_ST,0~15', "w": 4},
    ("VCPI_WRITE_OSTD_NUM", "ve_recst_wr_otsd"): {"r": 0, "d": 'AFBC_ST , 0~31', "w": 5},
    ("VCPI_WRITE_OSTD_NUM", "ve_vlcst_wr_otsd"): {"r": 0, "d": 'VLC_ST, 0~15', "w": 4},
    ("VE_TILE_INFO", "ve_num_tile_columns_minus1"): {"r": 0, "d": 'plus 1 specifies the ctu cols number in a tile of current picture. \nnum_tile_col', "w": 8, "m": True},
    ("VE_TILE_INFO", "ve_num_tile_rows_minus1"): {"r": 0, "d": 'plus 1 specifies the ctu rows number in a tile of current picture. \nnum_tile_row', "w": 8, "m": True},
    ("VE_TILE_INFO", "ve_tiled_en"): {"c": ('range', 0, 1), "r": 0, "d": 'tile enable flag,only used in HEVC', "w": 1},
}  # end VCPI_FIELD_CONSTRAINTS


@dataclass(frozen=True)
class BitFieldDef:
    register_name: str
    name: str
    width: int


@dataclass(frozen=True)
class RegisterSelection:
    name: str
    enabled: bool
    source_index: int
    # indices is only required when the member is a struct-array in t_reg_vcpi.
    # None means "not specified"; List[int] holds the validated, expanded indices.
    indices: Optional[List[int]] = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate cmd.cfg from register selection")
    parser.add_argument("--header", default="reg_data.h", help="Path to reg_data.h")
    parser.add_argument(
        "--select-json",
        default="register_selection.json",
        help="Path to register_selection.json",
    )
    parser.add_argument("--out", default="cmd.cfg", help="Output cfg file path")
    parser.add_argument("--seed", type=int, default=None, help="Optional RNG seed")
    parser.add_argument(
        "--dump-registers",
        action="store_true",
        help="Print parsed register and field catalog then exit",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


def create_rng(seed: Optional[int]) -> random.Random:
    """Create a deterministic RNG instance for reproducible runs."""
    return random.Random(seed)


def parse_struct_definitions(header_text: str) -> Dict[str, str]:
    """Return mapping of typedef name -> struct body text."""
    pattern = re.compile(
        r"typedef\s+struct\s+\w*\s*\{(?P<body>.*?)\}\s*(?P<name>\w+)\s*;",
        re.DOTALL,
    )
    result: Dict[str, str] = {}
    for match in pattern.finditer(header_text):
        result[match.group("name")] = match.group("body")
    return result


def parse_bitfields(struct_body: str, register_name: str) -> List[BitFieldDef]:
    fields: List[BitFieldDef] = []
    pattern = re.compile(r"REG32\s+(?P<name>\w+)\s*:\s*(?P<width>\d+)")
    for match in pattern.finditer(struct_body):
        field_name = match.group("name")
        if field_name.lower().startswith("rsvd"):
            continue
        fields.append(
            BitFieldDef(
                register_name=register_name,
                name=field_name,
                width=int(match.group("width")),
            )
        )
    return fields


def parse_vcpi_member_order(vcpi_struct_body: str) -> List[Tuple[str, str, int]]:
    """Return ordered tuples of (register_name, typedef_name, array_len) under t_reg_vcpi.

    array_len is 1 for non-array members, >1 for members declared as TYPE NAME[N].
    """
    members: List[Tuple[str, str, int]] = []
    line_pattern = re.compile(
        r"(?P<typedef>t_reg_\w+)\s+(?P<member>VCPI_[A-Z0-9_]+)(?:\s*\[(?P<alen>\d+)\])?\s*;"
    )
    for line in vcpi_struct_body.splitlines():
        match = line_pattern.search(line)
        if match:
            alen = int(match.group("alen")) if match.group("alen") else 1
            members.append((match.group("member"), match.group("typedef"), alen))
    return members


def build_register_catalog(
    header_text: str,
) -> Tuple[Dict[str, List[BitFieldDef]], Dict[str, int]]:
    """Parse t_reg_vcpi from header_text.

    Returns:
        catalog: mapping register_name -> List[BitFieldDef]
        array_lengths: mapping register_name -> array_len for array members (len > 1)
    """
    structs = parse_struct_definitions(header_text)
    if "typedef struct" in header_text and not structs:
        raise ValueError(
            f"{ERR_HEADER_STRUCT_NOT_FOUND}: no typedef struct block parsed from reg_data.h"
        )

    vcpi_body = structs.get("t_reg_vcpi")
    if not vcpi_body:
        raise ValueError(f"{ERR_HEADER_STRUCT_NOT_FOUND}: t_reg_vcpi not found in header")

    alias_pattern = re.compile(r"typedef\s+uint32_t\s+(?P<name>\w+)\s*;")
    scalar_aliases = {m.group("name") for m in alias_pattern.finditer(header_text)}

    catalog: Dict[str, List[BitFieldDef]] = {}
    array_lengths: Dict[str, int] = {}
    for register_name, typedef_name, alen in parse_vcpi_member_order(vcpi_body):
        if alen > 1:
            array_lengths[register_name] = alen
        body = structs.get(typedef_name)
        if not body:
            if typedef_name in scalar_aliases:
                # Scalar typedef registers are represented as empty bitfield lists.
                catalog[register_name] = []
            continue
        fields = parse_bitfields(body, register_name)
        catalog[register_name] = fields

    return catalog, array_lengths


def parse_selection_json(select_path: Path) -> List[RegisterSelection]:
    if not select_path.exists():
        raise FileNotFoundError(f"{ERR_SELECTION_FILE_MISSING}: {select_path}")

    try:
        data = json.loads(select_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{ERR_SELECTION_JSON_INVALID}: {exc.msg}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("registers"), list):
        raise ValueError(
            f"{ERR_SELECTION_SCHEMA_INVALID}: root must contain list field 'registers'"
        )

    selections: List[RegisterSelection] = []
    for index, item in enumerate(data["registers"]):
        if not isinstance(item, dict):
            raise ValueError(
                f"{ERR_SELECTION_SCHEMA_INVALID}: registers[{index}] must be object"
            )

        name = item.get("name")
        enabled = item.get("enabled")
        if not isinstance(name, str) or not isinstance(enabled, bool):
            raise ValueError(
                f"{ERR_SELECTION_SCHEMA_INVALID}: registers[{index}] requires name(str), enabled(bool)"
            )
        # Store raw indices value; expansion and range validation happens in
        # resolve_active_targets() where array_lengths is available.
        raw_indices = item.get("indices")  # may be None, "all", or list
        selections.append(
            RegisterSelection(
                name=name,
                enabled=enabled,
                source_index=index,
                indices=raw_indices,  # type: ignore[arg-type]
            )
        )

    return selections


_ARRAY_KEY_RE = re.compile(r"^(?P<base>\w+)\[(?P<idx>\d+)\]$")


def resolve_active_targets(
    selections: List[RegisterSelection],
    catalog: Dict[str, List[BitFieldDef]],
    array_lengths: Dict[str, int],
) -> List[str]:
    """Return ordered list of target keys to generate.

    Non-array members: plain register_name (e.g. 'VCPI_PIC_INFO0').
    Array members: expanded 'MEMBER[N]' keys for each enabled index
    (e.g. 'VCPI_QPG_LAMBDA[0]', 'VCPI_QPG_LAMBDA[1]').

    Validation (fast-fail):
    - Name must exist in catalog.
    - Array members MUST declare `indices`; missing indices raises ARRAY_MISSING_INDICES.
    - Index values must be in [0, array_len-1]; out-of-range raises ARRAY_INDEX_OUT_OF_RANGE.
    """
    # Preserve catalog insertion order for enabled members.
    enabled_set: Dict[str, RegisterSelection] = {}
    for sel in selections:
        if sel.name not in catalog:
            raise ValueError(
                f"{ERR_SELECTION_TARGET_NOT_FOUND}: {sel.name} at index {sel.source_index}"
            )
        if sel.enabled:
            enabled_set[sel.name] = sel

    targets: List[str] = []
    for register_name in catalog.keys():
        sel = enabled_set.get(register_name)
        if sel is None:
            continue
        if register_name in array_lengths:
            alen = array_lengths[register_name]
            raw = sel.indices
            if raw is None:
                # Array members MUST declare indices (FR-003b).
                raise ValueError(
                    f"{ERR_SELECTION_ARRAY_MISSING_INDICES}: '{register_name}' "
                    f"at index {sel.source_index} - array members must declare 'indices'"
                )
            if raw == "all" or raw == ["all"]:
                # Expand "all" to full range.
                indices_list = list(range(alen))
            elif isinstance(raw, list):
                indices_list = []
                for idx in raw:
                    if not isinstance(idx, int) or idx < 0 or idx >= alen:
                        raise ValueError(
                            f"{ERR_SELECTION_ARRAY_INDEX_OUT_OF_RANGE}: "
                            f"'{register_name}' index {idx} out of [0, {alen - 1}]"
                        )
                    indices_list.append(idx)
                # Sort for stable output ordering.
                indices_list = sorted(set(indices_list))
            else:
                raise ValueError(
                    f"{ERR_SELECTION_SCHEMA_INVALID}: '{register_name}' indices must be "
                    f"a list of ints or \"all\", got {type(raw).__name__}"
                )
            for idx in indices_list:
                targets.append(f"{register_name}[{idx}]")
        else:
            targets.append(register_name)

    if not targets:
        raise ValueError(ERR_SELECTION_EMPTY_ACTIVE_SET)
    return targets


def pick_aligned(rng: random.Random, min_value: int, max_value: int, align: int) -> int:
    if align <= 1:
        return rng.randint(min_value, max_value)

    start = min_value + ((align - (min_value % align)) % align)
    if start > max_value:
        raise ValueError("E_VALUE_RANGE_INVALID: no aligned value in range")
    count = ((max_value - start) // align) + 1
    return start + align * rng.randrange(count)


def generate_field_value(
    rng: random.Random,
    register_name: str,
    field_name: str,
    width: int,
) -> int:
    """Return a random value for the given field using VCPI_FIELD_CONSTRAINTS.

    Priority order (from vcpi.xlsx):
      1. "c" = ('fixed', v)       -> always return v (clamped to bit-width)
      2. "c" = ('range', lo, hi)  -> uniform random in [lo, hi] (clamped)
                                     with alignment if "a" present
      3. Only "r" present (reset) -> use reset value as baseline,
                                     random over full [0, 2^width-1] with alignment
      4. No entry                 -> uniform random over [0, 2^width-1]
    
    Alignment ("a" field):
      - If "a" is a dict with codec keys (hevc, h264, jpeg), use max alignment
        to satisfy all codecs (e.g., {'hevc': 8, 'h264': 16} -> align=16)
      - If "a" has 'default' key, use that value
      - Alignment is applied to range/reset-based randomization via pick_aligned()
    
    minus1 config ("m": True):
      - For fields using minus1 storage (actual_value = config_value + 1)
      - Alignment constraint applies to actual value, not config value
      - Generate aligned actual value in [min+1, max+1], then return actual-1
      - Example: ve_pic_width with 16-align and range [63,8191]
        -> generate actual in [64,8192] aligned to 16 (e.g., 2880)
        -> return config = 2879 (2879+1=2880, 2880%16=0)
    """
    max_from_width = (1 << width) - 1
    entry = VCPI_FIELD_CONSTRAINTS.get((register_name, field_name))

    # Determine alignment requirement (if any)
    alignment = 1
    is_minus1 = False
    if entry is not None:
        align_spec = entry.get("a")
        if align_spec:
            # Extract maximum alignment across all codec variants
            if "default" in align_spec:
                alignment = align_spec["default"]
            else:
                # Use max alignment to satisfy all codecs (HEVC, H.264, JPEG)
                alignment = max(align_spec.values())
        
        # Check for minus1 config flag
        is_minus1 = entry.get("m", False)

    if entry is not None:
        constraint = entry.get("c")
        if constraint is not None:
            kind = constraint[0]
            if kind == "fixed":
                # Fixed value: clamp to valid bit-width range
                fixed_val = min(max(constraint[1], 0), max_from_width)
                # For minus1 fields, fixed value is already the config value
                return fixed_val
            if kind == "range":
                lo = max(constraint[1], 0)
                hi = min(constraint[2], max_from_width)
                if lo > hi:
                    # Constraint range exceeds bit-width; fall back to full range
                    if is_minus1:
                        # Generate aligned actual value, then subtract 1
                        actual = pick_aligned(rng, 1, max_from_width + 1, alignment)
                        return actual - 1
                    return pick_aligned(rng, 0, max_from_width, alignment)
                
                # Apply alignment to the range constraint
                if is_minus1:
                    # For minus1: align applies to actual value (config+1)
                    # Generate actual in [lo+1, hi+1] with alignment
                    actual = pick_aligned(rng, lo + 1, hi + 1, alignment)
                    # Return config value (actual - 1)
                    return actual - 1
                else:
                    # Normal: align applies directly to config value
                    return pick_aligned(rng, lo, hi, alignment)
        
        # No "c" but entry exists -> reset-value baseline: random over full range
        # (reset value stored as "r" is informational; we still randomise fully)
        # Apply alignment if specified
        if is_minus1:
            # For minus1: generate aligned actual in [1, max+1], return actual-1
            actual = pick_aligned(rng, 1, max_from_width + 1, alignment)
            return actual - 1
        return pick_aligned(rng, 0, max_from_width, alignment)

    # No entry at all: full bit-width uniform random (no alignment)
    return rng.randint(0, max_from_width)


def generate_values(
    targets: Iterable[str],
    catalog: Dict[str, List[BitFieldDef]],
    seed: Optional[int],
) -> Tuple[Dict[str, List[Tuple[str, int]]], Dict[str, object]]:
    """Generate random values for all target keys.

    Targets may be plain names ('VCPI_PIC_INFO0') or array-indexed keys
    ('VCPI_QPG_LAMBDA[0]').  Array-indexed keys use the base member name
    for field and constraint lookup.
    """
    rng = create_rng(seed)

    generated: Dict[str, List[Tuple[str, int]]] = {}
    applied_rule_mode: Dict[str, str] = {}
    metadata: Dict[str, object] = {"seed": seed, "applied_rule_mode": applied_rule_mode}
    for target_key in targets:
        # Resolve base register name for catalog/constraint lookup.
        arr_match = _ARRAY_KEY_RE.match(target_key)
        register_name = arr_match.group("base") if arr_match else target_key

        fields = catalog.get(register_name)
        if fields is None:
            raise ValueError(f"{ERR_SELECTION_TARGET_NOT_FOUND}: register {register_name}")

        values: List[Tuple[str, int]] = []
        if not fields:
            # Scalar (uint32_t alias) member: generate as single 32-bit value.
            value = generate_field_value(rng, register_name, register_name.lower(), 32)
            values.append((register_name.lower(), value))
            applied_rule_mode[f"{target_key}.{register_name.lower()}"] = "FULL_RANDOM"
            generated[target_key] = values
            continue

        for field in fields:
            value = generate_field_value(rng, register_name, field.name, field.width)
            values.append((field.name, value))
            applied_rule_mode[f"{target_key}.{field.name}"] = "FULL_RANDOM"
        generated[target_key] = values

    return generated, metadata


def format_cfg(generated: Dict[str, List[Tuple[str, int]]]) -> str:
    """Format generated values as cmd.cfg text.

    - Section head: '#================ MEMBER_NAME ====================' or
      '#================ MEMBER_NAME[N] ===================='
    - Field lines: right-aligned field name (within section), colon separator.
      This matches the reg_data.h struct style for readability.
    - Python writes colon separator ('field : value') per spec contract v2.
    """
    lines: List[str] = []
    for section_name, fields in generated.items():
        tail = "===================="
        lines.append(f"#================ {section_name} {tail}")
        # Right-align field names to max width within this section.
        max_width = max((len(fn) for fn, _ in fields), default=0)
        for field_name, value in fields:
            lines.append(f"{field_name:>{max_width}} : {value}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False, dir=str(path.parent)
    ) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def dump_registers(catalog: Dict[str, List[BitFieldDef]]) -> None:
    for register_name, fields in catalog.items():
        print(register_name)
        if not fields:
            print("  - (scalar)")
            continue
        for field in fields:
            print(f"  - {field.name} ({field.width})")


def count_catalog(catalog: Dict[str, List[BitFieldDef]]) -> Tuple[int, int]:
    return len(catalog), sum(len(fields) for fields in catalog.values())


def main() -> int:
    args = parse_args()
    try:
        header_text = read_text(Path(args.header))
        catalog, array_lengths = build_register_catalog(header_text)
        register_count, field_count = count_catalog(catalog)

        if args.dump_registers:
            dump_registers(catalog)
            print(f"Parsed {register_count} registers, {field_count} bitfields")
            return 0

        selections = parse_selection_json(Path(args.select_json))
        targets = resolve_active_targets(selections, catalog, array_lengths)
        generated, metadata = generate_values(targets, catalog, args.seed)
        metadata["selected_registers"] = targets
        cfg_text = format_cfg(generated)
        write_atomic(Path(args.out), cfg_text)

        print(
            f"Parsed {register_count} registers, {field_count} bitfields; "
            f"Generated {args.out} for {len(generated)} register groups; "
            f"seed={metadata['seed']}"
        )
        return 0
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
