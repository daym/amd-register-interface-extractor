#!/usr/bin/env python3

import sys
import pdb
import sys
from io import StringIO
from collections import namedtuple

#RegisterInstanceSpec = namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])

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

class RegisterInstanceSpec(namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])):
	@property
	def resolved_physical_mnemonic(self):
		physical_mnemonic = self.physical_mnemonic
		for definition in self.variable_definitions:
			lhs_spec, rhs_spec = definition.split("=", 1)
			lhs = unroll_inst_item_pattern(lhs_spec.replace("::", "**"))
			rhs = unroll_inst_item_pattern("=" + rhs_spec.replace("::", "**"))
			assert len(lhs) == len(rhs), (self.physical_mnemonic, lhs_spec, rhs_spec, lhs, rhs)
			for l, r in zip(lhs, rhs):
				l = l.replace("**", "::")
				r = r.replace("**", "::").lstrip("=")
				if physical_mnemonic.startswith(l + "x"):
					physical_mnemonic = r + " + " + physical_mnemonic[len(l + "x"):]
					break
				elif physical_mnemonic.startswith(l):
					physical_mnemonic = r + " + " + physical_mnemonic[len(l):]
					break
		for k, v in settings.items():
			physical_mnemonic = physical_mnemonic.replace(k, v)
		return physical_mnemonic

"""
TODO:
            logical_mnemonic = logical_mnemonic.strip()
            if logical_mnemonic == "_ccd[7:0]_lthree[1:0]_core[3:0]_thread[1:0]" or logical_mnemonic.startswith("_ccd[7:0]_lthree[1:0]_core[3:0]_thread[1:0]_n"
) or logical_mnemonic == "_ccd[7:0]_lthree[1:0]_core[3:0]" or logical_mnemonic.startswith("_ccd[7:0]_lthree[1:0]_core[3:0]_n") or logical_mnemonic == "_ccd[7:0
]_lthree[1:0]" or logical_mnemonic.startswith("_ccd[7:0]_lthree[1:0]_n") or re_direct_instance_number.match(logical_mnemonic): # implicit core reference etc
                aliaskind = None
            elif context_string and context_string.startswith("SBRMIx"):
                aliaskind = None # FIXME: AMD does not specify which it is.
            elif context_string and context_string.startswith("DFPMCx"):
                aliaskind = None # FIXME: AMD does not specify which it is.
            else:
                assert logical_mnemonic.find("_alias") != -1, (logical_mnemonic, context_string)
                aliaskinds = re_alias.findall(logical_mnemonic)
                assert len(aliaskinds) == 1, logical_mnemonic
                aliaskind, = aliaskinds
"""

