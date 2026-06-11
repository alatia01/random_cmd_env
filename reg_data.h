#ifndef __EMUL_INCLUDE__REG_DATA_H__
#define __EMUL_INCLUDE__REG_DATA_H__

#include <stdint.h>
#define REG_VERION 0x97e3c83


#define  REG32 uint32_t
typedef struct t_reg_glb_version
{
    REG32   revision : 12;//[11:0]
    REG32 product_id : 20;//[31:12]
}t_reg_glb_version;

typedef struct t_reg_glb_ncores
{
    REG32  pipe_core_num :  4;//[3:0]
    REG32 parse_core_num :  4;//[7:4]
    REG32          rsvd0 : 24;//[31:8]
}t_reg_glb_ncores;

typedef struct t_reg_glb_fs_status
{
    REG32        fs_slot_valid :  4;//[3:0]
    REG32     fs_slot_0_status :  4;//[7:4]
    REG32     fs_slot_1_status :  4;//[11:8]
    REG32     fs_slot_2_status :  4;//[15:12]
    REG32     fs_slot_3_status :  4;//[19:16]
    REG32 fs_scheduling_status :  4;//[23:20]
    REG32                rsvd0 :  8;//[31:24]
}t_reg_glb_fs_status;

typedef uint32_t t_reg_glb_mon_tot_cc_high;
typedef uint32_t t_reg_glb_mon_tot_cc_low;
typedef uint32_t t_reg_glb_rd_word;
typedef uint32_t t_reg_glb_wr_word;
typedef struct t_reg_glb_mon_rd_latency
{
    REG32 mon0_rd_latency : 16;//[15:0]
    REG32 mon1_rd_latency : 16;//[31:16]
}t_reg_glb_mon_rd_latency;

typedef struct t_reg_glb_mon_wr_latency
{
    REG32 mon0_wr_latency : 16;//[15:0]
    REG32 mon1_wr_latency : 16;//[31:16]
}t_reg_glb_mon_wr_latency;

typedef uint32_t t_reg_glb_mon_rd_cmd;
typedef uint32_t t_reg_glb_mon_rd_burst8;
typedef uint32_t t_reg_glb_mon_rd_burst16;
typedef uint32_t t_reg_glb_mon_wr_cmd;
typedef uint32_t t_reg_glb_mon_wr_burst8;
typedef uint32_t t_reg_glb_mon_wr_burst16;
typedef uint32_t t_reg_glb_mon_rd_ostd_low;
typedef uint32_t t_reg_glb_mon_rd_ostd_high;
typedef uint32_t t_reg_glb_mon_wr_ostd_low;
typedef uint32_t t_reg_glb_mon_wr_ostd_high;
typedef uint32_t t_reg_glb_mon_rd_otsd_full;
typedef uint32_t t_reg_glb_mon_wr_otsd_full;
typedef struct t_reg_glb_irqve
{
    REG32 irqve_fsid0 :  1;//[0:0]
    REG32 irqve_fsid1 :  1;//[1:1]
    REG32 irqve_fsid2 :  1;//[2:2]
    REG32 irqve_fsid3 :  1;//[3:3]
    REG32       rsvd0 : 28;//[31:4]
}t_reg_glb_irqve;

typedef struct t_reg_glb_clkforce
{
    REG32 clkforce_ppcore0 :  1;//[0:0]
    REG32 clkforce_ppcore1 :  1;//[1:1]
    REG32 clkforce_pscore0 :  1;//[2:2]
    REG32 clkforce_pscore1 :  1;//[3:3]
    REG32    clkforce_vmac :  1;//[4:4]
    REG32    clkforce_vcpi :  1;//[5:5]
    REG32  clkforce_ppctrl :  1;//[6:6]
    REG32  clkforce_psctrl :  1;//[7:7]
    REG32            rsvd0 : 24;//[31:8]
}t_reg_glb_clkforce;

typedef struct t_reg_glb_reset
{
    REG32 reset :  1;//[0:0]
    REG32 rsvd0 : 31;//[31:1]
}t_reg_glb_reset;

typedef struct t_reg_glb_self_reset_en
{
    REG32 self_reset_enable :  1;//[0:0]
    REG32             rsvd0 : 31;//[31:1]
}t_reg_glb_self_reset_en;

typedef struct t_reg_glb_nsaid
{
    REG32   nsaid_default :  4;//[3:0]
    REG32    nsaid_public :  4;//[7:4]
    REG32 nsaid_protected :  4;//[11:8]
    REG32  nsaid_framebuf :  4;//[15:12]
    REG32   nsaid_private :  4;//[19:16]
    REG32           rsvd0 : 12;//[31:20]
}t_reg_glb_nsaid;

typedef struct t_reg_glb_arbiter_weight
{
    REG32 master0_weight :  4;//[3:0]
    REG32 master1_weight :  4;//[7:4]
    REG32 master2_weight :  4;//[11:8]
    REG32 master3_weight :  4;//[15:12]
    REG32          rsvd0 : 16;//[31:16]
}t_reg_glb_arbiter_weight;

typedef struct t_reg_glb_terminator_ostd0
{
    REG32 m0_ar_ostd :  8;//[7:0]
    REG32 m0_aw_ostd :  8;//[15:8]
    REG32 m1_ar_ostd :  8;//[23:16]
    REG32 m1_aw_ostd :  8;//[31:24]
}t_reg_glb_terminator_ostd0;

typedef struct t_reg_glb_terminator_ostd1
{
    REG32 m2_ar_ostd :  8;//[7:0]
    REG32 m2_aw_ostd :  8;//[15:8]
    REG32 m3_ar_ostd :  8;//[23:16]
    REG32 m3_aw_ostd :  8;//[31:24]
}t_reg_glb_terminator_ostd1;

typedef struct t_reg_glb_axi_otsd
{
    REG32 port0_r_otsd :  8;//[7:0]
    REG32 port0_w_otsd :  8;//[15:8]
    REG32 port1_r_otsd :  8;//[23:16]
    REG32 port1_w_otsd :  8;//[31:24]
}t_reg_glb_axi_otsd;

typedef struct t_reg_glb_axi_qos
{
    REG32 axi_arqos :  4;//[3:0]
    REG32 axi_awqos :  4;//[7:4]
    REG32     rsvd0 : 24;//[31:8]
}t_reg_glb_axi_qos;

typedef struct t_reg_glb_axi_mon_ctrl
{
    REG32     mon_run :  1;//[0:0]
    REG32 cluster_sel :  1;//[1:1]
    REG32       rsvd0 : 30;//[31:2]
}t_reg_glb_axi_mon_ctrl;

typedef uint32_t t_reg_reserved;
typedef struct t_reg_glb
{
    t_reg_glb_version                   GLB_VERSION;
    t_reg_glb_ncores                     GLB_NCORES;
    t_reg_glb_fs_status               GLB_FS_STATUS;
    t_reg_glb_mon_tot_cc_high   GLB_MON_TOT_CC_HIGH;
    t_reg_glb_mon_tot_cc_low     GLB_MON_TOT_CC_LOW;
    t_reg_glb_rd_word                   GLB_RD_WORD;
    t_reg_glb_wr_word                   GLB_WR_WORD;
    t_reg_glb_mon_rd_latency     GLB_MON_RD_LATENCY;
    t_reg_glb_mon_wr_latency     GLB_MON_WR_LATENCY;
    t_reg_glb_mon_rd_cmd             GLB_MON_RD_CMD;
    t_reg_glb_mon_rd_burst8       GLB_MON_RD_BURST8;
    t_reg_glb_mon_rd_burst16     GLB_MON_RD_BURST16;
    t_reg_glb_mon_wr_cmd             GLB_MON_WR_CMD;
    t_reg_glb_mon_wr_burst8       GLB_MON_WR_BURST8;
    t_reg_glb_mon_wr_burst16     GLB_MON_WR_BURST16;
    t_reg_glb_mon_rd_ostd_low   GLB_MON_RD_OSTD_LOW;
    t_reg_glb_mon_rd_ostd_high GLB_MON_RD_OSTD_HIGH;
    t_reg_glb_mon_wr_ostd_low   GLB_MON_WR_OSTD_LOW;
    t_reg_glb_mon_wr_ostd_high GLB_MON_WR_OSTD_HIGH;
    t_reg_glb_mon_rd_otsd_full GLB_MON_RD_OTSD_FULL;
    t_reg_glb_mon_wr_otsd_full GLB_MON_WR_OTSD_FULL;
    t_reg_glb_irqve                       GLB_IRQVE;
    t_reg_glb_clkforce                 GLB_CLKFORCE;
    t_reg_glb_reset                       GLB_RESET;
    t_reg_glb_self_reset_en       GLB_SELF_RESET_EN;
    t_reg_glb_nsaid                       GLB_NSAID;
    t_reg_glb_arbiter_weight     GLB_ARBITER_WEIGHT;
    t_reg_glb_terminator_ostd0 GLB_TERMINATOR_OSTD0;
    t_reg_glb_terminator_ostd1 GLB_TERMINATOR_OSTD1;
    t_reg_glb_axi_otsd                 GLB_AXI_OTSD;
    t_reg_glb_axi_qos                   GLB_AXI_QOS;
    t_reg_glb_axi_mon_ctrl         GLB_AXI_MON_CTRL;
    t_reg_reserved                         RESERVED;
} t_reg_glb;
typedef struct t_reg_fs_mmu_ctrl
{
    REG32   ve_mmu_disable :  1;//[0:0]
    REG32 ve_mmu_base_attr :  2;//[2:1]
    REG32            rsvd0 : 29;//[31:3]
}t_reg_fs_mmu_ctrl;

typedef struct t_reg_fs_mmu_flush
{
    REG32 ve_mmu_flush :  1;//[0:0]
    REG32        rsvd0 : 31;//[31:1]
}t_reg_fs_mmu_flush;

typedef uint32_t t_reg_fs_mmu_tbase_lo;
typedef struct t_reg_fs_mmu_tbase_hi
{
    REG32 ve_mmu_tbase_hi : 20;//[19:0]
    REG32           rsvd0 : 12;//[31:20]
}t_reg_fs_mmu_tbase_hi;

typedef struct t_reg_fs_nport
{
    REG32 ve_nport :  1;//[0:0]
    REG32    rsvd0 : 31;//[31:1]
}t_reg_fs_nport;

typedef struct t_reg_fs_map
{
    REG32 ve_map :  1;//[0:0]
    REG32  rsvd0 : 31;//[31:1]
}t_reg_fs_map;

typedef struct t_reg_fs_submit
{
    REG32   ve_submit :  1;//[0:0]
    REG32 ve_priority :  2;//[2:1]
    REG32       rsvd0 : 29;//[31:3]
}t_reg_fs_submit;

typedef struct t_reg_fs_reset
{
    REG32 ve_reset :  1;//[0:0]
    REG32    rsvd0 : 31;//[31:1]
}t_reg_fs_reset;

typedef struct t_reg_fs_time_mon_en
{
    REG32     ve_timeout_en :  1;//[0:0]
    REG32  ve_pipe_timer_en :  1;//[1:1]
    REG32 ve_parse_timer_en :  1;//[2:2]
    REG32             rsvd0 : 29;//[31:3]
}t_reg_fs_time_mon_en;

typedef uint32_t t_reg_fs_timeout_thr;
typedef uint32_t t_reg_fs_pipe_perf_timer;
typedef uint32_t t_reg_fs_parse_perf_timer;
typedef struct t_reg_fs_debug_ctrl
{
    REG32      ve_dbg_core_id :  2;//[1:0]
    REG32   ve_debug_vctrl_en :  1;//[2:2]
    REG32  ve_debug_dsctrl_en :  1;//[3:3]
    REG32     ve_debug_l2c_en :  1;//[4:4]
    REG32 ve_debug_bndctrl_en :  1;//[5:5]
    REG32   ve_debug_curld_en :  1;//[6:6]
    REG32     ve_debug_pme_en :  1;//[7:7]
    REG32   ve_debug_pmest_en :  1;//[8:8]
    REG32  ve_debug_cpdmov_en :  1;//[9:9]
    REG32     ve_debug_ref_en :  1;//[10:10]
    REG32     ve_debug_ime_en :  1;//[11:11]
    REG32  ve_debug_pintra_en :  1;//[12:12]
    REG32     ve_debug_qpg_en :  1;//[13:13]
    REG32     ve_debug_fme_en :  1;//[14:14]
    REG32     ve_debug_pmf_en :  1;//[15:15]
    REG32     ve_debug_mvp_en :  1;//[16:16]
    REG32   ve_debug_tqitq_en :  1;//[17:17]
    REG32   ve_debug_intra_en :  1;//[18:18]
    REG32     ve_debug_sel_en :  1;//[19:19]
    REG32 ve_debug_optdmov_en :  1;//[20:20]
    REG32  ve_debug_saoenc_en :  1;//[21:21]
    REG32     ve_debug_dbk_en :  1;//[22:22]
    REG32    ve_debug_pack_en :  1;//[23:23]
    REG32   ve_debug_recst_en :  1;//[24:24]
    REG32  ve_debug_parser_en :  1;//[25:25]
    REG32               rsvd0 :  6;//[31:26]
}t_reg_fs_debug_ctrl;

