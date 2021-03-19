#!/usr/bin/env python3

import phase2_result
import unroller
import re
import sys
from pprint import pprint
from rwops import strip_off_rwops

re_ficaa_offset_pattern = re.compile(r"^D([0-9A-Fa-f]+)F([0-9A-Fa-f]+)x([0-9A-Fa-f_]+)")

selected_access_method = "HOST"

def data_port_encode_ficaa(spec, data_port_base):
    if selected_access_method == "SMN":
        addr = calculate_hex_instance_value(spec)
        assert addr & data_port_base == 0, ("data_port_encode_ficaa: addr and data_port_base are disjunct", addr, data_port_base)
        return data_port_base | addr
    else:
        assert selected_access_method == "HOST"
        match = re_ficaa_offset_pattern.match(spec)
        assert(match), spec
        device, target_function, target_register = match.groups()
        device = int(device, 16)
        target_function = int(target_function, 16)
        target_register = int(target_register, 16)
        assert(device in [0x18]), device
        assert(target_function >= 0 and target_function < 8), target_function
        assert(target_register & 3 == 0), target_register
        assert(target_register < 2048), target_register
        addr = target_register | (target_function << 11)
        assert data_port_base & addr == 0, ("data_port_encode_ficaa: addr and data_port_base are disjunct", addr, data_port_base)
        # This loses the device reference.  I sure hope it's always D18
        return data_port_base | addr

re_x = re.compile(r"^[A-Z0-9_]+x.*")
re_xetc = re.compile(r"[A-Z0-9_]+.*x")

for item in [ #"_inst[TCDX[11:0],CAKE[5:0],PIE0,IOM[3:0],CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST; D18F1x200_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl",
#"_inst[TCDX[11:0],CAKE[5:0],PIE0,IOS3,IOM3,IOS2,IOM2,IOS1,IOM1,IOS0,IOM0,CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST;D18F0x04C_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl",
#"_inst[PIE0,IOM[3:0],CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST; D18F0x050_x[001E0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl",
#"_inst[IOS[3:0],BCST]_aliasHOST; D18F0x050_x[001[B:8]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl",
#"_inst[TCDX[11:0],CAKE[5:0],BCST]_aliasHOST; D18F0x050_x[00[30:1F]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl",
"_inst[TCDX[11:0],CAKE[5:0],PIE0,IOS3,IOM3,IOS2,IOM2,IOS1,IOM1,IOS0,IOM0,CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST; D18F0x044_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl",
"_nbio0_inst[IOAGR,NBIF0,PCIE[1:0]]_aliasSMN; IOMMUL1IOAGRPCIE0,IOMMUL1NBIFPCIE0,IOMMUL1PCIE[4,0]x000000F4; IOMMUL1IOAGRPCIE0,IOMMUL1NBIFPCIE0,IOMMUL1PCIE[4,0]=1[53,4F,4B,47]0_0000h",
"_nbio1_inst[IOAGR,NBIF0,PCIE[1:0]]_aliasSMN; IOMMUL1IOAGRPCIE1,IOMMUL1NBIFPCIE1,IOMMUL1PCIE[5,1]x000000F4; IOMMUL1IOAGRPCIE1,IOMMUL1NBIFPCIE1,IOMMUL1PCIE[5,1]=1[54,50,4C,48]0_0000h",
"_nbio2_inst[IOAGR,NBIF0,PCIE[1:0]]_aliasSMN; IOMMUL1IOAGRPCIE2,IOMMUL1NBIFPCIE2,IOMMUL1PCIE[6,2]x000000F4; IOMMUL1IOAGRPCIE2,IOMMUL1NBIFPCIE2,IOMMUL1PCIE[6,2]=1[55,51,4D,49]0_0000h",
"_nbio3_inst[IOAGR,NBIF0,PCIE[1:0]]_aliasSMN; IOMMUL1IOAGRPCIE3,IOMMUL1NBIFPCIE3,IOMMUL1PCIE[7,3]x000000F4; IOMMUL1IOAGRPCIE3,IOMMUL1NBIFPCIE3,IOMMUL1PCIE[7,3]=1[56,52,4E,4A]0_0000h",

]:
    item = item.replace("IOS3,IOM3", "IOMS3").replace("IOS2,IOM2", "IOMS2").replace("IOS1,IOM1", "IOMS1").replace("IOS0,IOM0", "IOMS0")
    instances = list(unroller.unroll_inst_pattern(item))
    pprint(instances)
    for instance in instances:
        print(instance, instance.resolve_physical_mnemonic(data_port_encode_ficaa))

    sys.exit(0)

#item = "_inst[TCDX[11:0],CAKE[5:0],PIE0,IOM[3:0],CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasSMN; DFF1x00000200_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DFF1=0001_C400h; DataPortWrite=DF::FabricConfigAccessControl"