def unroll_inst_item_pattern(spec):
	"""
	>>> list(unroll_inst_item_pattern("_inst[INTSBDEVINDCFG0,NBIF[1:0]DEVINDCFG0,PCIE1DEVINDCFG[7:0],PCIE0DEVINDCFG[7:0]]_aliasSMN"))
	['_instINTSBDEVINDCFG0_aliasSMN', '_instNBIF1DEVINDCFG0_aliasSMN', '_instNBIF0DEVINDCFG0_aliasSMN', '_instPCIE1DEVINDCFG7_aliasSMN', '_instPCIE1DEVINDCFG6_aliasSMN', '_instPCIE1DEVINDCFG5_aliasSMN', '_instPCIE1DEVINDCFG4_aliasSMN', '_instPCIE1DEVINDCFG3_aliasSMN', '_instPCIE1DEVINDCFG2_aliasSMN', '_instPCIE1DEVINDCFG1_aliasSMN', '_instPCIE1DEVINDCFG0_aliasSMN', '_instPCIE0DEVINDCFG7_aliasSMN', '_instPCIE0DEVINDCFG6_aliasSMN', '_instPCIE0DEVINDCFG5_aliasSMN', '_instPCIE0DEVINDCFG4_aliasSMN', '_instPCIE0DEVINDCFG3_aliasSMN', '_instPCIE0DEVINDCFG2_aliasSMN', '_instPCIE0DEVINDCFG1_aliasSMN', '_instPCIE0DEVINDCFG0_aliasSMN']
	>>> list(unroll_inst_item_pattern("IOHCDEVINDx[0000_C004,0000_9004,0000_8004,0000_[[4:1][C,8,4,0]]04]"))
	['IOHCDEVINDx0000_C004', 'IOHCDEVINDx0000_9004', 'IOHCDEVINDx0000_8004', 'IOHCDEVINDx0000_4C04', 'IOHCDEVINDx0000_4804', 'IOHCDEVINDx0000_4404', 'IOHCDEVINDx0000_4004', 'IOHCDEVINDx0000_3C04', 'IOHCDEVINDx0000_3804', 'IOHCDEVINDx0000_3404', 'IOHCDEVINDx0000_3004', 'IOHCDEVINDx0000_2C04', 'IOHCDEVINDx0000_2804', 'IOHCDEVINDx0000_2404', 'IOHCDEVINDx0000_2004', 'IOHCDEVINDx0000_1C04', 'IOHCDEVINDx0000_1804', 'IOHCDEVINDx0000_1404', 'IOHCDEVINDx0000_1004']
	"""
	class Scanner(object):
		def __init__(self, input_data):
			self.input_data = input_data
			self.c = self.input_data[0]
		def consume(self):
			self.input_data = self.input_data[1:]
			self.c = self.input_data[0] if self.input_data != "" else None
	if not spec:
		return []
	scanner = Scanner("{}".format(spec))
	def parse_item(): # "02432432foo[2:1] -> [02432432foo2, 02432432foo1]",  "5:[2,1]"
		item = StringIO("")
		while scanner.c and scanner.c not in ":,]=":
			if scanner.c == "[":
				prefix = item.getvalue()      # "foo[..." => "foo"
				scanner.consume()
				values = parse_alternatives()
				assert scanner.c == "]", (scanner.input_data, spec)
				scanner.consume()
				suffixes = parse_item()
				result = []
				for v in values:
					for x in suffixes:
						result.append("{}{}{}".format(prefix, v, x))
				#item = StringIO("")
				assert not (scanner.c and scanner.c not in ":,]"), "would stop anyway"
				return result
			else:
				item.write(scanner.c)
				scanner.consume()
		if scanner.c == "=": # after that, none of the stuff is supposed to do anything special!
			while scanner.c: # and scanner.c not in ":,]":
				if scanner.c == "{": # quote everything
					while scanner.c and scanner.c != "}":
						item.write(scanner.c)
						scanner.consume()
					if scanner.c:
						item.write(scanner.c)
						scanner.consume()
				else:
					item.write(scanner.c)
					scanner.consume()
		return [item.getvalue()]
	def parse_range(): # "a:b" or "a";   a*b   [3+2]*8
		a_s = parse_item()
		if scanner.c == ":":
			scanner.consume()
			b_s = parse_item()
			result = []
			for a in a_s:
				for b in b_s:
					beginning, end = a, b
					radix = 10
					short = len(beginning) == 1 and len(end) == 1 # cannot be misinterpreted
					# The idea is to prefer to interpret things as decimal, but fall back to hexadecimal if we must.
					radix = 10
					if spec.find("x") != -1:
						radix = 16
						assert not spec.startswith("_")
					else:
						assert spec.startswith("_"), spec

					beginning = int(beginning, radix)
					end = int(end, radix)
					assert beginning >= end
					for i in range(beginning, end - 1, -1):
						if radix == 16:
							result.append("{:X}".format(i))
						elif radix == 10:
							result.append("{}".format(i))
						else:
							assert False
			return result
		else:
			return a_s
	def parse_alternatives(): # "a,b" or "a";    a+b
		a = parse_range()
		while scanner.c == ",":
			scanner.consume()
			b = parse_range()
			a = a + b
		return a
	def parse_toplevel():
		result = []
		prefix = ""
		values = parse_alternatives()
		suffixes = parse_item()
		result = []
		for v in values:
			for x in suffixes:
				result.append("{}{}{}".format(prefix, v, x))
		#item = StringIO("")
		assert not (scanner.c and scanner.c not in ":,]"), "would stop anyway"
		return result

	#pdb.set_trace()
	return [choice for choice in parse_toplevel()]