typedef struct t_reg_fs_userinfo
{
    REG32 ve_userinfo :  4;//[3:0]
    REG32       rsvd0 : 28;//[31:4]
}t_reg_fs_userinfo;

typedef uint32_t t_reg_fs_streamid;
typedef struct t_reg_fs_mmu_phoffset
{
    REG32 ve_phoffset : 25;//[24:0]
    REG32       rsvd0 :  7;//[31:25]
}t_reg_fs_mmu_phoffset;

typedef uint32_t t_reg_fs_para_cfg_paddr_lo;
typedef uint32_t t_reg_fs_para_cfg_paddr_hi;
typedef uint32_t t_reg_fs_bitbuf_addr_lo;

typedef uint32_t t_reg_fs_bitbuf_addr_hi;

typedef struct t_reg_fs_bitbuf_len
{
    REG32     ve_bitbuf_len : 31;//[30:0]
    REG32 ve_bitbuf_trigger :  1;//[31:31]
}t_reg_fs_bitbuf_len;

typedef struct t_reg_fs_irq_mask
{
    REG32    ve_irqmask_ppengine :  1;//[0:0]
    REG32    ve_irqmask_psengine :  1;//[1:1]
    REG32     ve_irqmask_mmu_err :  1;//[2:2]
    REG32  ve_irqmask_slice_done :  1;//[3:3]
    REG32 ve_irqmask_stripe_done :  1;//[4:4]
    REG32 ve_irqmask_bitbuf_full :  1;//[5:5]
    REG32   ve_irqmask_vcpi_done :  1;//[6:6]
    REG32   ve_irqmask_fbc_error :  1;//[7:7]
    REG32   ve_irqmask_bus_error :  1;//[8:8]
    REG32     ve_irqmask_timeout :  1;//[9:9]
    REG32                  rsvd0 : 22;//[31:10]
}t_reg_fs_irq_mask;

typedef struct t_reg_fs_irq_enable
{
    REG32    ve_irq_enable_ppengine :  1;//[0:0]
    REG32    ve_irq_enable_psengine :  1;//[1:1]
    REG32      ve_irq_enable_mmuerr :  1;//[2:2]
    REG32  ve_irq_enable_slice_done :  1;//[3:3]
    REG32 ve_irq_enable_stripe_done :  1;//[4:4]
    REG32 ve_irq_enable_bitbuf_full :  1;//[5:5]
    REG32   ve_irq_enable_vcpi_done :  1;//[6:6]
    REG32   ve_irq_enable_fbc_error :  1;//[7:7]
    REG32   ve_irq_enable_bus_error :  1;//[8:8]
    REG32     ve_irq_enable_timeout :  1;//[9:9]
    REG32                     rsvd0 : 22;//[31:10]
}t_reg_fs_irq_enable;

typedef struct t_reg_fs_irq_out
{
    REG32    ve_irq_ppengine :  1;//[0:0]
    REG32    ve_irq_psengine :  1;//[1:1]
    REG32    ve_irq_mmu0_err :  1;//[2:2]
    REG32    ve_irq_mmu1_err :  1;//[3:3]
    REG32  ve_irq_slice_done :  1;//[4:4]
    REG32 ve_irq_stripe_done :  1;//[5:5]
    REG32 ve_irq_bitbuf_full :  1;//[6:6]
    REG32   ve_irq_vcpi_done :  1;//[7:7]
    REG32   ve_irq_fbc_error :  1;//[8:8]
    REG32   ve_irq_bus_error :  1;//[9:9]
    REG32     ve_irq_timeout :  1;//[10:10]
    REG32              rsvd0 : 21;//[31:11]
}t_reg_fs_irq_out;

typedef struct t_reg_fs_irq_ppe_info
{
    REG32 ve_irq_ppe_cnt :  3;//[2:0]
    REG32          rsvd0 : 29;//[31:3]
}t_reg_fs_irq_ppe_info;

typedef struct t_reg_fs_irq_ppe_mmu_info0
{
    REG32 ve_irq_ppe_mmu_type :  3;//[2:0]
    REG32  ve_irq_ppe_mmu_acc :  1;//[3:3]
    REG32  ve_irq_ppe_mmu_mid :  4;//[7:4]
    REG32               rsvd0 : 24;//[31:8]
}t_reg_fs_irq_ppe_mmu_info0;

typedef struct t_reg_fs_irq_ppe_mmu_info1
{
    REG32 ve_irq_ppe_mmu_addr : 27;//[26:0]
    REG32               rsvd0 :  5;//[31:27]
}t_reg_fs_irq_ppe_mmu_info1;

typedef struct t_reg_fs_irq_pse_mmu_info0
{
    REG32 ve_irq_pse_mmu_type :  3;//[2:0]
    REG32  ve_irq_pse_mmu_acc :  1;//[3:3]
    REG32  ve_irq_pse_mmu_mid :  4;//[7:4]
    REG32               rsvd0 : 24;//[31:8]
}t_reg_fs_irq_pse_mmu_info0;

typedef struct t_reg_fs_irq_pse_mmu_info1
{
    REG32 ve_irq_pse_mmu_addr : 27;//[26:0]
    REG32               rsvd0 :  5;//[31:27]
}t_reg_fs_irq_pse_mmu_info1;

typedef struct t_reg_fs_irq_pse_info
{
    REG32 ve_irq_pse_slice_len : 28;//[27:0]
    REG32      ve_irq_pse_fsid :  2;//[29:28]
    REG32      ve_irq_pse_type :  2;//[31:30]
}t_reg_fs_irq_pse_info;

typedef struct t_reg_fs_busattr0
{
    REG32  ve_arcache0 :  4;//[3:0]
    REG32  ve_awcache0 :  4;//[7:4]
    REG32 ve_ardomain0 :  4;//[11:8]
    REG32 ve_awdomain0 :  4;//[15:12]
    REG32        rsvd0 : 16;//[31:16]
}t_reg_fs_busattr0;

typedef struct t_reg_fs_busattr1
{
    REG32  ve_arcache1 :  4;//[3:0]
    REG32  ve_awcache1 :  4;//[7:4]
    REG32 ve_ardomain1 :  4;//[11:8]
    REG32 ve_awdomain1 :  4;//[15:12]
    REG32        rsvd0 : 16;//[31:16]
}t_reg_fs_busattr1;

typedef struct t_reg_fs_busattr2
{
    REG32  ve_arcache2 :  4;//[3:0]
    REG32  ve_awcache2 :  4;//[7:4]
    REG32 ve_ardomain2 :  4;//[11:8]
    REG32 ve_awdomain2 :  4;//[15:12]
    REG32        rsvd0 : 16;//[31:16]
}t_reg_fs_busattr2;

typedef struct t_reg_fs_busattr3
{
    REG32  ve_arcache3 :  4;//[3:0]
    REG32  ve_awcache3 :  4;//[7:4]
    REG32 ve_ardomain3 :  4;//[11:8]
    REG32 ve_awdomain3 :  4;//[15:12]
    REG32        rsvd0 : 16;//[31:16]
}t_reg_fs_busattr3;


typedef struct t_reg_fs
{
    t_reg_fs_mmu_ctrl                   FS_MMU_CTRL;
    t_reg_fs_mmu_flush                 FS_MMU_FLUSH;
    t_reg_fs_mmu_tbase_lo           FS_MMU_TBASE_LO;
    t_reg_fs_mmu_tbase_hi           FS_MMU_TBASE_HI;
    t_reg_fs_nport                         FS_NPORT;
    t_reg_fs_map                             FS_MAP;
    t_reg_fs_submit                       FS_SUBMIT;
    t_reg_fs_reset                         FS_RESET;
    t_reg_fs_time_mon_en             FS_TIME_MON_EN;
    t_reg_fs_timeout_thr             FS_TIMEOUT_THR;
    t_reg_fs_pipe_perf_timer     FS_PIPE_PERF_TIMER;
    t_reg_fs_parse_perf_timer   FS_PARSE_PERF_TIMER;
    t_reg_fs_debug_ctrl               FS_DEBUG_CTRL;
    t_reg_fs_userinfo                   FS_USERINFO;
    t_reg_fs_streamid                   FS_STREAMID;
    t_reg_fs_mmu_phoffset           FS_MMU_PHOFFSET;
    t_reg_fs_para_cfg_paddr_lo FS_PARA_CFG_PADDR_LO;
    t_reg_fs_para_cfg_paddr_hi FS_PARA_CFG_PADDR_HI;
    t_reg_fs_bitbuf_addr_lo       FS_BITBUF_ADDR_LO;
    t_reg_fs_bitbuf_addr_hi       FS_BITBUF_ADDR_HI;
    t_reg_fs_bitbuf_len               FS_BITBUF_LEN;
    t_reg_fs_irq_mask                   FS_IRQ_MASK;
    t_reg_fs_irq_enable               FS_IRQ_ENABLE;
    t_reg_fs_irq_out                     FS_IRQ_OUT;
    t_reg_fs_irq_ppe_info           FS_IRQ_PPE_INFO;
    t_reg_fs_irq_ppe_mmu_info0 FS_IRQ_PPE_MMU_INFO0;
    t_reg_fs_irq_ppe_mmu_info1 FS_IRQ_PPE_MMU_INFO1;
    t_reg_fs_irq_pse_mmu_info0 FS_IRQ_PSE_MMU_INFO0;
    t_reg_fs_irq_pse_mmu_info1 FS_IRQ_PSE_MMU_INFO1;
    t_reg_fs_irq_pse_info           FS_IRQ_PSE_INFO;
    t_reg_fs_busattr0                   FS_BUSATTR0;
    t_reg_fs_busattr1                   FS_BUSATTR1;
    t_reg_fs_busattr2                   FS_BUSATTR2;
    t_reg_fs_busattr3                   FS_BUSATTR3;
} t_reg_fs;
typedef struct t_reg_vcpi_pic_info0
{
    REG32                  ve_frame_type :  2;//[1:0]
    REG32                    ve_protocol :  2;//[3:2]
    REG32               ve_chroma_format :  2;//[5:4]
    REG32                ve_enc_bitdepth :  1;//[6:6]
    REG32                      ve_tmv_en :  1;//[7:7]
    REG32             ve_log2parmrglevel :  3;//[10:8]
    REG32          ve_nobackwardpredflag :  1;//[11:11]
    REG32          ve_collocated_l0_flag :  1;//[12:12]
    REG32 ve_direct_spatial_mv_pred_flag :  1;//[13:13]
    REG32   ve_direct_8x8_inference_flag :  1;//[14:14]
    REG32             ve_constrain_intra :  1;//[15:15]
    REG32      ve_strong_intra_smooth_en :  1;//[16:16]
    REG32               ve_dbl_bypass_en :  1;//[17:17]
    REG32                 ve_sao_luma_en :  1;//[18:18]
    REG32                 ve_sao_chma_en :  1;//[19:19]
    REG32                      ve_fbc_en :  1;//[20:20]
    REG32               ve_recst_disable :  1;//[21:21]
    REG32            ve_recst_ringbuf_en :  1;//[22:22]
    REG32                          rsvd0 :  9;//[31:23]
}t_reg_vcpi_pic_info0;

typedef struct t_reg_vcpi_pic_size
{
    REG32 ve_pic_height : 16;//[15:0]
    REG32  ve_pic_width : 16;//[31:16]
}t_reg_vcpi_pic_size;

typedef struct t_reg_ve_tile_info
{
    REG32    ve_num_tile_rows_minus1 :  8;//[7:0]
    REG32 ve_num_tile_columns_minus1 :  8;//[15:8]
    REG32                ve_tiled_en :  1;//[16:16]
    REG32                      rsvd0 : 15;//[31:17]
}t_reg_ve_tile_info;

