#!/usr/bin/env python3

"""
This file is there in order to avoid an register access needing another register access somewhere else.
The settings here are a lookup table and the assumption is that the firmware set up those values and left them at that--so we don't need to look them up in hardware.
"""

""" Ron:
0x1110_1018:0x00000000
0x1120_1018:0x00000000
0x1130_1018:0x00000000
0x1140_1018:0x00000000
0x1110_2018:0x00000000
0x1120_2018:0x00000000
0x1130_2018:0x00000000
0x1140_2018:0x00000000
0x1110_3018:0x00000000
0x1120_3018:0x00000000
0x1130_3018:0x00000000
0x1140_3018:0x00000000
0x1110_4018:0x00000000
0x1120_4018:0x00000000
0x1130_4018:0x00000000
0x1140_4018:0x00000000
0x1110_5018:0x00000000
0x1120_5018:0x00000000
0x1130_5018:0x00000000
0x1140_5018:0x00000000
0x1110_6018:0x00000000
0x1120_6018:0x00000000
0x1130_6018:0x00000000
0x1140_6018:0x00000000
0x1110_7018:0x00000000
0x1120_7018:0x00000000
0x1130_7018:0x00000000
0x1140_7018:0x00000000
"""

settings = [
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio0_aliasSMN; IOHCMISC0x000002F4; IOHCMISC0=13B1_0000h
#   Ron: 0x13B1_02F4:0x00000000
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio0_aliasSMN; IOHCMISC0x000002F0; IOHCMISC0=13B1_0000h
#   Ron: 0x13B1_02F0:0xc9280001
("{IOHC::IOAPIC_BASE_ADDR_HI_nbio0_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio0_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}", "c928_0000h"),
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio1_aliasSMN; IOHCMISC1x000002F4; IOHCMISC1=13C1_0000h
#   Ron: 0x13C1_02F4:0x00000000
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio1_aliasSMN; IOHCMISC1x000002F0; IOHCMISC1=13C1_0000h
#   Ron: 0x13C1_02F0:0xf4180001
("{IOHC::IOAPIC_BASE_ADDR_HI_nbio1_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio1_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}", "f418_0000h"),
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio2_aliasSMN; IOHCMISC2x000002F4; IOHCMISC2=13D1_0000h
#   Ron: 0x13D1_02F4:0x00000000
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio2_aliasSMN; IOHCMISC2x000002F0; IOHCMISC2=13D1_0000h
#   Ron: 0x13D1_02F0:0xc8180001
("{IOHC::IOAPIC_BASE_ADDR_HI_nbio2_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio2_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}", "c818_0000h"),
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio3_aliasSMN; IOHCMISC3x000002F4; IOHCMISC3=13E1_0000h
#   Ron: 0x13E1_02F4:0x00000000
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio3_aliasSMN; IOHCMISC3x000002F0; IOHCMISC3=13E1_0000h
#   Ron: 0x13E1_02F0:0xf5180001
("{IOHC::IOAPIC_BASE_ADDR_HI_nbio3_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio3_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}", "f518_0001h"),

# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio0_aliasSMN; IOMMUL2BCFG0x00000044; IOMMUL2BCFG0=13F0_0000h.
#   Ron: 0x13F0_0044:0xc9200001
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio0_aliasSMN; IOMMUL2BCFG0x00000048; IOMMUL2BCFG0=13F0_0000h.
#   Ron: 0x13F0_0048:0x00000000
("{IOMMUL2::IOMMU_CAP_BASE_HI_nbio0_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio0_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}", "c920_0001h"), # No default available
# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio1_aliasSMN; IOMMUL2BCFG1x00000044; IOMMUL2BCFG1=1400_0000h.
#   Ron: 0x1400_0044:0xf4100001
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio1_aliasSMN; IOMMUL2BCFG1x00000048; IOMMUL2BCFG1=1400_0000h.
#   Ron: 0x1400_0048:0x00000000
("{IOMMUL2::IOMMU_CAP_BASE_HI_nbio1_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio1_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}", "f41_0000h"), # No default available
# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio2_aliasSMN; IOMMUL2BCFG2x00000044; IOMMUL2BCFG2=1410_0000h.
#   Ron: 0x1410_0044:0xc8100001
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio2_aliasSMN; IOMMUL2BCFG2x00000048; IOMMUL2BCFG2=1410_0000h.
#   Ron: 0x1410_0048:0x00000000
("{IOMMUL2::IOMMU_CAP_BASE_HI_nbio2_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio2_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}", "c810_0001h"), # No default available
# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio3_aliasSMN; IOMMUL2BCFG3x00000044; IOMMUL2BCFG3=1420_0000h.
#   Ron: 0x1420_0044:0xf5100001
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio3_aliasSMN; IOMMUL2BCFG3x00000048; IOMMUL2BCFG3=1420_0000h.
#   Ron: 0x1420_0048:0x00000000
("{IOMMUL2::IOMMU_CAP_BASE_HI_nbio3_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio3_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}", "f510_0001h"), # No default available

# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2) at _nbio0_instNBIF2_dev0_func2_aliasSMN; NBIO0NBIF2EPF2CFGx00000014; NBIO0NBIF2EPF2CFG=1094_2000h
#   Ron: 0x1094_2014:0x00000000
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_1) at _nbio0_instNBIF2_dev0_func2_aliasSMN; NBIO0NBIF2EPF2CFGx00000010; NBIO0NBIF2EPF2CFG=1094_2000h
#   Ron: 0x1094_2010:0x0000000c
("{NBIFEPFNCFG::BASE_ADDR_2_nbio0_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio0_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}", "0Ch"), # Default: 0Ch