def unroll_inst_pattern(spec):
	#"""
	#>>> unroll_inst_pattern("_inst[INTSBDEVINDCFG0,NBIF[1:0]DEVINDCFG0,PCIE1DEVINDCFG[7:0],PCIE0DEVINDCFG[7:0]]_aliasSMN; IOHCDEVINDx[0000_C004,0000_9004,0000_8004,0000_[[4:1][C,8,4,0]]04]; IOHCDEVIND=13B3_0000h")
	#"""
	variable_definitions = []
	insts = []
	physs = []
	for item in spec.split(";"):
		item = item.strip()
		if item.find("=") != -1: # local variable definition
			physs.append(item)
			#variable_definitions.append(item)
		else:
			if item.startswith("_ccd[7:0]_lthree0_core[7:0]_thread[1:0]"): # According to AMD this does not count as a pattern for us
				item = item.replace("_ccd[7:0]_lthree0_core[7:0]_thread[1:0]", "_ccd7.0_lthree0_core7.0_thread1.0")
			elif item.startswith("_ccd[7:0]_lthree0_core[7:0]"): # According to AMD this does not count as a pattern for us
				item = item.replace("_ccd[7:0]_lthree0_core[7:0]", "_ccd7.0_lthree0_core7.0")
			elif item.startswith("_ccd[7:0]_lthree0"): # According to AMD this does not count as a pattern for us
				item = item.replace("_ccd[7:0]_lthree0", "_ccd7.0_lthree0")
			try:
				x = list(unroll_inst_item_pattern(item))
			except:
				print("ITEM", item, file=sys.stderr)
				raise
			x = [c.replace("_ccd7.0_lthree0_core7.0_thread1.0", "_ccd[7:0]_lthree0_core[7:0]_thread[1:0]").replace("_ccd7.0_lthree0_core7.0", "_ccd[7:0]_lthree0_core[7:0]").replace("_ccd7.0_lthree0", "_ccd[7:0]_lthree0") for c in x]
			while len(x) > 0 and x[-1] == "": # TODO: Be nicer about this.
				x = x[:-1]
			if item.startswith("_"): # find("_alias") != -1 or item.find(": # alias beginning
				insts += x
			else: # expression
				physs += x
	#result = RegisterInstanceSpec(logical_mnemonic=insts, physical_mnemonic_and_variables=physs)
	#FIXME: assert len(insts) == len(accesses), (insts, accesses)
	ps = [c for c in physs if c.find("=") == -1]
	if len(insts) != len(ps):
		if insts == [] and ps != []:
			pass
		elif insts != [] and ps == []:
			pass
		else:
			print("ERROR", insts, physs, file=sys.stderr)
		# else who knows
	#print("PHYSS", physs, file=sys.stderr)
	phys_i = 0
	for logical_mnemonic in insts:
		physical_mnemonic_and_variables = []
		if phys_i < len(physs):
			assert physs[phys_i].find("=") == -1
			physical_mnemonic = physs[phys_i]
			phys_i += 1
			variable_definitions = [c for c in physs[phys_i:] if c.find("=") != -1]
			while phys_i < len(physs) and physs[phys_i].find("=") != -1:
				phys_i += 1
			yield RegisterInstanceSpec(logical_mnemonic=logical_mnemonic, physical_mnemonic=physical_mnemonic, variable_definitions=variable_definitions)
		else:
			print("WARNING: Not enough phys entries, log={!r}; Note: all_physs={!r}".format(logical_mnemonic, physs), file=sys.stderr)

if __name__ == "__main__":
	import doctest
	doctest.testmod()
