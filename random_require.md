需求：
1. 将reg_data.h文件中的t_reg_vcpi结构体中的成员变量根据位宽来进行随机参数生成。
2. 先随机VCPI_PIC_INFO0和VCPI_PIC_SIZE这两个结构体成员，其中图像宽高要2对齐，分辨率不要超过1080p。
3. 随机生成的参数以cfg的形式呈现。
3.1 cfg文件格式示例：
```
    #======== VCPI_PIC_INFO0 ================
    ve_frame_type                    : 1
    ve_protocol                      : 3
    ve_chroma_format                 : 3
    ve_enc_bitdepth                  : 0
    ve_tmv_en                        : 1
    ve_log2parmrglevel               : 2
    ve_nobackwardpredflag            : 0
    ve_collocated_l0_flag            : 0
    ve_direct_spatial_mv_pred_flag   : 1
    ve_direct_8x8_inference_flag     : 1
    ve_constrain_intra               : 1
    ve_strong_intra_smooth_en        : 0
    ve_dbl_bypass_en                 : 1
    ve_sao_luma_en                   : 0
    ve_sao_chma_en                   : 0
    ve_fbc_en                        : 0
    ve_recst_disable                 : 0
    ve_recst_ringbuf_en              : 1

    #======== VCPI_PIC_SIZE =================
    ve_pic_height                    : 578
    ve_pic_width                     : 376