#item = "_inst[TCDX[11:0],CAKE[5:0],PIE0,IOS3,IOM3,IOS2,IOM2,IOS1,IOM1,IOS0,IOM0,CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST; D18F0x044_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl"

# Original has IOS0,IOM0 and so on.  That's not correct.
item = "_inst[TCDX[11:0],CAKE[5:0],PIE0,IOS3,IOM3,IOS2,IOM2,IOS1,IOM1,IOS0,IOM0,CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST;D18F0x044_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl"

# sanitized: item = "_inst[TCDX[11:0],CAKE[5:0],PIE0,IOMS3,IOMS2,IOMS1,IOMS0,CCM[7:0],CCIX[3:0],CS[7:0],BCST]_aliasHOST; D18F0x044_x[00[30:1E]_0001,001[B:0]_0001,000[B:0]_0001,00000000]; DataPortWrite=DF::FabricConfigAccessControl"

instances = list(unroller.unroll_inst_pattern(item))
pprint(instances)
for instance in instances:
    print(instance, instance.resolved_physical_address)
sys.exit(0)

for name in dir(phase2_result):
    try:
        header, items = getattr(phase2_result, name)
    except (ValueError, TypeError):
        continue
    if header.find("_alias") != -1:
        #print("HEADER", header, "END HEADER")
        for item in header.split("\n"):
            item = item.strip()
            rwops, item = strip_off_rwops(item)
            #if item.find(" expressed ") != -1 or item.find(" are ") != -1:
            #    pass
            #elif item.startswith("[ AB Index Register ]") or item.startswith("NOTE"):
            #    pass
            # and (item.startswith("PCI Capabilities Pointer register_aliasHOST; ") or item.startswith("PCI Class Code/Revision ID register_aliasHOST;") or item.startswith("PCI Device/Vendor ID 0 register_aliasHOST;") or item.startwith("PCI Device/Vendor ID 1 register_aliasHOST; ")):
            # Misparsing: "_aliasFoo; X; A=2_aliasBar; Y; A=foo_aliasSMN"
            if item.count("_alias") > 1:
                print("WARNING: {!r} has too many aliases in one line.  Maybe that's OK, maybe not--who knows.".format(item), file=sys.stderr)
            if item.startswith("_"): # or re_x.match(item) or item.find("=") != -1:
                instances = list(unroller.unroll_inst_pattern(item))
                for instance in instances:
                    print("INSTANCE", instance)
            else:
                # Sanity check; better than nothing--but actually not all that useful anymore.
                if item.startswith("PCI CFG") or item.startswith("Max_Lat register") or item.startswith("PCI Express Capability header") or item.startswith("The ") or item.startswith("IDP Index") or item.endswith(" register.") or item.endswith(" header.") or item.startswith("These ") or item.find(" are ") != -1 or item.find(" for ") != -1 or item.find(" the ") != -1 or item.startswith("[ Interrupt Enable 0 ]") or item.startswith("[ Configuration Address Maps ]") or item.startswith("[ IO Space Base Address ]") or item.find(" and ") != -1 or item.startswith("[ IO Space Limit Address ]") or item.startswith("11.6.2 [DRAM Address Maps]") or item.startswith("DF::DramBaseAddress[LgcyMmioHoleEn].") or item.find(" to ") != -1 or item.startswith("[ AB Index Register ]") or item.find(" in ") != -1 or item.endswith(" register") or item.find(" is ") != -1 or item.find(" or ") != -1 or item.startswith("When ") or item == "Multiplier[5:0]}." or item.startswith("For example") or item.startswith("[ ") or item.find("MAX[") != -1 or item.startswith("(UMC::Phy::") or item == "Base address + 0x18" or item.endswith(" Register") or item.startswith("Total TS1") or item.endswith(" Register.") or item.endswith(" registers.") or item == "pri_tx_fifo control lane 0" or item == "pri_tx_fifo miscellaneous command" or item.startswith("Constraint:") or item == "DFI MaxReadLatency" or item.endswith(" ONLY") or item == "HWT MaxReadLatency." or item.find(" during ") != -1 or item == "PUBMODE - HWT Mux Select" or item.find("upstream message") != -1 or item.find("upstream mailbox") != -1 or item.find("upstream data mailbox") != -1 or item == "PMU Config Mux Select" or item.find("mailbox protocol") != -1 or item == "Microframe Index Register Bit Definitions" or item.find("Expected Data") != -1:
                    pass
                else:
                    # That is better than nothing--but an exhaustive list would be better ("x" or not doesn't matter)
                    assert not re_xetc.search(item) and (item.find("[") <= 0 or item.find("=") != -1), item