typedef struct t_reg_vcpi_pps_info0
{
    REG32                        ve_cb_qp_offset :  6;//[5:0]
    REG32                        ve_cr_qp_offset :  6;//[11:6]
    REG32                    ve_beta_offset_div2 :  4;//[15:12]
    REG32                      ve_tc_offset_div2 :  4;//[19:16]
    REG32            ve_entropy_sync_enable_flag :  1;//[20:20]
    REG32 ve_loop_filter_cross_slice_enable_flag :  1;//[21:21]
    REG32  ve_loop_filter_cross_tile_enable_flag :  1;//[22:22]
    REG32       ve_pcm_loop_filter_disabled_flag :  1;//[23:23]
    REG32                    ve_mvd_l1_zero_flag :  1;//[24:24]
    REG32     ve_chma_qp_adjustment_enabled_flag :  1;//[25:25]
    REG32                      ve_cabac_init_idc :  2;//[27:26]
    REG32                 ve_trans_8x8_mode_flag :  1;//[28:28]
    REG32                                  rsvd0 :  3;//[31:29]
}t_reg_vcpi_pps_info0;

typedef struct t_reg_vcpi_pps_info1
{
    REG32                   ve_amp_enable_flag :  1;//[0:0]
    REG32         ve_max_transform_depth_inter :  2;//[2:1]
    REG32         ve_max_transform_depth_intra :  2;//[4:3]
    REG32               ve_log2_max_trafo_size :  4;//[8:5]
    REG32               ve_log2_min_trafo_size :  4;//[12:9]
    REG32                   ve_ctb_log2_size_y :  3;//[15:13]
    REG32            ve_transform_skip_enabled :  1;//[16:16]
    REG32         ve_transquant_bypass_enabled :  1;//[17:17]
    REG32          ve_sign_data_hiding_enabled :  1;//[18:18]
    REG32               ve_cu_qp_delta_enabled :  1;//[19:19]
    REG32         ve_log2_min_cu_qp_delta_size :  4;//[23:20]
    REG32 ve_log2_min_cu_chroma_qp_adjust_size :  4;//[27:24]
    REG32                ve_max_num_merge_cand :  3;//[30:28]
    REG32                                rsvd0 :  1;//[31:31]
}t_reg_vcpi_pps_info1;

typedef struct t_reg_vcpi_clk_force0
{
    REG32     ve_pipe_clkforce_en :  1;//[0:0]
    REG32    ve_vctrl_clkforce_en :  1;//[1:1]
    REG32    ve_curld_clkforce_en :  1;//[2:2]
    REG32      ve_pme_clkforce_en :  1;//[3:3]
    REG32    ve_pmest_clkforce_en :  1;//[4:4]
    REG32    ve_refld_clkforce_en :  1;//[5:5]
    REG32 ve_cpixdmov_clkforce_en :  1;//[6:6]
    REG32   ve_dsctrl_clkforce_en :  1;//[7:7]
    REG32  ve_bndctrl_clkforce_en :  1;//[8:8]
    REG32      ve_l2c_clkforce_en :  1;//[9:9]
    REG32      ve_nbi_clkforce_en :  1;//[10:10]
    REG32      ve_mmu_clkforce_en :  1;//[11:11]
    REG32      ve_ime_clkforce_en :  1;//[12:12]
    REG32   ve_pintra_clkforce_en :  1;//[13:13]
    REG32 ve_rpixctrl_clkforce_en :  1;//[14:14]
    REG32  ve_pixctrl_clkforce_en :  1;//[15:15]
    REG32      ve_qpg_clkforce_en :  1;//[16:16]
    REG32      ve_fme_clkforce_en :  1;//[17:17]
    REG32    ve_tqitq_clkforce_en :  1;//[18:18]
    REG32      ve_mvp_clkforce_en :  1;//[19:19]
    REG32      ve_pmf_clkforce_en :  1;//[20:20]
    REG32      ve_sel_clkforce_en :  1;//[21:21]
    REG32  ve_optdmov_clkforce_en :  1;//[22:22]
    REG32    ve_intra_clkforce_en :  1;//[23:23]
    REG32   ve_saoenc_clkforce_en :  1;//[24:24]
    REG32      ve_dbk_clkforce_en :  1;//[25:25]
    REG32   ve_saodec_clkforce_en :  1;//[26:26]
    REG32     ve_pack_clkforce_en :  1;//[27:27]
    REG32    ve_recst_clkforce_en :  1;//[28:28]
    REG32                   rsvd0 :  3;//[31:29]
}t_reg_vcpi_clk_force0;

typedef struct t_reg_vcpi_clk_force1
{
    REG32  ve_parser_clkforce_en :  1;//[0:0]
    REG32 ve_h4cabac_clkforce_en :  1;//[1:1]
    REG32 ve_h5cabac_clkforce_en :  1;//[2:2]
    REG32    ve_jvlc_clkforce_en :  1;//[3:3]
    REG32 ve_h4cabad_clkforce_en :  1;//[4:4]
    REG32 ve_h5cabad_clkforce_en :  1;//[5:5]
    REG32    ve_jvld_clkforce_en :  1;//[6:6]
    REG32     ve_sed_clkforce_en :  1;//[7:7]
    REG32   ve_bsdma_clkforce_en :  1;//[8:8]
    REG32                  rsvd0 : 23;//[31:9]
}t_reg_vcpi_clk_force1;

typedef struct t_reg_vcpi_slice_split_cfg
{
    REG32 ve_slice_split_en :  1;//[0:0]
    REG32     ve_slice_size :  8;//[8:1]
    REG32             rsvd0 : 23;//[31:9]
}t_reg_vcpi_slice_split_cfg;

typedef struct t_reg_vcpi_me_info0
{
    REG32        ve_preject_en :  1;//[0:0]
    REG32 ve_preject_threshold :  1;//[1:1]
    REG32        ve_breject_en :  1;//[2:2]
    REG32               ve_dzc :  1;//[3:3]
    REG32                ve_ir :  1;//[4:4]
    REG32              ve_rgmp :  4;//[8:5]
    REG32               ve_rgp :  3;//[11:9]
    REG32           ve_mrg2_en :  1;//[12:12]
    REG32                rsvd0 : 19;//[31:13]
}t_reg_vcpi_me_info0;

typedef struct t_reg_vcpi_me_info1
{
    REG32   ve_me_frmcfg2_pr_th2 :  5;//[4:0]
    REG32  ve_me_frmcfg2_pr_thdx :  6;//[10:5]
    REG32  ve_me_frmcfg2_pr_thdy :  4;//[14:11]
    REG32  ve_me_frmcfg2_pr_thca :  3;//[17:15]
    REG32  ve_me_frmcfg2_pr_thcb :  2;//[19:18]
    REG32 ve_me_frmcfg2_pr_thcnt :  3;//[22:20]
    REG32    ve_me_frmcfg2_ir_th :  6;//[28:23]
    REG32                  rsvd0 :  3;//[31:29]
}t_reg_vcpi_me_info1;

typedef struct t_reg_vcpi_me_info2
{
    REG32  ve_pme_area_width :  4;//[3:0]
    REG32 ve_pme_area_height :  4;//[7:4]
    REG32              rsvd0 : 24;//[31:8]
}t_reg_vcpi_me_info2;

typedef struct t_reg_vcpi_me_mvlimit
{
    REG32  ve_pme_mvlimit_left :  8;//[7:0]
    REG32 ve_pme_mvlimit_right :  8;//[15:8]
    REG32    ve_pme_mvlimit_up :  8;//[23:16]
    REG32  ve_pme_mvlimit_down :  8;//[31:24]
}t_reg_vcpi_me_mvlimit;

typedef struct t_reg_vcpi_me_wight
{
    REG32 ve_me_frmwgt0 :  8;//[7:0]
    REG32 ve_me_frmwgt1 :  8;//[15:8]
    REG32 ve_me_frmwgt2 :  8;//[23:16]
    REG32 ve_me_frmwgt3 :  8;//[31:24]
}t_reg_vcpi_me_wight;

typedef struct t_reg_vcpi_me_cu_en
{
    REG32   ve_disable_inter4x4 :  1;//[0:0]
    REG32   ve_disable_inter4x8 :  1;//[1:1]
    REG32   ve_disable_inter8x4 :  1;//[2:2]
    REG32   ve_disable_inter8x8 :  1;//[3:3]
    REG32  ve_disable_inter8x16 :  1;//[4:4]
    REG32  ve_disable_inter16x8 :  1;//[5:5]
    REG32 ve_disable_inter16x16 :  1;//[6:6]
    REG32      ve_disable_pskip :  1;//[7:7]
    REG32   ve_disable_intra4x4 :  1;//[8:8]
    REG32   ve_disable_intra8x8 :  1;//[9:9]
    REG32 ve_disable_intra16x16 :  1;//[10:10]
    REG32 ve_disable_intra32x32 :  1;//[11:11]
    REG32 ve_disable_inter32x32 :  1;//[12:12]
    REG32      ve_disable_bskip :  1;//[13:13]
    REG32        ve_disable_tu8 :  1;//[14:14]
    REG32 ve_disable_inter64x64 :  1;//[15:15]
    REG32                 rsvd0 : 16;//[31:16]
}t_reg_vcpi_me_cu_en;

typedef struct t_reg_vcpi_me_cst0
{
    REG32          ve_skip0 :  7;//[6:0]
    REG32          ve_skip1 :  7;//[13:7]
    REG32          ve_skip2 :  7;//[20:14]
    REG32 ve_split0_intra16 :  7;//[27:21]
    REG32             rsvd0 :  4;//[31:28]
}t_reg_vcpi_me_cst0;

typedef struct t_reg_vcpi_me_cst1
{
    REG32 ve_split1_intra8 :  7;//[6:0]
    REG32 ve_split2_intra4 :  7;//[13:7]
    REG32  ve_pred_inter16 :  7;//[20:14]
    REG32    ve_mrg_inter8 :  7;//[27:21]
    REG32            rsvd0 :  4;//[31:28]
}t_reg_vcpi_me_cst1;

typedef struct t_reg_vcpi_me_cst2
{
    REG32 ve_mrg_idx_birect16 :  7;//[6:0]
    REG32         ve_bdirect8 :  7;//[13:7]
    REG32          ve_unipred :  3;//[16:14]
    REG32           ve_bipred :  3;//[19:17]
    REG32               rsvd0 : 12;//[31:20]
}t_reg_vcpi_me_cst2;

typedef struct t_reg_vcpi_me_ipenalty
{
    REG32 ve_angular_penaty :  5;//[4:0]
    REG32  ve_planar_penaty :  5;//[9:5]
    REG32      ve_dc_penaty :  5;//[14:10]
    REG32  ve_accum8_penaty :  5;//[19:15]
    REG32 ve_accum16_penaty :  5;//[24:20]
    REG32  ve_full32_penaty :  5;//[29:25]
    REG32             rsvd0 :  2;//[31:30]
}t_reg_vcpi_me_ipenalty;

typedef struct t_reg_vcpi_me_cost_penalty
{
    REG32         ve_intra_penalty :  6;//[5:0]
    REG32  ve_accum8_inter_penalty :  5;//[10:6]
    REG32 ve_accum16_inter_penalty :  5;//[15:11]
    REG32 ve_accum32_inter_penalty :  5;//[20:16]
    REG32                    rsvd0 : 11;//[31:21]
}t_reg_vcpi_me_cost_penalty;

typedef struct t_reg_vcpi_me_zero_cut
{
    REG32  ve_zerocut_8 :  4;//[3:0]
    REG32 ve_zerocut_16 :  4;//[7:4]
    REG32 ve_zerocut_32 :  4;//[11:8]
    REG32 ve_zerocut_64 :  5;//[16:12]
    REG32         rsvd0 : 15;//[31:17]
}t_reg_vcpi_me_zero_cut;

typedef struct t_reg_vcpi_me_tmvpenalty
{
    REG32  ve_min_penaty :  4;//[3:0]
    REG32 ve_div8_penaty :  3;//[6:4]
    REG32  ve_reject_thx :  6;//[12:7]
    REG32  ve_reject_thy :  6;//[18:13]
    REG32          rsvd0 : 13;//[31:19]
}t_reg_vcpi_me_tmvpenalty;

typedef struct t_reg_vcpi_src_pic_size
{
    REG32 ve_src_pic_height : 16;//[15:0]
    REG32  ve_src_pic_width : 16;//[31:16]
}t_reg_vcpi_src_pic_size;

typedef struct t_reg_vcpi_src_format
{
    REG32       ve_src_format :  6;//[5:0]
    REG32 ve_msb_aligned_flag :  1;//[6:6]
    REG32               rsvd0 : 25;//[31:7]
}t_reg_vcpi_src_format;

