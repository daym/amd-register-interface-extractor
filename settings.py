#!/usr/bin/env python3

"""
This file is there in order to avoid an register access needing another register access somewhere else.
The settings here are a lookup table and the assumption is that the firmware set up those values and thus
and left them at that--so we don't need to look them up.
"""

settings = {
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio0_aliasSMN; IOHCMISC0x000002F4; IOHCMISC0=13B1_0000h
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio0_aliasSMN; IOHCMISC0x000002F0; IOHCMISC0=13B1_0000h
"{IOHC::IOAPIC_BASE_ADDR_HI_nbio0_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio0_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}": "FEC0_0000h",
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio1_aliasSMN; IOHCMISC1x000002F4; IOHCMISC1=13C1_0000h
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio1_aliasSMN; IOHCMISC1x000002F0; IOHCMISC1=13C1_0000h
"{IOHC::IOAPIC_BASE_ADDR_HI_nbio1_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio1_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}": "FEC0_0000h",
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio2_aliasSMN; IOHCMISC2x000002F4; IOHCMISC2=13D1_0000h
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio2_aliasSMN; IOHCMISC2x000002F0; IOHCMISC2=13D1_0000h
"{IOHC::IOAPIC_BASE_ADDR_HI_nbio2_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio2_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}": "FEC0_0000h",
# Note: Keep value in sync with IOHCMISC?x000002F4(IOHC::IOAPIC_BASE_ADDR_HI); _nbio3_aliasSMN; IOHCMISC3x000002F4; IOHCMISC3=13E1_0000h
# Note: Keep value in sync with IOHCMISC?x000002F0(IOHC::IOAPIC_BASE_ADDR_LO); _nbio3_aliasSMN; IOHCMISC3x000002F0; IOHCMISC3=13E1_0000h
"{IOHC::IOAPIC_BASE_ADDR_HI_nbio3_aliasSMN[IOAPIC_BASE_ADDR_HI] , IOHC::IOAPIC_BASE_ADDR_LO_nbio3_aliasSMN[IOAPIC_BASE_ADDR_LO] , 00h}": "FEC0_0000h",

# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio0_aliasSMN; IOMMUL2BCFG0x00000044; IOMMUL2BCFG0=13F0_0000h.
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio0_aliasSMN; IOMMUL2BCFG0x00000048; IOMMUL2BCFG0=13F0_0000h.
"{IOMMUL2::IOMMU_CAP_BASE_HI_nbio0_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio0_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}": "FIXME", # No default available
# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio1_aliasSMN; IOMMUL2BCFG1x00000044; IOMMUL2BCFG1=1400_0000h.
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio1_aliasSMN; IOMMUL2BCFG1x00000048; IOMMUL2BCFG1=1400_0000h.
"{IOMMUL2::IOMMU_CAP_BASE_HI_nbio1_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio1_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}": "FIXME", # No default available
# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio2_aliasSMN; IOMMUL2BCFG2x00000044; IOMMUL2BCFG2=1410_0000h.
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio2_aliasSMN; IOMMUL2BCFG2x00000048; IOMMUL2BCFG2=1410_0000h.
"{IOMMUL2::IOMMU_CAP_BASE_HI_nbio2_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio2_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}": "FIXME", # No default available
# Note: Keep value in sync with IOMMU_BASE_ADDR_LO; _nbio3_aliasSMN; IOMMUL2BCFG3x00000044; IOMMUL2BCFG3=1420_0000h.
# Note: Keep value in sync with IOMMU_BASE_ADDR_HI; _nbio3_aliasSMN; IOMMUL2BCFG3x00000048; IOMMUL2BCFG3=1420_0000h.
"{IOMMUL2::IOMMU_CAP_BASE_HI_nbio3_aliasHOST[IOMMU_BASE_ADDR_HI] , IOMMUL2::IOMMU_CAP_BASE_LO_nbio3_aliasHOST[IOMMU_BASE_ADDR_LO] , 19'h0_0000}": "FIXME", # No default available

# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2) at _nbio0_instNBIF2_dev0_func2_aliasSMN; NBIO0NBIF2EPF2CFGx00000014; NBIO0NBIF2EPF2CFG=1094_2000h
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_1) at _nbio0_instNBIF2_dev0_func2_aliasSMN; NBIO0NBIF2EPF2CFGx00000010; NBIO0NBIF2EPF2CFG=1094_2000h
"{NBIFEPFNCFG::BASE_ADDR_2_nbio0_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio0_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}": "0Ch",

