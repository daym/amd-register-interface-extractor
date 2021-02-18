#!/usr/bin/env python3

import phase2_result
import unroller
import re
import sys
from rwops import strip_off_rwops

re_x = re.compile(r"^[A-Z0-9_]+x.*")
re_xetc = re.compile(r"[A-Z0-9_]+.*x")

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
                x = unroller.unroll_inst_pattern(item)
                print(x)
            else:
                # Sanity check; better than nothing--but actually not all that useful anymore.
                if item.startswith("PCI CFG") or item.startswith("Max_Lat register") or item.startswith("PCI Express Capability header") or item.startswith("The ") or item.startswith("IDP Index") or item.endswith(" register.") or item.endswith(" header.") or item.startswith("These ") or item.find(" are ") != -1 or item.find(" for ") != -1 or item.find(" the ") != -1 or item.startswith("[ Interrupt Enable 0 ]") or item.startswith("[ Configuration Address Maps ]") or item.startswith("[ IO Space Base Address ]") or item.find(" and ") != -1 or item.startswith("[ IO Space Limit Address ]") or item.startswith("11.6.2 [DRAM Address Maps]") or item.startswith("DF::DramBaseAddress[LgcyMmioHoleEn].") or item.find(" to ") != -1 or item.startswith("[ AB Index Register ]") or item.find(" in ") != -1 or item.endswith(" register") or item.find(" is ") != -1 or item.find(" or ") != -1 or item.startswith("When ") or item == "Multiplier[5:0]}." or item.startswith("For example") or item.startswith("[ ") or item.find("MAX[") != -1 or item.startswith("(UMC::Phy::") or item == "Base address + 0x18" or item.endswith(" Register") or item.startswith("Total TS1") or item.endswith(" Register.") or item.endswith(" registers.") or item == "pri_tx_fifo control lane 0" or item == "pri_tx_fifo miscellaneous command" or item.startswith("Constraint:") or item == "DFI MaxReadLatency" or item.endswith(" ONLY") or item == "HWT MaxReadLatency." or item.find(" during ") != -1 or item == "PUBMODE - HWT Mux Select" or item.find("upstream message") != -1 or item.find("upstream mailbox") != -1 or item.find("upstream data mailbox") != -1 or item == "PMU Config Mux Select" or item.find("mailbox protocol") != -1 or item == "Microframe Index Register Bit Definitions" or item.find("Expected Data") != -1:
                    pass
                else:
                    # That is better than nothing--but an exhaustive list would be better ("x" or not doesn't matter)
                    assert not re_xetc.search(item) and (item.find("[") <= 0 or item.find("=") != -1), item