typedef struct t_reg_vcpi_src_ctrl_info
{
    REG32 ve_chroma_convert_en :  1;//[0:0]
    REG32     ve_stripe_height :  2;//[2:1]
    REG32            ve_uv_pad :  1;//[3:3]
    REG32        ve_mvrot_memc :  3;//[6:4]
    REG32    ve_memc_tf_swtich :  3;//[9:7]
    REG32         ve_src_aq_en :  1;//[10:10]
    REG32            ve_pme_en :  1;//[11:11]
    REG32          ve_bim_mode :  3;//[14:12]
    REG32         ve_bim_aq_en :  1;//[15:15]
    REG32        ve_ref0_valid :  1;//[16:16]
    REG32        ve_ref1_valid :  1;//[17:17]
    REG32                rsvd0 : 14;//[31:18]
}t_reg_vcpi_src_ctrl_info;

typedef struct t_reg_vcpi_src_uv_pad_value
{
    REG32 ve_user_chma_value : 10;//[9:0]
    REG32              rsvd0 : 22;//[31:10]
}t_reg_vcpi_src_uv_pad_value;

typedef struct t_reg_vcpi_src_rotation
{
    REG32 ve_rotation_degree :  2;//[1:0]
    REG32     ve_mirror_x_en :  1;//[2:2]
    REG32     ve_mirror_y_en :  1;//[3:3]
    REG32              rsvd0 : 28;//[31:4]
}t_reg_vcpi_src_rotation;

typedef struct t_reg_vcpi_mctf_tf_threshold
{
    REG32  ve_noise_threshold :  6;//[5:0]
    REG32 ve_error_threshold1 :  7;//[12:6]
    REG32 ve_error_threshold2 :  7;//[19:13]
    REG32   ve_diff_threshold : 10;//[29:20]
    REG32               rsvd0 :  2;//[31:30]
}t_reg_vcpi_mctf_tf_threshold;

typedef struct t_reg_vcpi_mctf_tf_weight1
{
    REG32 ve_ww_int_weight0 :  5;//[4:0]
    REG32 ve_ww_int_weight1 :  5;//[9:5]
    REG32 ve_ww_int_weight2 :  4;//[13:10]
    REG32 ve_ww_int_weight3 :  4;//[17:14]
    REG32 ve_ww_int_weight4 :  4;//[21:18]
    REG32    ve_luma_factor :  4;//[25:22]
    REG32    ve_chma_factor :  4;//[29:26]
    REG32             rsvd0 :  2;//[31:30]
}t_reg_vcpi_mctf_tf_weight1;

typedef struct t_reg_vcpi_mctf_tf_weight2
{
    REG32         ve_ref0_strengths :  7;//[6:0]
    REG32         ve_ref1_strengths :  7;//[13:7]
    REG32   ve_luma_sigma_sq_factor :  8;//[21:14]
    REG32 ve_chroma_sigma_sq_factor :  8;//[29:22]
    REG32                     rsvd0 :  2;//[31:30]
}t_reg_vcpi_mctf_tf_weight2;

typedef struct t_reg_vcpi_src_aq_pre_frm_avg_svar
{
    REG32        ve_aq_avg_svar :  8;//[7:0]
    REG32     ve_aq_svar_method :  2;//[9:8]
    REG32 ve_aq_frm_svar_method :  1;//[10:10]
    REG32     ve_aq_max_frm_ssd :  5;//[15:11]
    REG32   ve_aq_max_frm_error :  5;//[20:16]
    REG32                 rsvd0 : 11;//[31:21]
}t_reg_vcpi_src_aq_pre_frm_avg_svar;

typedef struct t_reg_vcpi_src_aq_stripe_qpdelta_para
{
    REG32     ve_aq_neg_ratio :  6;//[5:0]
    REG32     ve_aq_pos_ratio :  6;//[11:6]
    REG32 ve_aq_qpdelta_limit :  4;//[15:12]
    REG32           ve_aq_src :  6;//[21:16]
    REG32        ve_aq_weight :  4;//[25:22]
    REG32 ve_bim_aq_neg_ratio :  3;//[28:26]
    REG32 ve_bim_aq_pos_ratio :  3;//[31:29]
}t_reg_vcpi_src_aq_stripe_qpdelta_para;

typedef struct t_reg_vcpi_src_sa_th
{
    REG32  ve_sa_ssd_th0 :  7;//[6:0]
    REG32  ve_sa_ssd_th1 :  7;//[13:7]
    REG32 ve_aq_svar_th0 :  4;//[17:14]
    REG32 ve_aq_svar_th1 :  4;//[21:18]
    REG32   ve_sa_mv_th0 :  5;//[26:22]
    REG32   ve_sa_mv_th1 :  5;//[31:27]
}t_reg_vcpi_src_sa_th;

typedef struct t_reg_vcpi_src_bim_aq_th
{
    REG32 ve_bim_aq_th0 :  8;//[7:0]
    REG32 ve_bim_aq_th1 :  8;//[15:8]
    REG32 ve_bim_aq_th2 :  8;//[23:16]
    REG32 ve_bim_aq_th3 :  8;//[31:24]
}t_reg_vcpi_src_bim_aq_th;

typedef struct t_reg_vcpi_src_bim_aq_weight
{
    REG32 ve_bim_aq_tf_weight0 :  8;//[7:0]
    REG32 ve_bim_aq_tf_weight1 :  8;//[15:8]
    REG32  ve_bim_aq_sa_weight :  4;//[19:16]
    REG32  ve_bim_aq_sa_center :  8;//[27:20]
    REG32   ve_bim_aq_sa_coeff :  4;//[31:28]
}t_reg_vcpi_src_bim_aq_weight;

typedef struct t_reg_vcpi_src_osd_mosaic_ctrl
{
    REG32  ve_osd_0_en :  1;//[0:0]
    REG32  ve_osd_1_en :  1;//[1:1]
    REG32        rsvd0 : 14;//[15:2]
    REG32 ve_mosaic_en : 16;//[31:16]
}t_reg_vcpi_src_osd_mosaic_ctrl;

typedef struct t_reg_vcpi_src_osd_0_color_param
{
    REG32       ve_osd_0_cvt_colol_th : 10;//[9:0]
    REG32         ve_osd_0_init_alpha :  5;//[14:10]
    REG32             ve_osd_0_format :  2;//[16:15]
    REG32       ve_osd_0_cvt_color_en :  1;//[17:17]
    REG32      ve_osd_0_init_alpha_en :  1;//[18:18]
    REG32 ve_osd_0_rgb2yuv_coeff_mode :  2;//[20:19]
    REG32                       rsvd0 : 11;//[31:21]
}t_reg_vcpi_src_osd_0_color_param;

typedef struct t_reg_vcpi_src_osd_1_color_param
{
    REG32       ve_osd_1_cvt_colol_th : 10;//[9:0]
    REG32         ve_osd_1_init_alpha :  5;//[14:10]
    REG32             ve_osd_1_format :  2;//[16:15]
    REG32       ve_osd_1_cvt_color_en :  1;//[17:17]
    REG32      ve_osd_1_init_alpha_en :  1;//[18:18]
    REG32 ve_osd_1_rgb2yuv_coeff_mode :  2;//[20:19]
    REG32                       rsvd0 : 11;//[31:21]
}t_reg_vcpi_src_osd_1_color_param;

typedef struct t_reg_vcpi_src_osd_0_start_pos
{
    REG32 ve_osd_0_st_x : 16;//[15:0]
    REG32 ve_osd_0_st_y : 16;//[31:16]
}t_reg_vcpi_src_osd_0_start_pos;

typedef struct t_reg_vcpi_src_osd_1_start_pos
{
    REG32 ve_osd_1_st_x : 16;//[15:0]
    REG32 ve_osd_1_st_y : 16;//[31:16]
}t_reg_vcpi_src_osd_1_start_pos;

typedef struct t_reg_vcpi_src_osd_0_size
{
    REG32  ve_osd_0_width : 16;//[15:0]
    REG32 ve_osd_0_height : 16;//[31:16]
}t_reg_vcpi_src_osd_0_size;

typedef struct t_reg_vcpi_src_osd_1_size
{
    REG32  osd_1_width : 16;//[15:0]
    REG32 osd_1_height : 16;//[31:16]
}t_reg_vcpi_src_osd_1_size;

typedef uint32_t t_reg_vcpi_src_osd0_addr_base_lo;

typedef uint32_t t_reg_vcpi_src_osd0_addr_base_hi;

typedef uint32_t t_reg_vcpi_src_osd1_addr_base_lo;

typedef uint32_t t_reg_vcpi_src_osd1_addr_base_hi;

typedef struct t_reg_vcpi_src_osd_stride
{
    REG32 ve_src_osd0_stride : 16;//[15:0]
    REG32 ve_src_osd1_stride : 16;//[31:16]
}t_reg_vcpi_src_osd_stride;

typedef struct t_reg_vcpi_src_mosaic_pos
{
    REG32 ve_mosaic_st_x : 16;//[15:0]
    REG32 ve_mosaic_st_y : 16;//[31:16]
}t_reg_vcpi_src_mosaic_pos;

typedef struct t_reg_vcpi_src_mosaic_size
{
    REG32  ve_mosaic_width : 16;//[15:0]
    REG32 ve_mosaic_height : 16;//[31:16]
}t_reg_vcpi_src_mosaic_size;

typedef struct t_reg_vcpi_roi_enable
{
    REG32 ve_roi_en : 16;//[15:0]
    REG32     rsvd0 : 16;//[31:16]
}t_reg_vcpi_roi_enable;

typedef struct t_reg_vcpi_roi_pos
{
    REG32 ve_roi_st_x : 16;//[15:0]
    REG32 ve_roi_st_y : 16;//[31:16]
}t_reg_vcpi_roi_pos;

typedef struct t_reg_vcpi_roi_size
{
    REG32  ve_roi_width : 16;//[15:0]
    REG32 ve_roi_height : 16;//[31:16]
}t_reg_vcpi_roi_size;

typedef struct t_reg_vcpi_roi_value
{
    REG32 roi_priority :  4;//[3:0]
    REG32       roi_fs :  1;//[4:4]
    REG32       roi_fi :  1;//[5:5]
    REG32      roi_dqp :  8;//[13:6]
    REG32      roi_qpf :  7;//[20:14]
    REG32        rsvd0 : 11;//[31:21]
}t_reg_vcpi_roi_value;

typedef uint32_t t_reg_vcpi_fbc_lut_base_lo;

typedef uint32_t t_reg_vcpi_fbc_lut_base_hi;

typedef uint32_t t_reg_vcpi_fbc_slice_buf_base_lo;

typedef uint32_t t_reg_vcpi_fbc_slice_buf_base_hi;

typedef uint32_t t_reg_vcpi_fbc_slice_ring_offset;
typedef struct t_reg_vcpi_fbc_slice_stride
{
    REG32 ve_fbc_slice_stride : 18;//[17:0]
    REG32               rsvd0 : 14;//[31:18]
}t_reg_vcpi_fbc_slice_stride;

typedef uint32_t t_reg_vcpi_fbc_slice_buf_size;
typedef uint32_t t_reg_vcpi_ref0_lut_base_lo;

typedef uint32_t t_reg_vcpi_ref0_lut_base_hi;

typedef uint32_t t_reg_vcpi_ref1_lut_base_lo;

typedef uint32_t t_reg_vcpi_ref1_lut_base_hi;

typedef uint32_t t_reg_vcpi_ref0_slice_base_lo;

typedef uint32_t t_reg_vcpi_ref0_slice_base_hi;

typedef uint32_t t_reg_vcpi_ref1_slice_base_lo;

typedef uint32_t t_reg_vcpi_ref1_slice_base_hi;