# Note: Keep value in sync with BASE_ADDR_2 at _nbio1_instNBIF2_dev0_func2_aliasSMN; NBIO1NBIF2EPF2CFGx00000014; NBIO1NBIF2EPF2CFG=10A4_2000h
# Note: Keep value in sync with BASE_ADDR_1 at _nbio1_instNBIF2_dev0_func2_aliasSMN; NBIO1NBIF2EPF2CFGx00000010; NBIO1NBIF2EPF2CFG=10A4_2000h
"{NBIFEPFNCFG::BASE_ADDR_2_nbio1_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio1_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}": "0Ch",
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio2_instNBIF1_dev0_func3_aliasSMN; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF3CFGx00000014; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF[3:1]CFG=1074_[4:1]000h
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio2_instNBIF1_dev0_func3_aliasSMN; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF3CFGx00000010; NBIO2NBIF1EPF4NCFG,NBIO2NBIF1EPF[3:1]CFG=1074_[4:1]000h
"{NBIFEPFNCFG:: BASE_ADDR_2 _nbio2_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ] , NBIFEPFNCFG:: BASE_ADDR_1 _nbio2_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ]}": "4h",
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio2_instNBIF2_dev0_func2_aliasSMN; NBIO2NBIF2EPF2CFGx00000014; NBIO2NBIF2EPF2CFG=10B4_2000h
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio2_instNBIF2_dev0_func2_aliasSMN; NBIO2NBIF2EPF2CFGx00000010; NBIO2NBIF2EPF2CFG=10B4_2000h
"{NBIFEPFNCFG::BASE_ADDR_2_nbio2_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio2_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}": "0Ch",
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio3_instNBIF1_dev0_func3_aliasSMN; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFGx00000014; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFG=1084_3000h
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio3_instNBIF1_dev0_func3_aliasSMN; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFGx00000010; NBIO3NBIF1EPF4NCFG,NBIO3NBIF1EPF3CFG=1084_3000h
"{NBIFEPFNCFG:: BASE_ADDR_2 _nbio3_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ] , NBIFEPFNCFG:: BASE_ADDR_1 _nbio3_instNBIF1_dev0_func3_aliasHOST[ BASE_ADDR ]}": "4h",
# Note: Keep value in sync with BXXD00F?x014 (NBIFEPFNCFG::BASE_ADDR_2); _nbio3_instNBIF2_dev0_func2_aliasSMN; NBIO3NBIF2EPF2CFGx00000014; NBIO3NBIF2EPF2CFG=10C4_2000h
# Note: Keep value in sync with BXXD00F?x010 (NBIFEPFNCFG::BASE_ADDR_1); _nbio3_instNBIF2_dev0_func2_aliasSMN; NBIO3NBIF2EPF2CFGx00000010; NBIO3NBIF2EPF2CFG=10C4_2000h
"{NBIFEPFNCFG::BASE_ADDR_2_nbio3_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR] , NBIFEPFNCFG::BASE_ADDR_1_nbio3_instNBIF2_dev0_func2_aliasHOST[BASE_ADDR]}": "0Ch",

# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio0_aliasSMN; IOHCMISC0x00000044; IOHCMISC0=13B1_0000h
"IOHC::NB_BUS_NUM_CNTL_nbio0_aliasSMN[NB_BUS_NUM]": "FIXME", # No default available
# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio1_aliasSMN; IOHCMISC1x00000044; IOHCMISC1=13C1_0000h
"IOHC::NB_BUS_NUM_CNTL_nbio1_aliasSMN[NB_BUS_NUM]": "FIXME", # No default available
# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio2_aliasSMN; IOHCMISC2x00000044; IOHCMISC2=13D1_0000h
"IOHC::NB_BUS_NUM_CNTL_nbio2_aliasSMN[NB_BUS_NUM]": "FIXME", # No default available
# Note: Keep value in sync with IOHCMISC?x00000044 (IOHC::NB_BUS_NUM_CNTL); _nbio3_aliasSMN; IOHCMISC3x00000044; IOHCMISC3=13E1_0000h
"IOHC::NB_BUS_NUM_CNTL_nbio3_aliasSMN[NB_BUS_NUM]": "FIXME", # No default available

# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instNBIF0_dev0_aliasSMN; NBIO0NBIF0RCCFGx00000018; NBIO0NBIF0RCCFG=1010_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instNBIF1_dev0_aliasSMN; NBIO0NBIF1RCCFGx00000018; NBIO0NBIF1RCCFG=1050_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF0_dev0_aliasSMN; NBIO1NBIF0RCCFGx00000018; NBIO1NBIF0RCCFG=1020_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF1_dev0_aliasSMN; NBIO1NBIF1RCCFGx00000018; NBIO1NBIF1RCCFG=1060_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF1_dev1_aliasSMN; NBIO1NBIF1RCCFGx00001018; NBIO1NBIF1RCCFG=1060_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF1_dev1_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF1_dev2_aliasSMN; NBIO1NBIF1RCCFGx00002018; NBIO1NBIF1RCCFG=1060_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF1_dev2_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF0_dev0_aliasSMN; NBIO2NBIF0RCCFGx00000018; NBIO2NBIF0RCCFG=1030_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF1_dev0_aliasSMN; NBIO2NBIF1RCCFGx00000018; NBIO2NBIF1RCCFG=1070_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF1_dev1_aliasSMN; NBIO2NBIF1RCCFGx00001018; NBIO2NBIF1RCCFG=1070_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev1_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF1_dev2_aliasSMN; NBIO2NBIF1RCCFGx00002018; NBIO2NBIF1RCCFG=1070_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev2_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instNBIF0_dev0_aliasSMN; NBIO3NBIF0RCCFGx00000018; NBIO3NBIF0RCCFG=1040_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instNBIF0_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (NBIFRCCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instNBIF1_dev0_aliasSMN; NBIO3NBIF1RCCFGx00000018; NBIO3NBIF1RCCFG=1080_0000h
"NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available

# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instNBIF2_aliasSMN; NBIO0NBIF2SWDSCFGx00000018; NBIO0NBIF2SWDSCFG=1090_0000h
"NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instNBIF2_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instNBIF2_aliasSMN; NBIO1NBIF2SWDSCFGx00000018; NBIO1NBIF2SWDSCFG=10A0_0000h
"NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instNBIF2_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instNBIF2_aliasSMN; NBIO2NBIF2SWDSCFGx00000018; NBIO2NBIF2SWDSCFG=10B0_0000h
"NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF2_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD00F0x018 (NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instNBIF2_aliasSMN; NBIO3NBIF2SWDSCFGx00000018; NBIO3NBIF2SWDSCFG=10C0_0000h
"NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instNBIF2_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available

# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio0_instPCIE0_func[7:0]_aliasSMN; NBIO0PCIECORE0P[7:0]CFGx00000018; NBIO0PCIECORE0P[7:0]CFG=1110_[7:0]000h
"PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio0_instPCIE0_func0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio1_instPCIE0_func[7:0]_aliasSMN; NBIO1PCIECORE0P[7:0]CFGx00000018; NBIO1PCIECORE0P[7:0]CFG=1120_[7:0]000h
"PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio1_instPCIE0_func0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio2_instPCIE0_func[7:0]_aliasSMN; NBIO2PCIECORE0P[7:0]CFGx00000018; NBIO2PCIECORE0P[7:0]CFG=1130_[7:0]000h
"PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instPCIE0_func0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available
# Note: Keep value in sync with BXXD0???x018 (PCIERCCFG::SUB_BUS_NUMBER_LATENCY); _nbio3_instPCIE0_func[7:0]_aliasSMN; NBIO3PCIECORE0P[7:0]CFGx00000018; NBIO3PCIECORE0P[7:0]CFG=1140_[7:0]000h
"PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio3_instPCIE0_func0_aliasSMN[SECONDARY_BUS]": "FIXME", # No default available

"D00F0x": "PCI{Bus: 0, Device: 0x00, Function: 0}",
"D00F1x": "PCI{Bus: 0, Device: 0x00, Function: 1}",
"D00F2x": "PCI{Bus: 0, Device: 0x00, Function: 2}",
"D00F3x": "PCI{Bus: 0, Device: 0x00, Function: 3}",
"D00F4x": "PCI{Bus: 0, Device: 0x00, Function: 4}",

"D01F0x": "PCI{Bus: 0, Device: 0x01, Function: 0}",
"D01F1x": "PCI{Bus: 0, Device: 0x01, Function: 1}",
"D01F2x": "PCI{Bus: 0, Device: 0x01, Function: 2}",
"D01F3x": "PCI{Bus: 0, Device: 0x01, Function: 3}",
"D01F4x": "PCI{Bus: 0, Device: 0x01, Function: 4}",
"D01F5x": "PCI{Bus: 0, Device: 0x01, Function: 5}",
"D01F6x": "PCI{Bus: 0, Device: 0x01, Function: 6}",
"D01F7x": "PCI{Bus: 0, Device: 0x01, Function: 7}",

"D02F0x": "PCI{Bus: 0, Device: 0x02, Function: 0}",
"D02F1x": "PCI{Bus: 0, Device: 0x02, Function: 1}",
"D03F0x": "PCI{Bus: 0, Device: 0x03, Function: 0}",
"D04F0x": "PCI{Bus: 0, Device: 0x04, Function: 0}",
"D04F1x": "PCI{Bus: 0, Device: 0x04, Function: 1}",
"D05F1x": "PCI{Bus: 0, Device: 0x05, Function: 1}",
"D05F2x": "PCI{Bus: 0, Device: 0x05, Function: 2}",
"D07F0x": "PCI{Bus: 0, Device: 0x07, Function: 0}",
"D07F1x": "PCI{Bus: 0, Device: 0x07, Function: 1}",
"D08F0x": "PCI{Bus: 0, Device: 0x08, Function: 0}",
"D08F1x": "PCI{Bus: 0, Device: 0x08, Function: 1}",
"D08F2x": "PCI{Bus: 0, Device: 0x08, Function: 2}",
"D08F3x": "PCI{Bus: 0, Device: 0x08, Function: 3}",
"D14F3x": "PCI{Bus: 0, Device: 0x14, Function: 3}",

"D18F0x": "PCI{Bus: 0, Device: 0x18, Function: 0}",
"D18F1x": "PCI{Bus: 0, Device: 0x18, Function: 1}",
"D18F2x": "PCI{Bus: 0, Device: 0x18, Function: 2}",
"D18F3x": "PCI{Bus: 0, Device: 0x18, Function: 3}",
"D18F4x": "PCI{Bus: 0, Device: 0x18, Function: 4}",
"D18F5x": "PCI{Bus: 0, Device: 0x18, Function: 5}",
"D18F6x": "PCI{Bus: 0, Device: 0x18, Function: 6}",
"D18F7x": "PCI{Bus: 0, Device: 0x18, Function: 7}",
# TODO: D19 ?