# Note: Keep value in sync with BASE_ADDR_2 at _nbio1_instNBIF2_dev0_func2_aliasSMN; NBIO1NBIF2EPF2CFGx00000014; NBIO1NBIF2EPF2CFG=10A4_2000h
#   Ron: 0x10A4_2014:0x00000000
# Note: Keep value in sync with BASE_ADDR_1 at _nbio1_instNBIF2_dev0_func2_aliasSMN; NBIO1NBIF2EPF2CFGx00000010; NBIO1NBIF2EPF2CFG=10A4_2000h
#   Ron: 0x10A4_2010:0x0000000c
("{NBIFEPFNCFG::BASE_ADDR_2_nbio1_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio1_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}", "0Ch"), # Default: 0Ch

# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio2_instNBIF1_dev0_func3_aliasSMN; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF3CFGx00000014; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF[3:1]CFG=1074_[4:1]000h
#   Ron: 0x1074_1014:0x00000000
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio2_instNBIF1_dev0_func3_aliasSMN; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF3CFGx00000010; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF[3:1]CFG=1074_[4:1]000h
#   Ron: 0x1074_1010:0x00000000
#   Ron: 0x1074_2014:0x00000000
#   Ron: 0x1074_2010:0x00000000
#   Ron: 0x1074_3014:0x00000000
#   Ron: 0x1074_3010:0xc6000004
#   Ron: 0x1074_4014:0x00000000
#   Ron: 0x1074_4010:0x00000000
("{NBIFEPFNCFG:: BASE_ADDR_2 _nbio2_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ] , NBIFEPFNCFG:: BASE_ADDR_1 _nbio2_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ]}", "C6000004h"),
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio2_instNBIF2_dev0_func2_aliasSMN; NBIO2NBIF2EPF2CFGx00000014; NBIO2NBIF2EPF2CFG=10B4_2000h
#   Ron: 0x10B4_2014:0x00000000
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio2_instNBIF2_dev0_func2_aliasSMN; NBIO2NBIF2EPF2CFGx00000010; NBIO2NBIF2EPF2CFG=10B4_2000h
#   Ron: 0x10B4_2010:0x0000000c
("{NBIFEPFNCFG::BASE_ADDR_2_nbio2_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio2_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}", "0Ch"), # Default: 0Ch

# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio3_instNBIF1_dev0_func3_aliasSMN; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFGx00000014; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFG=1084_3000h
#   Ron: 0x1084_3014:0x00000000
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio3_instNBIF1_dev0_func3_aliasSMN; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFGx00000010; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFG=1084_3000h
#   Ron: 0x1084_3010:0xf8000004
("{NBIFEPFNCFG:: BASE_ADDR_2 _nbio3_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ] , NBIFEPFNCFG:: BASE_ADDR_1 _nbio3_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ]}", "f800_0004h"), # Default: 4h
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio3_instNBIF2_dev0_func2_aliasSMN; NBIO3NBIF2EPF2CFGx00000014; NBIO3NBIF2EPF2CFG=10C4_2000h
#   Ron: 0x10C4_2014:0x00000000
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio3_instNBIF2_dev0_func2_aliasSMN; NBIO3NBIF2EPF2CFGx00000010; NBIO3NBIF2EPF2CFG=10C4_2000h
#   Ron: 0x10C4_2010:0x0000000c
("{NBIFEPFNCFG::BASE_ADDR_2_nbio3_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio3_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}", "0Ch"), # Default: 0Ch

# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio0_aliasSMN; IOHCMISC0x00000044; IOHCMISC0=13B1_0000h
#   Ron: 0x13B1_0044:0x00000160
("IOHC::NB_BUS_NUM_CNTL_nbio0_aliasSMN[NB_BUS_NUM]", "160h"), # No default available
# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio1_aliasSMN; IOHCMISC1x00000044; IOHCMISC1=13C1_0000h
#   Ron: 0x13C1_0044:0x00000140
("IOHC::NB_BUS_NUM_CNTL_nbio1_aliasSMN[NB_BUS_NUM]", "140h"), # No default available
# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio2_aliasSMN; IOHCMISC2x00000044; IOHCMISC2=13D1_0000h
#   Ron: 0x13D1_0044:0x00000120
("IOHC::NB_BUS_NUM_CNTL_nbio2_aliasSMN[NB_BUS_NUM]", "120h"), # No default available
# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio3_aliasSMN; IOHCMISC3x00000044; IOHCMISC3=13E1_0000h
#   Ron: 0x13E1_0044:0x00000100
("IOHC::NB_BUS_NUM_CNTL_nbio3_aliasSMN[NB_BUS_NUM]", "100h"), # No default available

# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instNBIF0_dev0_aliasSMN; NBIO0NBIF0RCCFGx00000018; NBIO0NBIF0RCCFG=1010_0000h
#   Ron: 0x1010_0018:0x00636360
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]", "0063_6360h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instNBIF1_dev0_aliasSMN; NBIO0NBIF1RCCFGx00000018; NBIO0NBIF1RCCFG=1050_0000h
#   Ron: 0x1050_0018:0x00646460
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]", "64_6460h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF0_dev0_aliasSMN; NBIO1NBIF0RCCFGx00000018; NBIO1NBIF0RCCFG=1020_0000h
#   Ron: 0x1020_0018:0x00414140
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]", "41_4140h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF1_dev0_aliasSMN; NBIO1NBIF1RCCFGx00000018; NBIO1NBIF1RCCFG=1060_0000h
#   Ron: 0x1060_0018:0x00424240
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]", "42_4240h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF1_dev1_aliasSMN; NBIO1NBIF1RCCFGx00001018; NBIO1NBIF1RCCFG=1060_0000h
#   Ron: 0x1060_1018:0x00000000
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF1_dev1_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF1_dev2_aliasSMN; NBIO1NBIF1RCCFGx00002018; NBIO1NBIF1RCCFG=1060_0000h
#   Ron: 0x1060_2018:0x00000000
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF1_dev2_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF0_dev0_aliasSMN; NBIO2NBIF0RCCFGx00000018; NBIO2NBIF0RCCFG=1030_0000h
#   Ron: 0x1030_0018:0x00212120
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]", "21_2120h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF1_dev0_aliasSMN; NBIO2NBIF1RCCFGx00000018; NBIO2NBIF1RCCFG=1070_0000h
#   Ron: 0x1070_0018:0x00222220
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]", "22_2220h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF1_dev1_aliasSMN; NBIO2NBIF1RCCFGx00001018; NBIO2NBIF1RCCFG=1070_0000h
#   Ron: 0x1070_1018:0x00000000
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev1_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF1_dev2_aliasSMN; NBIO2NBIF1RCCFGx00002018; NBIO2NBIF1RCCFG=1070_0000h
#   Ron: 0x1070_2018:0x00000000
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev2_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instNBIF0_dev0_aliasSMN; NBIO3NBIF0RCCFGx00000018; NBIO3NBIF0RCCFG=1040_0000h
#   Ron: 0x1040_0018:0x00020200
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]", "2_0200h"), # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instNBIF1_dev0_aliasSMN; NBIO3NBIF1RCCFGx00000018; NBIO3NBIF1RCCFG=1080_0000h
#   Ron: 0x1080_0018:0x00030300
("NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]", "30300h"), # No default available

# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instNBIF2_aliasSMN; NBIO0NBIF2SWDSCFGx00000018; NBIO0NBIF2SWDSCFG=1090_0000h
#   Ron: 0x1090_0018:0x00000000
("NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instNBIF2_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF2_aliasSMN; NBIO1NBIF2SWDSCFGx00000018; NBIO1NBIF2SWDSCFG=10A0_0000h
#   Ron: 0x10A0_0018:0x00000000
("NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF2_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF2_aliasSMN; NBIO2NBIF2SWDSCFGx00000018; NBIO2NBIF2SWDSCFG=10B0_0000h
#   Ron: 0x10B0_0018:0x00000000
("NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF2_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instNBIF2_aliasSMN; NBIO3NBIF2SWDSCFGx00000018; NBIO3NBIF2SWDSCFG=10C0_0000h
#   Ron: 0x10C0_0018:0x00000000
("NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instNBIF2_aliasSMN[SECONDARY_BUS]", "0"), # No default available

# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instPCIE0_func[7:0]_aliasSMN; NBIO0PCIECORE0P[7:0]CFGx00000018; NBIO0PCIECORE0P[7:0]CFG=1110_[7:0]000h
#   Ron: 0x1110_0018:0x00000000
("PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instPCIE0_func0_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instPCIE0_func[7:0]_aliasSMN; NBIO1PCIECORE0P[7:0]CFGx00000018; NBIO1PCIECORE0P[7:0]CFG=1120_[7:0]000h
#   Ron: 0x1120_0018:0x00000000
("PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instPCIE0_func0_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instPCIE0_func[7:0]_aliasSMN; NBIO2PCIECORE0P[7:0]CFGx00000018; NBIO2PCIECORE0P[7:0]CFG=1130_[7:0]000h
#   Ron: 0x1130_0018:0x00000000
("PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instPCIE0_func0_aliasSMN[SECONDARY_BUS]", "0"), # No default available
# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instPCIE0_func[7:0]_aliasSMN; NBIO3PCIECORE0P[7:0]CFGx00000018; NBIO3PCIECORE0P[7:0]CFG=1140_[7:0]000h
#   Ron: 0x1140_0018:0x00010100
("PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instPCIE0_func0_aliasSMN[SECONDARY_BUS]", "1_0100h"), # No default available

("BXXD00F0x", "PCI{Bus: BXX, Device: 0x00, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM] or BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF?_dev?_aliasSMN[SECONDARY_BUS] or BXX=NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF2_aliasSMN[SECONDARY_BUS] or BXX=PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instPCIE0_func0_aliasSMN[PRIMARY_BUS] or BXX=PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instPCIE0_func0_aliasSMN[SECONDARY_BUS]; see IOHCMISC[0...3]x00000044 (IOHC::NB_BUS_NUM_CNTL) [_nbio[3:0]_aliasSMN; IOHCMISC[3:0]x00000044; IOHCMISC[3:0]=13[E:B]1_0000h]; default: disabled
("BXXD00F1x", "PCI{Bus: BXX, Device: 0x00, Function: 0x1}"), # BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF?_dev0_aliasSMN[SECONDARY_BUS] or BXX=NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF2_aliasSMN[SECONDARY_BUS]
("BXXD00F2x", "PCI{Bus: BXX, Device: 0x00, Function: 0x2}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM] or BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF?_dev0_aliasSMN[SECONDARY_BUS] or BXX=NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF2_aliasSMN[SECONDARY_BUS]
("BXXD00F3x", "PCI{Bus: BXX, Device: 0x00, Function: 0x3}"), # BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]
("BXXD00F4x", "PCI{Bus: BXX, Device: 0x00, Function: 0x4}"), # BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]
("BXXD01F0x", "PCI{Bus: BXX, Device: 0x01, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]; see IOHCMISC[0...3]x00000044 (IOHC::NB_BUS_NUM_CNTL) [_nbio[3:0]_aliasSMN; IOHCMISC[3:0]x00000044; IOHCMISC[3:0]=13[E:B]1_0000h]
("BXXD01F1x", "PCI{Bus: BXX, Device: 0x01, Function: 0x1}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD01F2x", "PCI{Bus: BXX, Device: 0x01, Function: 0x2}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD01F3x", "PCI{Bus: BXX, Device: 0x01, Function: 0x3}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD01F4x", "PCI{Bus: BXX, Device: 0x01, Function: 0x4}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD01F5x", "PCI{Bus: BXX, Device: 0x01, Function: 0x5}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD01F6x", "PCI{Bus: BXX, Device: 0x01, Function: 0x6}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD01F7x", "PCI{Bus: BXX, Device: 0x01, Function: 0x7}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD02F0x", "PCI{Bus: BXX, Device: 0x02, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD02F1x", "PCI{Bus: BXX, Device: 0x02, Function: 0x1}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD03F0x", "PCI{Bus: BXX, Device: 0x03, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD04F0x", "PCI{Bus: BXX, Device: 0x04, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD04F1x", "PCI{Bus: BXX, Device: 0x04, Function: 0x1}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD05F1x", "PCI{Bus: BXX, Device: 0x05, Function: 0x1}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio0_aliasSMN[NB_BUS_NUM]
("BXXD05F2x", "PCI{Bus: BXX, Device: 0x05, Function: 0x2}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio0_aliasSMN[NB_BUS_NUM]
("BXXD07F0x", "PCI{Bus: BXX, Device: 0x07, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD07F1x", "PCI{Bus: BXX, Device: 0x07, Function: 0x1}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD08F0x", "PCI{Bus: BXX, Device: 0x08, Function: 0x0}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD08F1x", "PCI{Bus: BXX, Device: 0x08, Function: 0x1}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD08F2x", "PCI{Bus: BXX, Device: 0x08, Function: 0x2}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
("BXXD08F3x", "PCI{Bus: BXX, Device: 0x08, Function: 0x3}"), # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]

("D00F0x", "e0000000h + "),
("D00F1x", "e0001000h + "),
("D00F2x", "e0002000h + "),
("D00F3x", "e0003000h + "),
("D00F4x", "e0004000h + "),

("D01F0x", "e0008000h + "),
("D01F1x", "e0009000h + "),
("D01F2x", "e000a000h + "),
("D01F3x", "e000b000h + "),
("D01F4x", "e000c000h + "),
("D01F5x", "e000d000h + "),
("D01F6x", "e000e000h + "),
("D01F7x", "e000f000h + "),

("D02F0x", "e0010000h + "),
("D02F1x", "e0011000h + "),
("D03F0x", "e0018000h + "),
("D04F0x", "e0020000h + "),
("D04F1x", "e0021000h + "),
("D05F1x", "e0029000h + "),
("D05F2x", "e002a000h + "),
("D07F0x", "e0038000h + "),
("D07F1x", "e0039000h + "),
("D08F0x", "e0040000h + "),
("D08F1x", "e0041000h + "),
("D08F2x", "e0042000h + "),
("D08F3x", "e0043000h + "),
("D14F3x", "e00a3000h + "),

("D18F0x", "e00c0000h + "),
("D18F1x", "e00c1000h + "),
("D18F2x", "e00c2000h + "),
("D18F3x", "e00c3000h + "),
("D18F4x", "e00c4000h + "),
("D18F5x", "e00c5000h + "),
("D18F6x", "e00c6000h + "),
("D18F7x", "e00c7000h + "),
# TODO: D19?

]

phase4_cluster_names = {
	"DF": { # Peripheral
		"DeviceVendorId0": "PCIInfo0",
		#"StatusCommand0": "PCIInfo0",
		"DeviceVendorId1": "PCIInfo1",
		"DeviceVendorId2": "PCIInfo2",
		"DeviceVendorId3": "PCIInfo3",
		"DeviceVendorId4": "PCIInfo4",
		"DeviceVendorId5": "PCIInfo5",
		"DeviceVendorId6": "PCIInfo6",
		"DeviceVendorId7": "PCIInfo7",

		#"CapabilitiesPtr0": "FCAC0",
		#"CapabilitiesPtr1": "FCAC1",
		#"CapabilitiesPtr2": "FCAC2",
		#"CapabilitiesPtr3": "FCAC3",
		#"CapabilitiesPtr4": "FCAC4",
		#"CapabilitiesPtr5": "FCAC5",
		#"CapabilitiesPtr6": "FCAC6",
		#"CapabilitiesPtr7": "FCAC7",

		"FabricConfigAccessControl": "FCAC", # Note: Dummy cluster name just to make it stop grouping the register in the previous cluster
		"FabricIndirectConfigAccessAddress_n0": "FICAA",
		"FabricIndirectConfigAccessDataLo_n0": "FICAD",
		#"FabricIndirectConfigAccessDataHi_n1": "FICAD", # AMD has this in an extra register table
	},
	"FCH_I2C": {
		"IC_CON_link0": "Connection_link0",
		"IC_SDA_SETUP_link0": "Connection_link0",
		"IC_COMP_PARAM_1_link0": "CompParam1_link0",

		"IC_CON_link1": "Connection_link1",
		"IC_SDA_SETUP_link1": "Connection_link1",
		"IC_COMP_PARAM_1_link1": "CompParam1_link1",

		"IC_CON_link2": "Connection_link2",
		"IC_SDA_SETUP_link2": "Connection_link2",
		"IC_COMP_PARAM_1_link2": "CompParam1_link2",

		"IC_CON_link3": "Connection_link3",
		"IC_SDA_SETUP_link3": "Connection_link3",
		"IC_COMP_PARAM_1_link3": "IC_CompParam1_link3",

		"IC_CON_link4": "Connection_link4",
		"IC_SDA_SETUP_link4": "Connection_link4",
		"IC_COMP_PARAM_1_link4": "CompParam1_link4",

		"IC_CON_link5": "Connection_link5",
		"IC_SDA_SETUP_link5": "Connection_link5",
		"IC_COMP_PARAM_1_link5": "CompParam1_link5",
	},
	"FCH_ITF_LPC": {
		"VENDOR_ID": "PCIInfo",
		"CAPABILITIES_POINTER": "CAPABILITIES_POINTER",
	},
	"IOHC": {
		"NB_VENDOR_ID_nbio3": "PCIInfo_nbio3",
		"NB_VENDOR_ID_nbio2": "PCIInfo_nbio2",
		"NB_VENDOR_ID_nbio1": "PCIInfo_nbio1",
		"NB_VENDOR_ID_nbio0": "PCIInfo_nbio0",
	},
	"IOMMUL2": {
		"IOMMU_VENDOR_ID_nbio3": "PCIInfo_nbio3",
		"IOMMU_VENDOR_ID_nbio2": "PCIInfo_nbio2",
		"IOMMU_VENDOR_ID_nbio1": "PCIInfo_nbio1",
		"IOMMU_VENDOR_ID_nbio0": "PCIInfo_nbio0",
	},
	"Core_X86_Msr": {
		"LVTLINT[%s]": "LVTLINT",
		"InterruptEnable0": "InterruptEnable0",
	},
	"FCH_AB": {
		"BIFCtl0": "BIFCtl0",
		"MiscCtl1": "MiscCtl1",
		"BLinkRABCtl": "BLinkRABCtl",
		"MiscCtl2": "MiscCtl2",
		"AL_Arb_Ctl": "AL_Arb_Ctl",
		"ALinkDmaPrefetchEn": "ALinkDmaPrefetchEn",
		"MiscCtl3": "MiscCtl3",
		"MsiCtl": "MsiCtl",
	},
	"FCH_SDP": {
		"DISCONNECT_CTL": "DisconnectCtl",
		"MISC_CTL": "MiscCtl",
	},
}