typedef struct t_reg_vcpi_rgb2yuv_coef0
{
    REG32 ve_rgb2yuv_coeff0_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef0;

typedef struct t_reg_vcpi_rgb2yuv_coef1
{
    REG32 ve_rgb2yuv_coeff1_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef1;

typedef struct t_reg_vcpi_rgb2yuv_coef2
{
    REG32 ve_rgb2yuv_coeff2_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef2;

typedef struct t_reg_vcpi_rgb2yuv_coef3
{
    REG32 ve_rgb2yuv_coeff3_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef3;

typedef struct t_reg_vcpi_rgb2yuv_coef4
{
    REG32 ve_rgb2yuv_coeff4_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef4;

typedef struct t_reg_vcpi_rgb2yuv_coef5
{
    REG32 ve_rgb2yuv_coeff5_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef5;

typedef struct t_reg_vcpi_rgb2yuv_coef6
{
    REG32 ve_rgb2yuv_coeff6_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef6;

typedef struct t_reg_vcpi_rgb2yuv_coef7
{
    REG32 ve_rgb2yuv_coeff7_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef7;

typedef struct t_reg_vcpi_rgb2yuv_coef8
{
    REG32 ve_rgb2yuv_coeff8_matrix : 16;//[15:0]
    REG32                    rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_coef8;

typedef struct t_reg_vcpi_rgb2yuv_yuv_val_range
{
    REG32 ve_luma_min :  8;//[7:0]
    REG32 ve_luma_max :  8;//[15:8]
    REG32 ve_chma_min :  8;//[23:16]
    REG32 ve_chma_max :  8;//[31:24]
}t_reg_vcpi_rgb2yuv_yuv_val_range;

typedef struct t_reg_vcpi_rgb2yuv_rgb_val_range
{
    REG32 ve_rgb_min :  8;//[7:0]
    REG32 ve_rgb_max :  8;//[15:8]
    REG32      rsvd0 : 16;//[31:16]
}t_reg_vcpi_rgb2yuv_rgb_val_range;

typedef uint32_t t_reg_vcpi_src_ext_base_lo_0;

typedef uint32_t t_reg_vcpi_src_ext_base_hi_0;

typedef uint32_t t_reg_vcpi_src_ext_base_lo_1;

typedef uint32_t t_reg_vcpi_src_ext_base_hi_1;

typedef uint32_t t_reg_vcpi_src_ext_base_lo_2;

typedef uint32_t t_reg_vcpi_src_ext_base_hi_2;

typedef uint32_t t_reg_vcpi_src_pre_ext_base_lo_0;

typedef uint32_t t_reg_vcpi_src_pre_ext_base_hi_0;

typedef uint32_t t_reg_vcpi_src_pre_ext_base_lo_1;

typedef uint32_t t_reg_vcpi_src_pre_ext_base_hi_1;

typedef uint32_t t_reg_vcpi_src_pre_ext_base_lo_2;

typedef uint32_t t_reg_vcpi_src_pre_ext_base_hi_2;

typedef uint32_t t_reg_vcpi_src_post_ext_base_lo_0;

typedef uint32_t t_reg_vcpi_src_post_ext_base_hi_0;

typedef uint32_t t_reg_vcpi_src_post_ext_base_lo_1;

typedef uint32_t t_reg_vcpi_src_post_ext_base_hi_1;

typedef uint32_t t_reg_vcpi_src_post_ext_base_lo_2;

typedef uint32_t t_reg_vcpi_src_post_ext_base_hi_2;

typedef uint32_t t_reg_vcpi_pmest_base_lo;

typedef uint32_t t_reg_vcpi_pmest_base_hi;

typedef uint32_t t_reg_vcpi_ds_load_base_lo_0;

typedef uint32_t t_reg_vcpi_ds_load_base_hi_0;

typedef uint32_t t_reg_vcpi_ds_load_base_lo_1;

typedef uint32_t t_reg_vcpi_ds_load_base_hi_1;

typedef uint32_t t_reg_vcpi_src_stride_0;
typedef uint32_t t_reg_vcpi_src_stride_1;
typedef uint32_t t_reg_vcpi_src_stride_2;
typedef uint32_t t_reg_vcpi_src_pre_stride_0;
typedef uint32_t t_reg_vcpi_src_pre_stride_1;
typedef uint32_t t_reg_vcpi_src_pre_stride_2;
typedef uint32_t t_reg_vcpi_src_post_stride_0;
typedef uint32_t t_reg_vcpi_src_post_stride_1;
typedef uint32_t t_reg_vcpi_src_post_stride_2;
typedef uint32_t t_reg_vcpi_pmest_stride;
typedef uint32_t t_reg_vcpi_downsample_stride_0;
typedef uint32_t t_reg_vcpi_downsample_stride_1;
typedef uint32_t t_reg_vcpi_pks_buf0_addr_lo;

typedef uint32_t t_reg_vcpi_pks_buf0_addr_hi;

typedef uint32_t t_reg_vcpi_pks_buf0_len;
typedef uint32_t t_reg_vcpi_pks_buf1_addr_lo;

typedef uint32_t t_reg_vcpi_pks_buf1_addr_hi;

typedef uint32_t t_reg_vcpi_pks_buf1_len;
typedef uint32_t t_reg_vcpi_pks_buf2_addr_lo;

typedef uint32_t t_reg_vcpi_pks_buf2_addr_hi;

typedef uint32_t t_reg_vcpi_pks_buf2_len;
typedef uint32_t t_reg_vcpi_pks_buf3_addr_lo;

typedef uint32_t t_reg_vcpi_pks_buf3_addr_hi;

typedef uint32_t t_reg_vcpi_pks_buf3_len;
typedef uint32_t t_reg_vcpi_bnd_buf_size;
typedef uint32_t t_reg_vcpi_bnd_row_addr_lo;

typedef uint32_t t_reg_vcpi_bnd_row_addr_hi;

typedef uint32_t t_reg_vcpi_col_load_addr_lo;

typedef uint32_t t_reg_vcpi_col_load_addr_hi;

typedef uint32_t t_reg_vcpi_col_store_addr_lo;

typedef uint32_t t_reg_vcpi_col_store_addr_hi;

typedef struct t_reg_vcpi_col_total_word
{
    REG32 ve_col_total_word : 21;//[20:0]
    REG32             rsvd0 : 11;//[31:21]
}t_reg_vcpi_col_total_word;

typedef uint32_t t_reg_vcpi_ds_load_addr_lo;

typedef uint32_t t_reg_vcpi_ds_load_addr_hi;

typedef uint32_t t_reg_vcpi_ds_store_addr_lo;

typedef uint32_t t_reg_vcpi_ds_store_addr_hi;

typedef uint32_t t_reg_vcpi_qpg_load_addr_lo;

typedef uint32_t t_reg_vcpi_qpg_load_addr_hi;

typedef uint32_t t_reg_vcpi_bitbuf_addr_lo;

typedef uint32_t t_reg_vcpi_bitbuf_addr_hi;

typedef struct t_reg_vcpi_bitbuf_len
{
    REG32 ve_bitbuf_len : 31;//[30:0]
    REG32         rsvd0 :  1;//[31:31]
}t_reg_vcpi_bitbuf_len;

typedef struct t_reg_vcpi_bus_ctrl
{
    REG32 ve_bus_ctrl :  2;//[1:0]
    REG32       rsvd0 : 30;//[31:2]
}t_reg_vcpi_bus_ctrl;

typedef struct t_reg_vcpi_read_ostd_num
{
    REG32  ve_ref_rd_otsd :  6;//[5:0]
    REG32  ve_bnd_rd_otsd :  3;//[8:6]
    REG32  ve_src_rd_otsd :  6;//[14:9]
    REG32 ve_mctf_rd_otsd :  6;//[20:15]
    REG32   ve_ds_rd_otsd :  5;//[25:21]
    REG32  ve_pks_rd_otsd :  4;//[29:26]
    REG32           rsvd0 :  2;//[31:30]
}t_reg_vcpi_read_ostd_num;

typedef struct t_reg_vcpi_write_ostd_num
{
    REG32 ve_recst_wr_otsd :  5;//[4:0]
    REG32   ve_bnd_wr_otsd :  4;//[8:5]
    REG32 ve_vlcst_wr_otsd :  4;//[12:9]
    REG32    ve_ds_wr_otsd :  6;//[18:13]
    REG32   ve_pks_wr_otsd :  4;//[22:19]
    REG32            rsvd0 :  9;//[31:23]
}t_reg_vcpi_write_ostd_num;

typedef struct t_reg_vcpi_mmu_chn_bypass
{
    REG32      ve_refld_bypass :  1;//[0:0]
    REG32        ve_bnd_bypass :  1;//[1:1]
    REG32     ve_src_ld_bypass :  1;//[2:2]
    REG32  ve_presrc_ld_bypass :  1;//[3:3]
    REG32 ve_postsrc_ld_bypass :  1;//[4:4]
    REG32      ve_ds_ld_bypass :  1;//[5:5]
    REG32     ve_pme_st_bypass :  1;//[6:6]
    REG32     ve_pks_st_bypass :  1;//[7:7]
    REG32      ve_recst_bypass :  1;//[8:8]
    REG32        ve_qpg_bypass :  1;//[9:9]
    REG32      ve_bs_st_bypass :  1;//[10:10]
    REG32     ve_pks_ld_bypass :  1;//[11:11]
    REG32                rsvd0 : 20;//[31:12]
}t_reg_vcpi_mmu_chn_bypass;

typedef struct t_reg_vcpi_mmu_chn_prio
{
    REG32      ve_refld_priority :  1;//[0:0]
    REG32        ve_bnd_priority :  1;//[1:1]
    REG32     ve_src_ld_priority :  1;//[2:2]
    REG32  ve_presrc_ld_priority :  1;//[3:3]
    REG32 ve_postsrc_ld_priority :  1;//[4:4]
    REG32      ve_ds_ld_priority :  1;//[5:5]
    REG32     ve_pme_st_priority :  1;//[6:6]
    REG32     ve_pks_st_priority :  1;//[7:7]
    REG32      ve_recst_priority :  1;//[8:8]
    REG32        ve_qpg_priority :  1;//[9:9]
    REG32      ve_bs_st_priority :  1;//[10:10]
    REG32   ve_master11_priority :  1;//[11:11]
    REG32                  rsvd0 : 20;//[31:12]
}t_reg_vcpi_mmu_chn_prio;

typedef struct t_reg_vcpi_mmu_evtsel0
{
    REG32 ve_master0_evtsel :  3;//[2:0]
    REG32 ve_master1_evtsel :  3;//[5:3]
    REG32 ve_master2_evtsel :  3;//[8:6]
    REG32 ve_master3_evtsel :  3;//[11:9]
    REG32 ve_master4_evtsel :  3;//[14:12]
    REG32 ve_master5_evtsel :  3;//[17:15]
    REG32 ve_master6_evtsel :  3;//[20:18]
    REG32 ve_master7_evtsel :  3;//[23:21]
    REG32 ve_master8_evtsel :  3;//[26:24]
    REG32 ve_master9_evtsel :  3;//[29:27]
    REG32             rsvd0 :  2;//[31:30]
}t_reg_vcpi_mmu_evtsel0;

typedef struct t_reg_vcpi_mmu_evtsel1
{
    REG32 ve_master10_evtsel :  3;//[2:0]
    REG32 ve_master11_evtsel :  3;//[5:3]
    REG32              rsvd0 : 26;//[31:6]
}t_reg_vcpi_mmu_evtsel1;

typedef struct t_reg_vcpi_fro_dc_0
{
    REG32   ve_dc_luma_iii_8x8 :  8;//[7:0]
    REG32 ve_dc_luma_iii_16x16 :  8;//[15:8]
    REG32 ve_dc_luma_iii_32x32 :  8;//[23:16]
    REG32 ve_dc_luma_iii_64x64 :  8;//[31:24]
}t_reg_vcpi_fro_dc_0;

typedef struct t_reg_vcpi_fro_dc_1
{
    REG32   ve_dc_luma_iip_8x8 :  8;//[7:0]
    REG32 ve_dc_luma_iip_16x16 :  8;//[15:8]
    REG32 ve_dc_luma_iip_32x32 :  8;//[23:16]
    REG32 ve_dc_luma_iip_64x64 :  8;//[31:24]
}t_reg_vcpi_fro_dc_1;

typedef struct t_reg_vcpi_fro_dc_2
{
    REG32   ve_dc_luma_eip_8x8 :  8;//[7:0]
    REG32 ve_dc_luma_eip_16x16 :  8;//[15:8]
    REG32 ve_dc_luma_eip_32x32 :  8;//[23:16]
    REG32 ve_dc_luma_eip_64x64 :  8;//[31:24]
}t_reg_vcpi_fro_dc_2;

typedef struct t_reg_vcpi_fro_dc_3
{
    REG32   ve_dc_chroma_iii_4x4 :  8;//[7:0]
    REG32   ve_dc_chroma_iii_8x8 :  8;//[15:8]
    REG32 ve_dc_chroma_iii_16x16 :  8;//[23:16]
    REG32 ve_dc_chroma_iii_32x32 :  8;//[31:24]
}t_reg_vcpi_fro_dc_3;

typedef struct t_reg_vcpi_fro_dc_4
{
    REG32   ve_dc_chroma_iip_4x4 :  8;//[7:0]
    REG32   ve_dc_chroma_iip_8x8 :  8;//[15:8]
    REG32 ve_dc_chroma_iip_16x16 :  8;//[23:16]
    REG32 ve_dc_chroma_iip_32x32 :  8;//[31:24]
}t_reg_vcpi_fro_dc_4;

typedef struct t_reg_vcpi_fro_dc_5
{
    REG32   ve_dc_chroma_eip_4x4 :  8;//[7:0]
    REG32   ve_dc_chroma_eip_8x8 :  8;//[15:8]
    REG32 ve_dc_chroma_eip_16x16 :  8;//[23:16]
    REG32 ve_dc_chroma_eip_32x32 :  8;//[31:24]
}t_reg_vcpi_fro_dc_5;

typedef struct t_reg_vcpi_fro_ac_0
{
    REG32   ve_ac_luma_iii_8x8 :  8;//[7:0]
    REG32 ve_ac_luma_iii_16x16 :  8;//[15:8]
    REG32 ve_ac_luma_iii_32x32 :  8;//[23:16]
    REG32 ve_ac_luma_iii_64x64 :  8;//[31:24]
}t_reg_vcpi_fro_ac_0;

typedef struct t_reg_vcpi_fro_ac_1
{
    REG32   ve_ac_luma_iip_8x8 :  8;//[7:0]
    REG32 ve_ac_luma_iip_16x16 :  8;//[15:8]
    REG32 ve_ac_luma_iip_32x32 :  8;//[23:16]
    REG32 ve_ac_luma_iip_64x64 :  8;//[31:24]
}t_reg_vcpi_fro_ac_1;

typedef struct t_reg_vcpi_fro_ac_2
{
    REG32   ve_ac_luma_eip_8x8 :  8;//[7:0]
    REG32 ve_ac_luma_eip_16x16 :  8;//[15:8]
    REG32 ve_ac_luma_eip_32x32 :  8;//[23:16]
    REG32 ve_ac_luma_eip_64x64 :  8;//[31:24]
}t_reg_vcpi_fro_ac_2;

typedef struct t_reg_vcpi_fro_ac_3
{
    REG32   ve_ac_chroma_iii_4x4 :  8;//[7:0]
    REG32   ve_ac_chroma_iii_8x8 :  8;//[15:8]
    REG32 ve_ac_chroma_iii_16x16 :  8;//[23:16]
    REG32 ve_ac_chroma_iii_32x32 :  8;//[31:24]
}t_reg_vcpi_fro_ac_3;

typedef struct t_reg_vcpi_fro_ac_4
{
    REG32   ve_ac_chroma_iip_4x4 :  8;//[7:0]
    REG32   ve_ac_chroma_iip_8x8 :  8;//[15:8]
    REG32 ve_ac_chroma_iip_16x16 :  8;//[23:16]
    REG32 ve_ac_chroma_iip_32x32 :  8;//[31:24]
}t_reg_vcpi_fro_ac_4;

typedef struct t_reg_vcpi_fro_ac_5
{
    REG32   ve_ac_chroma_eip_4x4 :  8;//[7:0]
    REG32   ve_ac_chroma_eip_8x8 :  8;//[15:8]
    REG32 ve_ac_chroma_eip_16x16 :  8;//[23:16]
    REG32 ve_ac_chroma_eip_32x32 :  8;//[31:24]
}t_reg_vcpi_fro_ac_5;

typedef struct t_reg_vcpi_fro_st_0
{
    REG32   ve_st_luma_iii_8x8 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32 ve_st_luma_iii_16x16 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_st_luma_iii_32x32 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_st_luma_iii_64x64 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_st_0;

typedef struct t_reg_vcpi_fro_st_1
{
    REG32   ve_st_luma_iip_8x8 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32 ve_st_luma_iip_16x16 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_st_luma_iip_32x32 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_st_luma_iip_64x64 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_st_1;

typedef struct t_reg_vcpi_fro_st_2
{
    REG32   ve_st_luma_eip_8x8 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32 ve_st_luma_eip_16x16 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_st_luma_eip_32x32 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_st_luma_eip_64x64 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_st_2;

typedef struct t_reg_vcpi_fro_st_3
{
    REG32   ve_st_chma_iii_4x4 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32   ve_st_chma_iii_8x8 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_st_chma_iii_16x16 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_st_chma_iii_32x32 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_st_3;

typedef struct t_reg_vcpi_fro_st_4
{
    REG32   ve_st_chma_iip_4x4 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32   ve_st_chma_iip_8x8 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_st_chma_iip_16x16 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_st_chma_iip_32x32 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_st_4;

typedef struct t_reg_vcpi_fro_st_5
{
    REG32   ve_st_chma_eip_4x4 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32   ve_st_chma_eip_8x8 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_st_chma_eip_16x16 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_st_chma_eip_32x32 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_st_5;

typedef struct t_reg_vcpi_fro_mx_0
{
    REG32   ve_mx_luma_iii_8x8 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32 ve_mx_luma_iii_16x16 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_mx_luma_iii_32x32 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_mx_luma_iii_64x64 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_mx_0;

typedef struct t_reg_vcpi_fro_mx_1
{
    REG32   ve_mx_luma_iip_8x8 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32 ve_mx_luma_iip_16x16 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_mx_luma_iip_32x32 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_mx_luma_iip_64x64 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_mx_1;

typedef struct t_reg_vcpi_fro_mx_2
{
    REG32   ve_mx_luma_eip_8x8 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32 ve_mx_luma_eip_16x16 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_mx_luma_eip_32x32 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_mx_luma_eip_64x64 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_mx_2;

typedef struct t_reg_vcpi_fro_mx_3
{
    REG32   ve_mx_chma_iii_4x4 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32   ve_mx_chma_iii_8x8 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_mx_chma_iii_16x16 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_mx_chma_iii_32x32 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_mx_3;

typedef struct t_reg_vcpi_fro_mx_4
{
    REG32   ve_mx_chma_iip_4x4 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32   ve_mx_chma_iip_8x8 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_mx_chma_iip_16x16 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_mx_chma_iip_32x32 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_mx_4;

typedef struct t_reg_vcpi_fro_mx_5
{
    REG32   ve_mx_chma_eip_4x4 :  6;//[5:0]
    REG32                rsvd0 :  2;//[7:6]
    REG32   ve_mx_chma_eip_8x8 :  6;//[13:8]
    REG32                rsvd1 :  2;//[15:14]
    REG32 ve_mx_chma_eip_16x16 :  6;//[21:16]
    REG32                rsvd2 :  2;//[23:22]
    REG32 ve_mx_chma_eip_32x32 :  6;//[29:24]
    REG32                rsvd3 :  2;//[31:30]
}t_reg_vcpi_fro_mx_5;

typedef struct t_reg_vcpi_qpg_lambda
{
    REG32 ve_sqrt_lambda0 :  8;//[7:0]
    REG32  ve_sel_lambda0 : 16;//[23:8]
    REG32           rsvd0 :  8;//[31:24]
}t_reg_vcpi_qpg_lambda;

typedef struct t_reg_vcpi_sao_lambda_group
{
    REG32 ve_sao_lambda0 : 14;//[13:0]
    REG32 ve_sao_lambda1 : 14;//[27:14]
    REG32          rsvd0 :  4;//[31:28]
}t_reg_vcpi_sao_lambda_group;

typedef struct t_reg_vcpi_lambda_scaling
{
    REG32 ve_lambda_scale_inter : 10;//[9:0]
    REG32 ve_lambda_scale_intra : 10;//[19:10]
    REG32                 rsvd0 : 12;//[31:20]
}t_reg_vcpi_lambda_scaling;

typedef struct t_reg_vcpi_lambda_sqrt_scaling
{
    REG32 ve_lambda_sq_scale_inter : 10;//[9:0]
    REG32 ve_lambda_sq_scale_intra : 10;//[19:10]
    REG32                    rsvd0 : 12;//[31:20]
}t_reg_vcpi_lambda_sqrt_scaling;

typedef struct t_reg_vcpi_force_period_intra
{
    REG32    ve_force_intra_ctu_row : 10;//[9:0]
    REG32 ve_force_intra_ctu_period : 15;//[24:10]
    REG32                     rsvd0 :  7;//[31:25]
}t_reg_vcpi_force_period_intra;

typedef struct t_reg_vcpi_tq_qbias
{
    REG32 ve_tq_qbias :  7;//[6:0]
    REG32       rsvd0 : 25;//[31:7]
}t_reg_vcpi_tq_qbias;

typedef struct t_reg_vcpi_mvp_poc
{
    REG32 ve_mvp_curr_poc : 16;//[15:0]
    REG32  ve_mvp_col_poc : 16;//[31:16]
}t_reg_vcpi_mvp_poc;

typedef struct t_reg_vcpi_mvp_ref_poc
{
    REG32 ve_mvp_ref0_poc : 16;//[15:0]
    REG32 ve_mvp_ref1_poc : 16;//[31:16]
}t_reg_vcpi_mvp_ref_poc;

typedef struct t_reg_vcpi_mvp_colref_poc
{
    REG32 ve_mvp_colref0_poc : 16;//[15:0]
    REG32 ve_mvp_colref1_poc : 16;//[31:16]
}t_reg_vcpi_mvp_colref_poc;

typedef struct t_reg_vcpi_mvp_pic_info
{
    REG32 ve_mvp_l0_longterm_flag :  1;//[0:0]
    REG32 ve_mvp_l1_longterm_flag :  1;//[1:1]
    REG32 ve_col_l0_longterm_flag :  1;//[2:2]
    REG32 ve_col_l1_longterm_flag :  1;//[3:3]
    REG32       ve_num_ref_idx_l1 :  2;//[5:4]
    REG32       ve_num_ref_idx_l0 :  2;//[7:6]
    REG32                   rsvd0 : 24;//[31:8]
}t_reg_vcpi_mvp_pic_info;

typedef struct t_reg_vcpi_qpg_info0
{
    REG32               ve_rc_en :  1;//[0:0]
    REG32             ve_rc_init :  1;//[1:1]
    REG32             ve_rc_mode :  1;//[2:2]
    REG32         ve_sep_mode_en :  1;//[3:3]
    REG32          ve_qpg_bim_en :  1;//[4:4]
    REG32           ve_qpg_aq_en :  1;//[5:5]
    REG32        ve_qpg_bimaq_en :  1;//[6:6]
    REG32        ve_change_qp_en :  1;//[7:7]
    REG32    ve_change_lambda_en :  1;//[8:8]
    REG32         ve_frame_level :  2;//[10:9]
    REG32 ve_num_of_lcu_inreg_m1 : 11;//[21:11]
    REG32     ve_rc_max_dqp_step :  5;//[26:22]
    REG32    ve_rc_max_dqp_range :  5;//[31:27]
}t_reg_vcpi_qpg_info0;

typedef struct t_reg_vcpi_qpg_info1
{
    REG32      ve_bitrate_window :  7;//[6:0]
    REG32              ve_qp_min :  6;//[12:7]
    REG32              ve_qp_max :  6;//[18:13]
    REG32              ve_frm_qp :  6;//[24:19]
    REG32           ve_ba_method :  2;//[26:25]
    REG32 ve_rc_force_bitrate_en :  1;//[27:27]
    REG32                  rsvd0 :  4;//[31:28]
}t_reg_vcpi_qpg_info1;

typedef struct t_reg_vcpi_qpg_avg_info0
{
    REG32 ve_qpg_avg_svar :  8;//[7:0]
    REG32  ve_qpg_avg_mv0 :  9;//[16:8]
    REG32  ve_qpg_avg_mv1 :  9;//[25:17]
    REG32           rsvd0 :  6;//[31:26]
}t_reg_vcpi_qpg_avg_info0;

typedef struct t_reg_vcpi_qpg_avg_info1
{
    REG32 ve_qpg_avg_ssd0 : 20;//[19:0]
    REG32           rsvd0 : 12;//[31:20]
}t_reg_vcpi_qpg_avg_info1;

typedef struct t_reg_vcpi_qpg_avg_info2
{
    REG32 ve_qpg_avg_ssd1 : 20;//[19:0]
    REG32           rsvd0 : 12;//[31:20]
}t_reg_vcpi_qpg_avg_info2;

typedef struct t_reg_vcpi_qpg_avg_info3
{
    REG32 ve_qpg_avg_bim_err : 21;//[20:0]
    REG32              rsvd0 : 11;//[31:21]
}t_reg_vcpi_qpg_avg_info3;

typedef uint32_t t_reg_vcpi_rc_target_bits;
typedef uint32_t t_reg_vcpi_total_costintra0;
typedef uint32_t t_reg_vcpi_total_costintra1;
typedef uint32_t t_reg_vcpi_rc_lambda_min;
typedef uint32_t t_reg_vcpi_rc_lambda_max;
typedef uint32_t t_reg_vcpi_rc_lambda;
typedef uint32_t t_reg_vcpi_rc_beta_min;
typedef uint32_t t_reg_vcpi_rc_beta_max;
typedef uint32_t t_reg_vcpi_rc_beta;
typedef uint32_t t_reg_vcpi_rc_alpha_min;
typedef uint32_t t_reg_vcpi_rc_alpha_max;
typedef uint32_t t_reg_vcpi_rc_alpha;
typedef struct t_reg_vcpi_qpg_aq_gdr_para
{
    REG32  ve_aq_qp_min :  6;//[5:0]
    REG32         rsvd0 :  2;//[7:6]
    REG32  ve_aq_qp_max :  6;//[13:8]
    REG32         rsvd1 :  2;//[15:14]
    REG32    ve_gdr_pos :  8;//[23:16]
    REG32 ve_gdr_number :  8;//[31:24]
}t_reg_vcpi_qpg_aq_gdr_para;
typedef struct t_reg_vcpi_qpg_cyclic_info
{
    REG32      ve_qpg_cyclic_pos : 16;//[15:0]
    REG32 ve_qpg_cyclic_internal : 16;//[31:16]
}t_reg_vcpi_qpg_cyclic_info;

typedef uint32_t t_reg_vcpi_qpg_tt_bitweight;
typedef uint32_t t_reg_vcpi_qpg_max_frame_size;
typedef struct t_reg_vcpi_qpg_num_reg
{
    REG32 ve_qpg_num_reg : 16;//[15:0]
    REG32          rsvd0 : 16;//[31:16]
}t_reg_vcpi_qpg_num_reg;

typedef struct t_reg_vcpi_eop_ind
{
    REG32 ve_frame_eop :  1;//[0:0]
    REG32        rsvd0 : 31;//[31:1]
}t_reg_vcpi_eop_ind;

typedef struct t_reg_vcpi
{
    t_reg_vcpi_pic_info0                                   VCPI_PIC_INFO0;
    t_reg_vcpi_pic_size                                     VCPI_PIC_SIZE;
    t_reg_ve_tile_info                                       VE_TILE_INFO;
    t_reg_vcpi_pps_info0                                   VCPI_PPS_INFO0;
    t_reg_vcpi_pps_info1                                   VCPI_PPS_INFO1;
    t_reg_vcpi_clk_force0                                 VCPI_CLK_FORCE0;
    t_reg_vcpi_clk_force1                                 VCPI_CLK_FORCE1;
    t_reg_vcpi_slice_split_cfg                       VCPI_SLICE_SPLIT_CFG;
    t_reg_vcpi_me_info0                                     VCPI_ME_INFO0;
    t_reg_vcpi_me_info1                                     VCPI_ME_INFO1;
    t_reg_vcpi_me_info2                                     VCPI_ME_INFO2;
    t_reg_vcpi_me_mvlimit                                 VCPI_ME_MVLIMIT;
    t_reg_vcpi_me_wight                                     VCPI_ME_WIGHT;
    t_reg_vcpi_me_cu_en                                     VCPI_ME_CU_EN;
    t_reg_vcpi_me_cst0                                       VCPI_ME_CST0;
    t_reg_vcpi_me_cst1                                       VCPI_ME_CST1;
    t_reg_vcpi_me_cst2                                       VCPI_ME_CST2;
    t_reg_vcpi_me_ipenalty                               VCPI_ME_IPENALTY;
    t_reg_vcpi_me_cost_penalty                       VCPI_ME_COST_PENALTY;
    t_reg_vcpi_me_zero_cut                               VCPI_ME_ZERO_CUT;
    t_reg_vcpi_me_tmvpenalty                           VCPI_ME_TMVPENALTY;
    t_reg_vcpi_src_pic_size                             VCPI_SRC_PIC_SIZE;
    t_reg_vcpi_src_format                                 VCPI_SRC_FORMAT;
    t_reg_vcpi_src_ctrl_info                           VCPI_SRC_CTRL_INFO;
    t_reg_vcpi_src_uv_pad_value                     VCPI_SRC_UV_PAD_VALUE;
    t_reg_vcpi_src_rotation                             VCPI_SRC_ROTATION;
    t_reg_vcpi_mctf_tf_threshold                   VCPI_MCTF_TF_THRESHOLD;
    t_reg_vcpi_mctf_tf_weight1                       VCPI_MCTF_TF_WEIGHT1;
    t_reg_vcpi_mctf_tf_weight2                       VCPI_MCTF_TF_WEIGHT2;
    t_reg_vcpi_src_aq_pre_frm_avg_svar       VCPI_SRC_AQ_PRE_FRM_AVG_SVAR;
    t_reg_vcpi_src_aq_stripe_qpdelta_para VCPI_SRC_AQ_STRIPE_QPDELTA_PARA;
    t_reg_vcpi_src_sa_th                                   VCPI_SRC_SA_TH;
    t_reg_vcpi_src_bim_aq_th                           VCPI_SRC_BIM_AQ_TH;
    t_reg_vcpi_src_bim_aq_weight                   VCPI_SRC_BIM_AQ_WEIGHT;
    t_reg_vcpi_src_osd_mosaic_ctrl               VCPI_SRC_OSD_MOSAIC_CTRL;
    t_reg_vcpi_src_osd_0_color_param           VCPI_SRC_OSD_0_COLOR_PARAM;
    t_reg_vcpi_src_osd_1_color_param           VCPI_SRC_OSD_1_COLOR_PARAM;
    t_reg_vcpi_src_osd_0_start_pos               VCPI_SRC_OSD_0_START_POS;
    t_reg_vcpi_src_osd_1_start_pos               VCPI_SRC_OSD_1_START_POS;
    t_reg_vcpi_src_osd_0_size                         VCPI_SRC_OSD_0_SIZE;
    t_reg_vcpi_src_osd_1_size                         VCPI_SRC_OSD_1_SIZE;
    t_reg_vcpi_src_osd0_addr_base_lo           VCPI_SRC_OSD0_ADDR_BASE_LO;
    t_reg_vcpi_src_osd0_addr_base_hi           VCPI_SRC_OSD0_ADDR_BASE_HI;
    t_reg_vcpi_src_osd1_addr_base_lo           VCPI_SRC_OSD1_ADDR_BASE_LO;
    t_reg_vcpi_src_osd1_addr_base_hi           VCPI_SRC_OSD1_ADDR_BASE_HI;
    t_reg_vcpi_src_osd_stride                         VCPI_SRC_OSD_STRIDE;
    t_reg_vcpi_src_mosaic_pos                     VCPI_SRC_MOSAIC_POS[16];
    t_reg_vcpi_src_mosaic_size                   VCPI_SRC_MOSAIC_SIZE[16];
    t_reg_vcpi_roi_enable                                 VCPI_ROI_ENABLE;
    t_reg_vcpi_roi_pos                                   VCPI_ROI_POS[16];
    t_reg_vcpi_roi_size                                 VCPI_ROI_SIZE[16];
    t_reg_vcpi_roi_value                               VCPI_ROI_VALUE[16];
    t_reg_vcpi_fbc_lut_base_lo                       VCPI_FBC_LUT_BASE_LO;
    t_reg_vcpi_fbc_lut_base_hi                       VCPI_FBC_LUT_BASE_HI;
    t_reg_vcpi_fbc_slice_buf_base_lo           VCPI_FBC_SLICE_BUF_BASE_LO;
    t_reg_vcpi_fbc_slice_buf_base_hi           VCPI_FBC_SLICE_BUF_BASE_HI;
    t_reg_vcpi_fbc_slice_ring_offset           VCPI_FBC_SLICE_RING_OFFSET;
    t_reg_vcpi_fbc_slice_stride                     VCPI_FBC_SLICE_STRIDE;
    t_reg_vcpi_fbc_slice_buf_size                 VCPI_FBC_SLICE_BUF_SIZE;
    t_reg_vcpi_ref0_lut_base_lo                     VCPI_REF0_LUT_BASE_LO;
    t_reg_vcpi_ref0_lut_base_hi                     VCPI_REF0_LUT_BASE_HI;
    t_reg_vcpi_ref1_lut_base_lo                     VCPI_REF1_LUT_BASE_LO;
    t_reg_vcpi_ref1_lut_base_hi                     VCPI_REF1_LUT_BASE_HI;
    t_reg_vcpi_ref0_slice_base_lo                 VCPI_REF0_SLICE_BASE_LO;
    t_reg_vcpi_ref0_slice_base_hi                 VCPI_REF0_SLICE_BASE_HI;
    t_reg_vcpi_ref1_slice_base_lo                 VCPI_REF1_SLICE_BASE_LO;
    t_reg_vcpi_ref1_slice_base_hi                 VCPI_REF1_SLICE_BASE_HI;
    t_reg_vcpi_rgb2yuv_coef0                           VCPI_RGB2YUV_COEF0;
    t_reg_vcpi_rgb2yuv_coef1                           VCPI_RGB2YUV_COEF1;
    t_reg_vcpi_rgb2yuv_coef2                           VCPI_RGB2YUV_COEF2;
    t_reg_vcpi_rgb2yuv_coef3                           VCPI_RGB2YUV_COEF3;
    t_reg_vcpi_rgb2yuv_coef4                           VCPI_RGB2YUV_COEF4;
    t_reg_vcpi_rgb2yuv_coef5                           VCPI_RGB2YUV_COEF5;
    t_reg_vcpi_rgb2yuv_coef6                           VCPI_RGB2YUV_COEF6;
    t_reg_vcpi_rgb2yuv_coef7                           VCPI_RGB2YUV_COEF7;
    t_reg_vcpi_rgb2yuv_coef8                           VCPI_RGB2YUV_COEF8;
    t_reg_vcpi_rgb2yuv_yuv_val_range           VCPI_RGB2YUV_YUV_VAL_RANGE;
    t_reg_vcpi_rgb2yuv_rgb_val_range           VCPI_RGB2YUV_RGB_VAL_RANGE;
    t_reg_vcpi_src_ext_base_lo_0                   VCPI_SRC_EXT_BASE_LO_0;
    t_reg_vcpi_src_ext_base_hi_0                   VCPI_SRC_EXT_BASE_HI_0;
    t_reg_vcpi_src_ext_base_lo_1                   VCPI_SRC_EXT_BASE_LO_1;
    t_reg_vcpi_src_ext_base_hi_1                   VCPI_SRC_EXT_BASE_HI_1;
    t_reg_vcpi_src_ext_base_lo_2                   VCPI_SRC_EXT_BASE_LO_2;
    t_reg_vcpi_src_ext_base_hi_2                   VCPI_SRC_EXT_BASE_HI_2;
    t_reg_vcpi_src_pre_ext_base_lo_0           VCPI_SRC_PRE_EXT_BASE_LO_0;
    t_reg_vcpi_src_pre_ext_base_hi_0           VCPI_SRC_PRE_EXT_BASE_HI_0;
    t_reg_vcpi_src_pre_ext_base_lo_1           VCPI_SRC_PRE_EXT_BASE_LO_1;
    t_reg_vcpi_src_pre_ext_base_hi_1           VCPI_SRC_PRE_EXT_BASE_HI_1;
    t_reg_vcpi_src_pre_ext_base_lo_2           VCPI_SRC_PRE_EXT_BASE_LO_2;
    t_reg_vcpi_src_pre_ext_base_hi_2           VCPI_SRC_PRE_EXT_BASE_HI_2;
    t_reg_vcpi_src_post_ext_base_lo_0         VCPI_SRC_POST_EXT_BASE_LO_0;
    t_reg_vcpi_src_post_ext_base_hi_0         VCPI_SRC_POST_EXT_BASE_HI_0;
    t_reg_vcpi_src_post_ext_base_lo_1         VCPI_SRC_POST_EXT_BASE_LO_1;
    t_reg_vcpi_src_post_ext_base_hi_1         VCPI_SRC_POST_EXT_BASE_HI_1;
    t_reg_vcpi_src_post_ext_base_lo_2         VCPI_SRC_POST_EXT_BASE_LO_2;
    t_reg_vcpi_src_post_ext_base_hi_2         VCPI_SRC_POST_EXT_BASE_HI_2;
    t_reg_vcpi_pmest_base_lo                           VCPI_PMEST_BASE_LO;
    t_reg_vcpi_pmest_base_hi                           VCPI_PMEST_BASE_HI;
    t_reg_vcpi_ds_load_base_lo_0                   VCPI_DS_LOAD_BASE_LO_0;
    t_reg_vcpi_ds_load_base_hi_0                   VCPI_DS_LOAD_BASE_HI_0;
    t_reg_vcpi_ds_load_base_lo_1                   VCPI_DS_LOAD_BASE_LO_1;
    t_reg_vcpi_ds_load_base_hi_1                   VCPI_DS_LOAD_BASE_HI_1;
    t_reg_vcpi_src_stride_0                             VCPI_SRC_STRIDE_0;
    t_reg_vcpi_src_stride_1                             VCPI_SRC_STRIDE_1;
    t_reg_vcpi_src_stride_2                             VCPI_SRC_STRIDE_2;
    t_reg_vcpi_src_pre_stride_0                     VCPI_SRC_PRE_STRIDE_0;
    t_reg_vcpi_src_pre_stride_1                     VCPI_SRC_PRE_STRIDE_1;
    t_reg_vcpi_src_pre_stride_2                     VCPI_SRC_PRE_STRIDE_2;
    t_reg_vcpi_src_post_stride_0                   VCPI_SRC_POST_STRIDE_0;
    t_reg_vcpi_src_post_stride_1                   VCPI_SRC_POST_STRIDE_1;
    t_reg_vcpi_src_post_stride_2                   VCPI_SRC_POST_STRIDE_2;
    t_reg_vcpi_pmest_stride                             VCPI_PMEST_STRIDE;
    t_reg_vcpi_downsample_stride_0               VCPI_DOWNSAMPLE_STRIDE_0;
    t_reg_vcpi_downsample_stride_1               VCPI_DOWNSAMPLE_STRIDE_1;
    t_reg_vcpi_pks_buf0_addr_lo                     VCPI_PKS_BUF0_ADDR_LO;
    t_reg_vcpi_pks_buf0_addr_hi                     VCPI_PKS_BUF0_ADDR_HI;
    t_reg_vcpi_pks_buf0_len                             VCPI_PKS_BUF0_LEN;
    t_reg_vcpi_pks_buf1_addr_lo                     VCPI_PKS_BUF1_ADDR_LO;
    t_reg_vcpi_pks_buf1_addr_hi                     VCPI_PKS_BUF1_ADDR_HI;
    t_reg_vcpi_pks_buf1_len                             VCPI_PKS_BUF1_LEN;
    t_reg_vcpi_pks_buf2_addr_lo                     VCPI_PKS_BUF2_ADDR_LO;
    t_reg_vcpi_pks_buf2_addr_hi                     VCPI_PKS_BUF2_ADDR_HI;
    t_reg_vcpi_pks_buf2_len                             VCPI_PKS_BUF2_LEN;
    t_reg_vcpi_pks_buf3_addr_lo                     VCPI_PKS_BUF3_ADDR_LO;
    t_reg_vcpi_pks_buf3_addr_hi                     VCPI_PKS_BUF3_ADDR_HI;
    t_reg_vcpi_pks_buf3_len                             VCPI_PKS_BUF3_LEN;
    t_reg_vcpi_bnd_buf_size                             VCPI_BND_BUF_SIZE;
    t_reg_vcpi_bnd_row_addr_lo                       VCPI_BND_ROW_ADDR_LO;
    t_reg_vcpi_bnd_row_addr_hi                       VCPI_BND_ROW_ADDR_HI;
    t_reg_vcpi_col_load_addr_lo                     VCPI_COL_LOAD_ADDR_LO;
    t_reg_vcpi_col_load_addr_hi                     VCPI_COL_LOAD_ADDR_HI;
    t_reg_vcpi_col_store_addr_lo                   VCPI_COL_STORE_ADDR_LO;
    t_reg_vcpi_col_store_addr_hi                   VCPI_COL_STORE_ADDR_HI;
    t_reg_vcpi_col_total_word                         VCPI_COL_TOTAL_WORD;
    t_reg_vcpi_ds_load_addr_lo                       VCPI_DS_LOAD_ADDR_LO;
    t_reg_vcpi_ds_load_addr_hi                       VCPI_DS_LOAD_ADDR_HI;
    t_reg_vcpi_ds_store_addr_lo                     VCPI_DS_STORE_ADDR_LO;
    t_reg_vcpi_ds_store_addr_hi                     VCPI_DS_STORE_ADDR_HI;
    t_reg_vcpi_qpg_load_addr_lo                     VCPI_QPG_LOAD_ADDR_LO;
    t_reg_vcpi_qpg_load_addr_hi                     VCPI_QPG_LOAD_ADDR_HI;
    t_reg_vcpi_bitbuf_addr_lo                         VCPI_BITBUF_ADDR_LO;
    t_reg_vcpi_bitbuf_addr_hi                         VCPI_BITBUF_ADDR_HI;
    t_reg_vcpi_bitbuf_len                                 VCPI_BITBUF_LEN;
    t_reg_vcpi_bus_ctrl                                     VCPI_BUS_CTRL;
    t_reg_vcpi_read_ostd_num                           VCPI_READ_OSTD_NUM;
    t_reg_vcpi_write_ostd_num                         VCPI_WRITE_OSTD_NUM;
    t_reg_vcpi_mmu_chn_bypass                         VCPI_MMU_CHN_BYPASS;
    t_reg_vcpi_mmu_chn_prio                             VCPI_MMU_CHN_PRIO;
    t_reg_vcpi_mmu_evtsel0                               VCPI_MMU_EVTSEL0;
    t_reg_vcpi_mmu_evtsel1                               VCPI_MMU_EVTSEL1;
    t_reg_vcpi_fro_dc_0                                     VCPI_FRO_DC_0;
    t_reg_vcpi_fro_dc_1                                     VCPI_FRO_DC_1;
    t_reg_vcpi_fro_dc_2                                     VCPI_FRO_DC_2;
    t_reg_vcpi_fro_dc_3                                     VCPI_FRO_DC_3;
    t_reg_vcpi_fro_dc_4                                     VCPI_FRO_DC_4;
    t_reg_vcpi_fro_dc_5                                     VCPI_FRO_DC_5;
    t_reg_vcpi_fro_ac_0                                     VCPI_FRO_AC_0;
    t_reg_vcpi_fro_ac_1                                     VCPI_FRO_AC_1;
    t_reg_vcpi_fro_ac_2                                     VCPI_FRO_AC_2;
    t_reg_vcpi_fro_ac_3                                     VCPI_FRO_AC_3;
    t_reg_vcpi_fro_ac_4                                     VCPI_FRO_AC_4;
    t_reg_vcpi_fro_ac_5                                     VCPI_FRO_AC_5;
    t_reg_vcpi_fro_st_0                                     VCPI_FRO_ST_0;
    t_reg_vcpi_fro_st_1                                     VCPI_FRO_ST_1;
    t_reg_vcpi_fro_st_2                                     VCPI_FRO_ST_2;
    t_reg_vcpi_fro_st_3                                     VCPI_FRO_ST_3;
    t_reg_vcpi_fro_st_4                                     VCPI_FRO_ST_4;
    t_reg_vcpi_fro_st_5                                     VCPI_FRO_ST_5;
    t_reg_vcpi_fro_mx_0                                     VCPI_FRO_MX_0;
    t_reg_vcpi_fro_mx_1                                     VCPI_FRO_MX_1;
    t_reg_vcpi_fro_mx_2                                     VCPI_FRO_MX_2;
    t_reg_vcpi_fro_mx_3                                     VCPI_FRO_MX_3;
    t_reg_vcpi_fro_mx_4                                     VCPI_FRO_MX_4;
    t_reg_vcpi_fro_mx_5                                     VCPI_FRO_MX_5;
    t_reg_vcpi_qpg_lambda                             VCPI_QPG_LAMBDA[52];
    t_reg_vcpi_sao_lambda_group                 VCPI_SAO_LAMBDA_GROUP[26];
    t_reg_vcpi_lambda_scaling                         VCPI_LAMBDA_SCALING;
    t_reg_vcpi_lambda_sqrt_scaling               VCPI_LAMBDA_SQRT_SCALING;
    t_reg_vcpi_force_period_intra                 VCPI_FORCE_PERIOD_INTRA;
    t_reg_vcpi_tq_qbias                                     VCPI_TQ_QBIAS;
    t_reg_vcpi_mvp_poc                                       VCPI_MVP_POC;
    t_reg_vcpi_mvp_ref_poc                               VCPI_MVP_REF_POC;
    t_reg_vcpi_mvp_colref_poc                         VCPI_MVP_COLREF_POC;
    t_reg_vcpi_mvp_pic_info                             VCPI_MVP_PIC_INFO;
    t_reg_vcpi_qpg_info0                                   VCPI_QPG_INFO0;
    t_reg_vcpi_qpg_info1                                   VCPI_QPG_INFO1;
    t_reg_vcpi_qpg_avg_info0                           VCPI_QPG_AVG_INFO0;
    t_reg_vcpi_qpg_avg_info1                           VCPI_QPG_AVG_INFO1;
    t_reg_vcpi_qpg_avg_info2                           VCPI_QPG_AVG_INFO2;
    t_reg_vcpi_qpg_avg_info3                           VCPI_QPG_AVG_INFO3;
    t_reg_vcpi_rc_target_bits                         VCPI_RC_TARGET_BITS;
    t_reg_vcpi_total_costintra0                     VCPI_TOTAL_COSTINTRA0;
    t_reg_vcpi_total_costintra1                     VCPI_TOTAL_COSTINTRA1;
    t_reg_vcpi_rc_lambda_min                           VCPI_RC_LAMBDA_MIN;
    t_reg_vcpi_rc_lambda_max                           VCPI_RC_LAMBDA_MAX;
    t_reg_vcpi_rc_lambda                                   VCPI_RC_LAMBDA;
    t_reg_vcpi_rc_beta_min                               VCPI_RC_BETA_MIN;
    t_reg_vcpi_rc_beta_max                               VCPI_RC_BETA_MAX;
    t_reg_vcpi_rc_beta                                       VCPI_RC_BETA;
    t_reg_vcpi_rc_alpha_min                             VCPI_RC_ALPHA_MIN;
    t_reg_vcpi_rc_alpha_max                             VCPI_RC_ALPHA_MAX;
    t_reg_vcpi_rc_alpha                                     VCPI_RC_ALPHA;
    t_reg_vcpi_qpg_aq_gdr_para                       VCPI_QPG_AQ_GDR_PARA;
    t_reg_vcpi_qpg_cyclic_info                       VCPI_QPG_CYCLIC_INFO;
    t_reg_vcpi_qpg_tt_bitweight                     VCPI_QPG_TT_BITWEIGHT;
    t_reg_vcpi_qpg_max_frame_size                 VCPI_QPG_MAX_FRAME_SIZE;
    t_reg_vcpi_qpg_num_reg                               VCPI_QPG_NUM_REG;
    t_reg_vcpi_eop_ind                                       VCPI_EOP_IND;
} t_reg_vcpi;
typedef struct t_reg_vcpi_restart_config
{
    REG32        ve_ri_enable :  1;//[0:0]
    REG32 ve_restart_interval : 16;//[16:1]
    REG32               rsvd0 : 15;//[31:17]
}t_reg_vcpi_restart_config;

typedef uint32_t t_reg_vcpi_hufftlb_addr_lo;

typedef uint32_t t_reg_vcpi_hufftlb_addr_hi;

typedef struct t_reg_vcpi_luma_multipara
{
    REG32 ve_luma_multipara0 : 16;//[15:0]
    REG32 ve_luma_multipara1 : 16;//[31:16]
}t_reg_vcpi_luma_multipara;

typedef struct t_reg_vcpi_luma_qrc
{
    REG32 ve_luma_rcpara0 : 16;//[15:0]
    REG32 ve_luma_rcpara1 : 16;//[31:16]
}t_reg_vcpi_luma_qrc;

typedef struct t_reg_vcpi_chma_multipara
{
    REG32 ve_chma_multipara0 : 16;//[15:0]
    REG32 ve_chma_multipara1 : 16;//[31:16]
}t_reg_vcpi_chma_multipara;

typedef struct t_reg_vcpi_chma_qrc
{
    REG32 ve_chma_rcpara0 : 16;//[15:0]
    REG32 ve_chma_rcpara1 : 16;//[31:16]
}t_reg_vcpi_chma_qrc;

typedef struct t_reg_vcpi_jpge
{
    t_reg_vcpi_restart_config      VCPI_RESTART_CONFIG;
    t_reg_vcpi_hufftlb_addr_lo    VCPI_HUFFTLB_ADDR_LO;
    t_reg_vcpi_hufftlb_addr_hi    VCPI_HUFFTLB_ADDR_HI;
    t_reg_vcpi_luma_multipara  VCPI_LUMA_MULTIPARA[32];
    t_reg_vcpi_luma_qrc              VCPI_LUMA_QRC[32];
    t_reg_vcpi_chma_multipara  VCPI_CHMA_MULTIPARA[32];
    t_reg_vcpi_chma_qrc              VCPI_CHMA_QRC[32];
} t_reg_vcpi_jpge;
#define REG_VCPI_JPGE_OFFSET_IN_VCPI    (__builtin_offsetof (t_reg_vcpi, VCPI_FRO_DC_0))
//help for reg JPGE  access
#define REG_JPGE(p_vcpi)           (*((t_reg_vcpi_jpge*)((REG32*)p_vcpi + (REG_VCPI_JPGE_OFFSET_IN_VCPI/4))))
#endif //!__EMUL_INCLUDE__REG_DATA_H__
