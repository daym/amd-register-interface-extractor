#!/usr/bin/env python3

import phase2_result
import unroller
import re
import sys

re_x = re.compile(r"^[A-Z0-9_]+x.*")
re_xetc = re.compile(r"[A-Z0-9_]+.*x")

for name in dir(phase2_result):
    try:
        header, items = getattr(phase2_result, name)
    except (ValueError, TypeError):
        continue
    if header.find("_alias") != -1:
        print("HEADER", header, "END HEADER")
        for item in header.split("\n"):
            item = item.strip()
            if item.startswith("Read-write.") or item.startswith("Read-only.") or item.startswith("Reset:") or item.startswith("Read,Write-1-to-clear.") or item.startswith("Volatile.") or item.startswith("Read-write,Volatile.") or item.startswith("Inaccessible.") or item.startswith("Write-only.") or item.startswith("Write-1-to-clear.") or item.startswith("Read-only,Volatile.") or item.startswith("Read-write,Read,Write-1-to-clear.") or item.startswith("Read-write,Reserved."):
              continue
            """
            if item.startswith("[ Interrupt Enable 0 ]"):
              continue
            if item.find("version and revision of the component, nominally expressed as: HwMajVer.HwMinVer.HwRev") != -1: # bug workaround
              continue
            if item.find("registers: DF::X86IOBaseAddress") != -1: # bug workaround
              continue
            if item.startswith("(PCS::DXIO::"): # bug workaround
              continue
            if item.startswith("[ "): # bug workaround
              continue
            if item.startswith("where they need to be routed."):
              continue
            if item.startswith("base/limit range are routed"):
              continue
            if item.startswith("IO mapping rules:"):
              continue
            if item.find("and as specified by DF::X86IOBaseAddress[IE]") != -1:
              continue
            if item.startswith("The appropriate DF::X86IOBaseAddress[RE]"):
              continue
            if item.startswith("IO Space Limit Address Register. See"):
              continue
            if item.startswith("DRAM limit registers provides mapping"):
              continue
            if item.startswith("This register along with the"):
              continue
            if item.startswith("MMIO addresses to the corresponding FabricID of the IOS where they need to be routed."):
              continue
            if item.startswith("a ") or item.find(" and ") != -1 or item.endswith("and") or item.find(" is defined ") != -1 or item.find(" or ") != -1:
              continue
            if item.find(" the ") != -1 or item.startswith("The") or item.find(" a ") != -1:
              continue
            if item.find(" to ") != -1 or item.find(" for ") != -1 or item.find(" and ") != -1:
              continue
            if item.find("Lane 0") != -1 or item.endswith("register.") or item.endswith("header.") or item.endswith("Pointer."):
              continue
            if item.find("  BAR") != -1 and item.find(".") != -1:
              continue
            if item.find(" register ") != -1: # XXX
              continue
            if item.find(" table ") != -1: # XXX
              continue
            if item.startswith("(DF::") or item.startswith("DF::") or item.startswith("(FCH::"):
              continue
            if item.find("See ") != -1 or item.startswith("also "):
              continue
            if item.startswith("NOTE1:"): # XXX
              continue
            if item.startswith("NOTE2:"): # XXX
              continue
            if item.startswith("*Note"):
              continue
            if item.startswith("One "): # XXX
              continue
            if item.startswith("For example,"):
              continue
            if item.find(" denotes ") != -1 or item.find(" with ") != -1:
              continue
            if item == "Register A: Control register" or item == "Register B: Control register" or item == "Register C: Control register":
              continue
            if item.startswith("(IOAPIC::"):
              continue
            if item.startswith("IOHC::") or item.startswith("(IOHC::") or item.startswith("(IOMMUL1::") or item.startswith("(IOMMUL2::") or item.startswith("IOMMUL2::"):
              continue
            if item.startswith("MCA::"):
              continue
            if item.startswith("(MCA::"):
              continue
            if item.find(" through ") != -1:
              continue
            if item.startswith("same as "):
              continue
            if item.startswith("result in "): # XXX
              continue
            if item.startswith("(SYSHUBMM::"):
              continue
            if item.startswith("NBIFEPFNCFG::") and item.endswith("}"):
              continue
            if item.startswith("Multiplier") and item.endswith("}."):
              continue
            if item.startswith("(SDPMUX::") or item.startswith("(SST::"):
              continue
            if item.startswith("when "): # " is "
              continue
            if item.startswith("(UMC::"):
              continue
            if item.startswith("(USB31::"):
              continue
            if item.startswith("simply "): # " be "
              continue
            if item == "Programming constraints:" or item == "For 1X mode:" or item == "For 2X mode:" or item == "For 4X mode:" or item == "For dynamic mode:": # XXX
              continue
            if item.find("Tref > ( ") != -1 or item.find("Tref > ( (MAX[Txs+Tzqoper, 2*Trfc2,2*Tzqcs] + MAX[32 *") != -1 or item.find("Tref > ( (MAX[Txs+Tzqoper, 4*Trfc2,4*Tzqcs]r + MAX[32") != -1 or item.find("Tref > ( (MAX[Txs+Tzqoper, 4*Trfc4,4*Tzqcs]") != -1: # XXX
              continue
            if item == "xHCI Register Power-On Value:":
              continue
            if item == "TX/RX Data FIFO Sizes:" or item == "TX/RX Threshold Control Register Settings as below:" or item == "Global User Control Register:":
              continue
            if item == "Note:" or item.startswith("Note :") or item.startswith("the "):
              continue
            if item.find(" is valid") != -1:
              continue
            if item.find("Field ") != -1 or item.find("Register") != -1 or item.find(" four ") != -1:
              continue
            if item.startswith("PHY Initialization Engine"):
              continue
            if item == 'Bus (USB) Specification 3.1.':
              continue
            """
            #if item.find(" expressed ") != -1 or item.find(" are ") != -1:
            #    pass
            #elif item.startswith("[ AB Index Register ]") or item.startswith("NOTE"):
            #    pass
            # and (item.startswith("PCI Capabilities Pointer register_aliasHOST; ") or item.startswith("PCI Class Code/Revision ID register_aliasHOST;") or item.startswith("PCI Device/Vendor ID 0 register_aliasHOST;") or item.startwith("PCI Device/Vendor ID 1 register_aliasHOST; ")):
            if item.count("_alias") > 1:
                for item in item.split("_alias")[1:]:
                    item = "_alias" + item
                    x = unroller.unroll_inst_pattern(item)
                    print(x)
                continue
            elif item.count("_alias") in [0,1]:
                pass
            else:
                print("WARNING: {!r} has too many aliases in one line".format(item), file=sys.stderr)
            if item.startswith("_"): # or re_x.match(item) or item.find("=") != -1:
                x = unroller.unroll_inst_pattern(item)
                print(x)
            else:
                # Sanity check
                if item.startswith("PCI CFG") or item.startswith("Max_Lat register") or item.startswith("PCI Express Capability header") or item.startswith("The ") or item.startswith("IDP Index") or item.endswith(" register.") or item.endswith(" header.") or item.startswith("These ") or item.find(" are ") != -1 or item.find(" for ") != -1 or item.find(" the ") != -1 or item.startswith("[ Interrupt Enable 0 ]") or item.startswith("[ Configuration Address Maps ]") or item.startswith("[ IO Space Base Address ]") or item.find(" and ") != -1 or item.startswith("[ IO Space Limit Address ]") or item.startswith("11.6.2 [DRAM Address Maps]") or item.startswith("DF::DramBaseAddress[LgcyMmioHoleEn].") or item.find(" to ") != -1 or item.startswith("[ AB Index Register ]") or item.find(" in ") != -1 or item.endswith(" register") or item.find(" is ") != -1 or item.find(" or ") != -1 or item.startswith("When ") or item == "Multiplier[5:0]}." or item.startswith("For example"):
                    pass
                else:
                    # That is better than nothing--but an exhaustive list would be better ("x" or not doesn't matter)
                    assert not re_xetc.search(item) and (item.find("[") <= 0 or item.find("=") != -1), item