"BXXD00F0x": "PCI{Bus: BXX, Device: 0x00, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM] or BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF?_dev?_aliasSMN[SECONDARY_BUS] or BXX=NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF2_aliasSMN[SECONDARY_BUS] or BXX=PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instPCIE0_func0_aliasSMN[PRIMARY_BUS] or BXX=PCIERCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instPCIE0_func0_aliasSMN[SECONDARY_BUS]; see IOHCMISC[0...3]x00000044 (IOHC::NB_BUS_NUM_CNTL) [_nbio[3:0]_aliasSMN; IOHCMISC[3:0]x00000044; IOHCMISC[3:0]=13[E:B]1_0000h]; default: disabled
"BXXD00F1x": "PCI{Bus: BXX, Device: 0x00, Function: 0x1}", # BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF?_dev0_aliasSMN[SECONDARY_BUS] or BXX=NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF2_aliasSMN[SECONDARY_BUS]
"BXXD00F2x": "PCI{Bus: BXX, Device: 0x00, Function: 0x2}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM] or BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF?_dev0_aliasSMN[SECONDARY_BUS] or BXX=NBIFSWDSCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF2_aliasSMN[SECONDARY_BUS]
"BXXD00F3x": "PCI{Bus: BXX, Device: 0x00, Function: 0x3}", # BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio?_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]
"BXXD00F4x": "PCI{Bus: BXX, Device: 0x00, Function: 0x4}", # BXX=NBIFRCCFG::SUB_BUS_NUMBER_LATENCY_nbio2_instNBIF1_dev0_aliasSMN[SECONDARY_BUS]
"BXXD01F0x": "PCI{Bus: BXX, Device: 0x01, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]; see IOHCMISC[0...3]x00000044 (IOHC::NB_BUS_NUM_CNTL) [_nbio[3:0]_aliasSMN; IOHCMISC[3:0]x00000044; IOHCMISC[3:0]=13[E:B]1_0000h]
"BXXD01F1x": "PCI{Bus: BXX, Device: 0x01, Function: 0x1}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD01F2x": "PCI{Bus: BXX, Device: 0x01, Function: 0x2}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD01F3x": "PCI{Bus: BXX, Device: 0x01, Function: 0x3}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD01F4x": "PCI{Bus: BXX, Device: 0x01, Function: 0x4}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD01F5x": "PCI{Bus: BXX, Device: 0x01, Function: 0x5}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD01F6x": "PCI{Bus: BXX, Device: 0x01, Function: 0x6}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD01F7x": "PCI{Bus: BXX, Device: 0x01, Function: 0x7}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD02F0x": "PCI{Bus: BXX, Device: 0x02, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD02F1x": "PCI{Bus: BXX, Device: 0x02, Function: 0x1}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD03F0x": "PCI{Bus: BXX, Device: 0x03, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD04F0x": "PCI{Bus: BXX, Device: 0x04, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD04F1x": "PCI{Bus: BXX, Device: 0x04, Function: 0x1}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD05F1x": "PCI{Bus: BXX, Device: 0x05, Function: 0x1}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio0_aliasSMN[NB_BUS_NUM]
"BXXD05F2x": "PCI{Bus: BXX, Device: 0x05, Function: 0x2}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio0_aliasSMN[NB_BUS_NUM]
"BXXD07F0x": "PCI{Bus: BXX, Device: 0x07, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD07F1x": "PCI{Bus: BXX, Device: 0x07, Function: 0x1}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD08F0x": "PCI{Bus: BXX, Device: 0x08, Function: 0x0}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD08F1x": "PCI{Bus: BXX, Device: 0x08, Function: 0x1}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD08F2x": "PCI{Bus: BXX, Device: 0x08, Function: 0x2}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
"BXXD08F3x": "PCI{Bus: BXX, Device: 0x08, Function: 0x3}", # BXX=IOHC::NB_BUS_NUM_CNTL_nbio?_aliasSMN[NB_BUS_NUM]
}

