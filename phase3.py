#!/usr/bin/env python3

import sys
import getopt
import re
import shutil
import phase2_result
from phase2_result import __names, __model
import os
import pprint
import traceback
import logging
from collections import namedtuple
from rwops import strip_off_rwops
from unroller import unroll_inst_pattern, RegisterInstanceSpec
from hexcalculator import calculate_hex_instance_value as internal_calculate_hex_instance_value
from logging import debug, info, warning, error, critical

logging.basicConfig(level=logging.INFO)

selected_access_method = "HOST"
selected_data_port_write = "direct"
selected_error_handling = "omit-registers-with-errors"
selected_alias_reduction_method = "none"

def usage():
    print("Usage: {} [-a] [-m <mode>] [-d <data-port-write>] [-k]".format(sys.argv[0]))
    print("Options:")
    print("\t-a\t--reduce-aliases\tReduce the number of aliases printed by preferring aliases with modern access methods to aliases with older access methods")
    print("\t-m <method>\t--mode=<method>\tOnly emit registers with the given access method (choices: HOST, IO, SMN)")
    print("\t-d <data-port-write>\t--data-port-write=<data-port-write>\tOnly emit registers with the given data port write")
    print("\t-k\t--keep-registers-with-errors\tKeep registers that have errors (like unknown addressOffset), but mark them in the description")

try:
    opts, args = getopt.getopt(sys.argv[1:], "m:d:kah", ["mode=", "data-port-write=", "keep-registers-with-errors", "reduce-aliases", "help"])
except getopt.GetoptError:
    usage()
    sys.exit(2)

for k,v in opts:
	if k == "-m" or k == "--mode":
		selected_access_method = v
	elif k == "-d" or k == "--data-port-write":
		selected_data_port_write = v
	elif k == "-k" or k == "--keep-registers-with-errors":
		selected_error_handling = "keep-registers-with-errors"
	elif k == "-a" or k == "--reduce-aliases":
		selected_alias_reduction_method = "default"
	elif k == "-h" or k == "--help":
		usage()
		sys.exit()

def calculate_hex_instance_value(s):
	if s.startswith("MSR"):
		# Those have "MSR" prefix AND "MSR" access method.
		assert selected_access_method == "MSR"
		s = s[len("MSR"):]
	else:
		assert selected_access_method != "MSR"
	return internal_calculate_hex_instance_value(s)

re_pattern = re.compile(r"^([0-9A-F]+[_0-9A-Fa-f]*)[.][.][.]([0-9A-F]+[_0-9A-Fa-f]*)$")

def unroll_pattern(spec):
	""" Note: Can return None """
	# TODO: UARTx[2E...3F]8
	if spec.startswith("Table "):
		return [spec]
	#print("SPEC", spec)
	i = spec.find("[")
	if i != -1:
		j = spec.find("]")
		assert j != -1
		prefix = spec[:i]
		suffix = spec[j + 1:]
		assert prefix.count("[") == 0
		assert prefix.count("]") == 0
		assert suffix.count("[") == 0
		assert suffix.count("]") == 0
		pattern = spec[i + 1 : j]
		match = re_pattern.match(pattern)
		assert match, (spec, pattern)
		i = len(match.group(1))
		assert i == len(match.group(2))
		fmt = "{:0%dX}" % (i, ) # as many digits as the original had
		beginning = int(match.group(1), 16)
		end = int(match.group(2), 16)
		for i in range(beginning, end + 1):
			yield prefix + fmt.format(i) + suffix
	elif spec.find("...") != -1:
		beginning_string, end_string = spec.split("...")
		return None
	else:
		# TODO: Sometimes, a hex digit can be mistaken for a character.
		return [spec]

#List_of_Namespaces = phase2_result.List_of_Namespaces # Namespace -> Chapter

memory_map = None
if selected_access_method == "HOST" or selected_access_method == "HOSTGPU":
	if selected_data_port_write == "DF::FabricConfigAccessControl":
		_, memory_map = getattr(phase2_result, "Memory_Map___PCICFG_Physical_Mnemonic_Namespace", ("", []))
	else:
		_, memory_map = getattr(phase2_result, "Memory_Map___Main_Memory_Physical_Mnemonic_Namespace", ("", []))
elif selected_access_method == "MSR":
	_, memory_map = phase2_result.Memory_Map___MSR_Physical_Mnemonic_Namespace
elif selected_access_method == "SMN":
	_, memory_map = getattr(phase2_result, "Memory_Map___SMN_Physical_Mnemonic_Namespace", getattr(phase2_result, "Memory_Map___SMN", ("", None)))
	if memory_map is None:
		warning("No 'Memory Map - SMN' section found in PDF.  Namespaces will be hard-coded")
		memory_map = []
elif selected_access_method == "SMNCCD":
	_, memory_map = getattr(phase2_result, "Memory_Map___SMNCCD_Physical_Mnemonic_Namespace", ("", []))
elif selected_access_method == "IO":
	memory_map = [] # TODO: hard-code all the IO namespaces
elif selected_access_method == "HOSTLEGACY":
	memory_map = []
elif selected_access_method == "MSRLEGACY":
	memory_map = []
elif selected_access_method == "MSRLSLEGACY":
	memory_map = []
elif selected_access_method == "CPUID":
	memory_map = []

assert memory_map is not None, "Memory map for access_method={!r}, data_port_write={!r}".format(selected_access_method, selected_data_port_write)

if memory_map != [] and memory_map[-1] == []:
	memory_map = memory_map[:-1]

re_umc_ctl = re.compile(r"(UMC[0-9][0-9]CTLx00000804_)")
re_smu_clk = re.compile(r"(RSMUCLKA0[0-9]MMIOx)")

def raise_namespace_error(problematic_prefix):
	error("Cannot determine unique namespace for prefix {!r}".format(problematic_prefix + "x"))
	info("Context for the error above:")
	for row in memory_map:
		try:
			spec, namespace = row
		except (TypeError, ValueError): # sometimes there are slight mistakes in the namespace map
			warning("Malformed row in memory map: {}".format(row))
			continue

		addr, *spec = spec.split(":", 1)
		if len(spec) > 0:
			spec = spec[0]
			spec = spec.strip()
			prefix, *b = spec.split("x", 1)
			if len(b) > 0:
				if prefix == problematic_prefix:
					info(" prefix {!r} namespace {!r} (spec {!r}) ".format(prefix, namespace, spec))
	raise Exception("Cannot determine unique namespace for prefix {!r}".format(problematic_prefix + "x"))

def calculate_namespaces():
	# For now, this assumes that the part of the name before the "x" is unique enough.
	# If necessary, this can be adapted to unroll the spec pattern in the map and register all of those instances in the map (with the respective namespace)--but for now, that's overkill.
	result = {}
	for row in memory_map:
		try:
			spec, namespace = row
		except (TypeError, ValueError): # sometimes there are slight mistakes in the namespace map
			warning("Malformed row in memory map: {}".format(row))
			continue
		addr, *spec = spec.split(":", 1)
		if len(spec) > 0:
			spec = spec[0]
			spec = spec.strip()
			prefix, *b = spec.split("x", 1)
			if len(b) > 0:
				assert len(prefix) >= 2
				if spec.startswith("PMx5F_"): # RTCEXT
					pass
				elif spec.startswith("PMx"):
					result["PMx"] = "FCH::PM" #  PM2 only very rarely
				elif spec.startswith("SATA0AHCIx") or spec.startswith("SATA1AHCIx") or spec.startswith("SATA2AHCIx") or spec.startswith("SATA3AHCIx"):
					# Technically, there's still more sub-namespaces here.
					result[spec[:spec.find("x") + 1]] = "SYSHUB::SATA::AHCI"
				elif spec.startswith("USBCONTAINER0x0007") or spec.startswith("USBCONTAINER1x0007"):
					pass
				elif spec.startswith("PCIERCCFG0F0x") or spec.startswith("PCIERCCFG1F0x"): # Work around Naples namespace confusion
					result[spec[:spec.find("x") + 1]] = "PCIESWUSCFG"
				elif spec.startswith("GPUF0REGx"):
					result[spec[:spec.find("x") + 1]] = "OSS"
				elif spec.startswith("ACPMMIOx"):
					result[spec[:spec.find("x") + 1]] = "ACP" # way too complicated otherwise
				elif spec.startswith("D18F5x000002"): # those are in a more specific namespace than just "DF". (Milan A0)
					# ['0001D400: D18F5x00000200_x0000_0001..._x000B_0001', 'MCA::CS']
					# ['0001_D400h: D18F5x00000200_x001E_0001', 'MCA::PIE']
					result[spec] = namespace # sigh. Way too specific--but it will work.
				elif m := re_umc_ctl.match(spec): # -> UMC::Phy; Genoa
					result[m.group(1)] = namespace
				elif spec.startswith("SMNSCFx"): # in Genoa
					result[spec] = namespace # That's way too specific--but it will work.
				elif spec.startswith("FCHI3Cx"):
					# ['00000000: FCHI3Cx02DE2000...x02DE22E8', 'FCH::I3C']
					# ['00000000: FCHI3Cx02DE2600...x02DE2610', 'FCHI3C']
					# ['00000000: FCHI3Cx02DE3000...x02DE32E8', 'FCH::I3C']
					# ['00000000: FCHI3Cx02DE3600...x02DE3610', 'FCHI3C']
					# ['00000000: FCHI3Cx02DE4000...x02DE42E8', 'FCH::I3C']
					# ['00000000: FCHI3Cx02DE4600...x02DE4610', 'FCHI3C']
					# ['00000000: FCHI3Cx02DE5000...x02DE52E8', 'FCH::I3C']
					# ['00000000: FCHI3Cx02DE5600...x02DE5610', 'FCHI3C']
					result[spec] = namespace
				elif spec.startswith("WAFLC0x0002"):
					# prefix 'WAFLC0' namespace 'WAFLC::WAFL0' (spec 'WAFLC0x00000000...x00010000')
					# prefix 'WAFLC0' namespace 'AESCTR' (spec 'WAFLC0x00020000...x000200A4')
					result["WAFLC0x0002"] = namespace
				elif spec.startswith("WAFLC1x0002"):
					# prefix 'WAFLC1' namespace 'WAFLC::WAFL1' (spec 'WAFLC1x00000000...x00010000')
					# prefix 'WAFLC1' namespace 'AESCTR' (spec 'WAFLC1x00020000...x000200A4')
					result["WAFLC1x0002"] = namespace
				elif prefix.startswith("RSMU") and prefix.endswith("MMIO"):
					# prefix 'RSMUMP1MMIO' namespace 'SMU::RSMU::RSMU::MP1::MMIO' (spec 'RSMUMP1MMIOx00000004...x000003C4')
					# prefix 'RSMUMP1MMIO' namespace 'SMU::RSMU::RSMU::MP1::MMIOEXT' (spec 'RSMUMP1MMIOx000007B8...x000007C4')
					# prefix 'RSMUMP1MMIO' namespace 'SMU::RSMU::RSMU::MP1::MMIO' (spec 'RSMUMP1MMIOx00000800...x00000DD8')
					# prefix 'RSMUTHMMMIO' namespace 'SMU::RSMU::RSMU::THM::MMIO' (spec 'RSMUTHMMMIOx00000004...x000003C4')
					# prefix 'RSMUTHMMMIO' namespace 'SMU::RSMU::RSMU::THM::MMIOEXT' (spec 'RSMUTHMMMIOx000007B8...x000007C4')
					# prefix 'RSMUTHMMMIO' namespace 'SMU::RSMU::RSMU::THM::MMIO' (spec 'RSMUTHMMMIOx00000800...x00000DD8')
					# prefix 'RSMUSMUIOMMIO' namespace 'SMU::RSMU::RSMU::SMUIO::MMIO' (spec 'RSMUSMUIOMMIOx00000004...x000003C4')
					# prefix 'RSMUSMUIOMMIO' namespace 'SMU::RSMU::RSMU::SMUIO::MMIOEXT' (spec 'RSMUSMUIOMMIOx00000794...x000007C4')
					# prefix 'RSMUSMUIOMMIO' namespace 'SMU::RSMU::RSMU::SMUIO::MMIO' (spec 'RSMUSMUIOMMIOx00000800...x00000DD8')
					# prefix 'RSMUFUSEMMIO' namespace 'SMU::RSMU::RSMU::FUSE::MMIO' (spec 'RSMUFUSEMMIOx00000004...x000003C4')
					# prefix 'RSMUFUSEMMIO' namespace 'SMU::RSMU::RSMU::FUSE::MMIOEXT' (spec 'RSMUFUSEMMIOx000007B8...x000007C4')
					# prefix 'RSMUFUSEMMIO' namespace 'SMU::RSMU::RSMU::FUSE::MMIO' (spec 'RSMUFUSEMMIOx00000800...x00000DD8')
					# prefix 'RSMUSMUIO1MMIO' namespace 'SMU::RSMU::RSMU::SMUIO1::MMIO' (spec 'RSMUSMUIO1MMIOx00000004...x000003C4')
					# prefix 'RSMUSMUIO1MMIO' namespace 'SMU::RSMU::RSMU::SMUIO1::MMIOEXT' (spec 'RSMUSMUIO1MMIOx000007B8...x000007C4')
					# prefix 'RSMUSMUIO1MMIO' namespace 'SMU::RSMU::RSMU::SMUIO1::MMIO' (spec 'RSMUSMUIO1MMIOx00000800...x00000DD8')
					# prefix 'RSMUCLKA00MMIO' namespace 'SMU::RSMU::RSMU::CLKA::MMIO' (spec 'RSMUCLKA00MMIOx00000018...x000003C4')
					# prefix 'RSMUCLKA00MMIO' namespace 'SMU::RSMU::RSMU::CLKA::MMIOEXT' (spec 'RSMUCLKA00MMIOx000007B8...x000007D0')
					# prefix 'RSMUCLKA00MMIO' namespace 'SMU::RSMU::RSMU::CLKA::MMIO' (spec 'RSMUCLKA00MMIOx00000800...x00000DD8')
					# prefix 'RSMUACPMMIO' namespace 'SMU::RSMU::RSMU::ACP::MMIO' (spec 'RSMUACPMMIOx00000008...x000003C4')
					# prefix 'RSMUACPMMIO' namespace 'SMU::RSMU::RSMU::ACP::MMIOEXT' (spec 'RSMUACPMMIOx000007B8...x000007C4')
					# prefix 'RSMUACPMMIO' namespace 'SMU::RSMU::RSMU::ACP::MMIO' (spec 'RSMUACPMMIOx00000800...x00000DD8')
					# prefix 'RSMUSDPMUX0MMIO' namespace 'SMU::RSMU::RSMU::SDPMUX::MMIO' (spec 'RSMUSDPMUX0MMIOx00000004...x000003C4')
					# prefix 'RSMUSDPMUX0MMIO' namespace 'SMU::RSMU::RSMU::SDPMUX::MMIOEXT' (spec 'RSMUSDPMUX0MMIOx00000784...x000007C4')
					# prefix 'RSMUSDPMUX0MMIO' namespace 'SMU::RSMU::RSMU::SDPMUX::MMIO' (spec 'RSMUSDPMUX0MMIOx00000800...x00000DD8')
					# prefix 'RSMUNTB0MMIO' namespace 'SMU::RSMU::RSMU::NTB::MMIO' (spec 'RSMUNTB0MMIOx00000004...x000003C4')
					# prefix 'RSMUNTB0MMIO' namespace 'SMU::RSMU::RSMU::NTB::MMIOEXT' (spec 'RSMUNTB0MMIOx000007B8...x000007C4')
					# prefix 'RSMUNTB0MMIO' namespace 'SMU::RSMU::RSMU::NTB::MMIO' (spec 'RSMUNTB0MMIOx00000800...x00000DD8')
					result[spec] = namespace # That's way too specific--but it will work.
				elif prefix.endswith("SMUMMIO"):
					# prefix 'CCD00CCXSEC0RSMUMMIO' namespace 'SMU::RSMU::RSMU::CCXSEC::MMIO' (spec 'CCD00CCXSEC0RSMUMMIOx00000000...x000003C4')
					# prefix 'CCD00CCXSEC0RSMUMMIO' namespace 'SMU::RSMU::RSMU::CCXSEC::MMIOEXT' (spec 'CCD00CCXSEC0RSMUMMIOx000007B8...x000007C4')
					# prefix 'CCD00CCXSEC0RSMUMMIO' namespace 'SMU::RSMU::RSMU::CCXSEC::MMIO' (spec 'CCD00CCXSEC0RSMUMMIOx00000800...x00000DE8')
					result[spec] = namespace # That's way too specific--but it will work.
				elif spec.startswith("NBIO0NBIFMISC0x000008") or spec.startswith("NBIO0NBIFMISC1x000008") or spec.startswith("NBIO1NBIFMISC0x000008") or spec.startswith("NBIO1NBIFMISC1x000008"):
					# prefix 'NBIO0NBIFMISC0' namespace 'NBIFMM' (spec 'NBIO0NBIFMISC0x00000000...x00000600')
					# prefix 'NBIO0NBIFMISC0' namespace 'SYSHUBMM' (spec 'NBIO0NBIFMISC0x00000800...x000008F4')
					# prefix 'NBIO0NBIFMISC0' namespace 'NBIFMM' (spec 'NBIO0NBIFMISC0x00000900...x0000094C')
					result[spec] = namespace
				elif spec.startswith("MCAKPXGMICNTRx"): # Note: Value of variable MCAKPXGMICNTR is different depending on namespace.
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::SERDES' (spec 'MCAKPXGMICNTRx00000000...x000000A8')

					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::WAFL' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::WAFL' (spec 'MCAKPXGMICNTRx00000000...x000000A8')

					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					# prefix 'MCAKPXGMICNTR' namespace 'MCA::KPX::GMI' (spec 'MCAKPXGMICNTRx00000000...x000000A8')
					result[spec] = namespace
				elif prefix in ["CCD00SMNCONFIG", "CCD01SMNCONFIG", "CCD02SMNCONFIG", "CCD03SMNCONFIG", "CCD04SMNCONFIG", "CCD05SMNCONFIG", "CCD06SMNCONFIG", "CCD07SMNCONFIG", "CCD08SMNCONFIG", "CCD09SMNCONFIG", "CCD10SMNCONFIG", "CCD11SMNCONFIG"]:
					# prefix 'CCD00SMNCONFIG' namespace 'SMNCCD::CCDCCXSEC0' (spec 'CCD00SMNCONFIGx0005C000...x0005C108')
					# prefix 'CCD00SMNCONFIG' namespace 'SMNCCD::CCDKPX1CCD' (spec 'CCD00SMNCONFIGx0005C800...x0005C908')
					# ...
					result[spec] = namespace
				elif prefix in ["CCD00MP5MMIOPRIVATE", "CCD01MP5MMIOPRIVATE", "CCD02MP5MMIOPRIVATE", "CCD03MP5MMIOPRIVATE", "CCD04MP5MMIOPRIVATE", "CCD05MP5MMIOPRIVATE", "CCD06MP5MMIOPRIVATE", "CCD07MP5MMIOPRIVATE", "CCD08MP5MMIOPRIVATE", "CCD09MP5MMIOPRIVATE", "CCD10MP5MMIOPRIVATE", "CCD11MP5MMIOPRIVATE"]:
					# prefix 'CCD00MP5MMIOPRIVATE' namespace 'MPCCD::MP5CRU' (spec 'CCD00MP5MMIOPRIVATEx00000000...x00000928')
					# prefix 'CCD00MP5MMIOPRIVATE' namespace 'MPCCD::MP5MMU' (spec 'CCD00MP5MMIOPRIVATEx00010000...x00010240')
					# prefix 'CCD00MP5MMIOPRIVATE' namespace 'MPCCD::MP5SMNIF' (spec 'CCD00MP5MMIOPRIVATEx00020000...x0002024C')
					# prefix 'CCD00MP5MMIOPRIVATE' namespace 'MPCCD::MP5ROM' (spec 'CCD00MP5MMIOPRIVATEx00060000...x00060028')
					# prefix 'CCD00MP5MMIOPRIVATE' namespace 'MPCCD::MP5DFP' (spec 'CCD00MP5MMIOPRIVATEx000F0000...x000F0010')
					result[spec] = namespace
				elif prefix in ["CCD00MP5MMIOPUBLIC", "CCD01MP5MMIOPUBLIC", "CCD02MP5MMIOPUBLIC", "CCD03MP5MMIOPUBLIC", "CCD04MP5MMIOPUBLIC", "CCD05MP5MMIOPUBLIC", "CCD06MP5MMIOPUBLIC", "CCD07MP5MMIOPUBLIC", "CCD08MP5MMIOPUBLIC", "CCD09MP5MMIOPUBLIC", "CCD10MP5MMIOPUBLIC", "CCD11MP5MMIOPUBLIC"]:
					# prefix 'CCD00MP5MMIOPUBLIC' namespace 'MPCCD::MP5CRU' (spec 'CCD00MP5MMIOPUBLICx00010000...x00010D1C')
					# prefix 'CCD00MP5MMIOPUBLIC' namespace 'MCA::MP5' (spec 'CCD00MP5MMIOPUBLICx00030000...x0003028C MPCCD::MP5MMU 30430400: MCAMP5x00000000...x000000A8')
					# prefix 'CCD00MP5MMIOPUBLIC' namespace 'SMU::TWIX' (spec 'CCD00MP5MMIOPUBLICx00030600...x0003060C MPCCD::MP5MMU 30600000:  CCD00TWIXCCDSMUTWIXDECx00000000...x00000044')
					result[spec] = namespace
				elif prefix in ["CCD00KPX0CCDPCSCFG", "CCD01KPX0CCDPCSCFG", "CCD02KPX0CCDPCSCFG", "CCD03KPX0CCDPCSCFG", "CCD04KPX0CCDPCSCFG", "CCD05KPX0CCDPCSCFG", "CCD06KPX0CCDPCSCFG", "CCD07KPX0CCDPCSCFG", "CCD08KPX0CCDPCSCFG", "CCD09KPX0CCDPCSCFG", "CCD10KPX0CCDPCSCFG", "CCD11KPX0CCDPCSCFG"]:
					# prefix 'CCD00KPX0CCDPCSCFG' namespace 'MCA::KPX::GMI' (spec 'CCD00KPX0CCDPCSCFGx00000000...x000003AC PCS::DXIO 30900400: MCAKPXGMIx00000000...x000000A8')
					# prefix 'CCD00KPX0CCDPCSCFG' namespace 'PCS::DXIO' (spec 'CCD00KPX0CCDPCSCFGx00000500...x0001AFFC')
					result[spec] = namespace
				elif prefix in ["CCDLOCALSMNCONFIG", "CCDLOCALMP5MMIOPRIVATE", "CCDLOCALMP5MMIOPUBLIC", "CCDLOCALPCS0CCDPCSCFG", "CCDLOCALPCS1CCDPCSCFG", "CCDLOCALKPX0CCDPCSCFG", "CCDLOCALKPX1CCDPCSCFG"]:
					# prefix 'CCDLOCALSMNCONFIG' namespace 'SMNCCD::CCDKPX0CCD' (spec 'CCDLOCALSMNCONFIGx0005C000...x0005C108 SMNCCD::CCDCCXSEC0 40200000: CCDLOCALSMNCONFIGx0005C800...x0005C908 SMNCCD::CCDKPX1CCD 40200000:  CCDLOCALSMNCONFIGx0005CA00...x0005CB08')
					# prefix 'CCDLOCALSMNCONFIG' namespace 'SMNCCD::CCDPCS1CCD' (spec 'CCDLOCALSMNCONFIGx0005CC00...x0005CD08')
					# ...
					result[spec] = namespace
				else:
					if (prefix + "x") in result:
						x_namespace = result[prefix + "x"]
						if x_namespace != namespace:
							raise_namespace_error(prefix)
						assert x_namespace == namespace, (prefix, namespace, x_namespace)
					result[prefix + "x"] = namespace
	return result

namespace_by_prefix = calculate_namespaces()

def extract_nice_name(spec, nuke_pattern=True):
	"""
	>>> extract_nice_name("foo (bar::baz)")
	'bar::baz'
	"""
	if nuke_pattern:
		# get rid of pattern
		i = spec.find("[")
		j = spec.find("]", i + 1)
		if i == -1:
			assert j == -1
		else:
			assert j != -1
			pattern = spec[i + 1:j]
			match = re_pattern.match(pattern)
			if match:
				assert len(match.group(1)) == len(match.group(2))
				patternlen = len(match.group(1))
			else:
				patternlen = 1
			spec = spec[:i] + pattern.replace(".", "_") + "_" + spec[j + 1:]
			#if spec.startswith("ENET[0...3]BAR0x"):
			# FIXME	assert False, spec
		if i == -1 and j == -1 and spec.find("...") != -1:
			spec, *nice_name = spec.split("(")
			spec, b = spec.split("...")
			spec = spec + "_etc"
			if len(nice_name) > 0 and nice_name[0].strip().find("::") != -1:
				spec = "{} ({}".format(spec, nice_name[0])
	#if spec.startswith("ENET") and spec.find("::") == -1:
	#FIXME	assert False, spec
	if spec.startswith("Table "):
		if spec.find("::") != -1 and spec.find(".") == -1 and spec.find("[") == -1 and spec.count("(") <= spec.count(")") and spec.count("(") > 0:
			# TODO: Warn once
			warning("Disregarding '::' name in {!r} even though it kinda looks like a register".format(spec))
		return spec
	elif spec.find("::") != -1 and spec.find(".") == -1 and spec.find("[") == -1 and spec.count("(") <= spec.count(")") and spec.count("(") > 0:
		_, name = spec.split("(", 1)
		name, *_ = name.split(")", 1)
		assert name.find("::") != -1
		#assert not spec.startswith("BXXD00"), (spec, name)
		name = name.rstrip(")").strip()
		return name
	else:
		if spec.startswith("Table ") or spec.find("x") == -1:
			return spec
		elif spec.startswith("PMx000001FF"):
			return "FCH::PM2::{}".format(spec)
		elif spec.startswith("PMx5F_"):
			return "FCH::PM::RTCEXT::{}".format(spec)
		elif spec.startswith("USBCONTAINER0x0007") or spec.startswith("USBCONTAINER1x0007"):
			return "USB31::USBCONTAINERS0REGCNTR0::{}".format(spec)
		for prefix, namespace in reverse(sorted(namespace_by_prefix.items())): # this makes sure that longer matches are tried first
			if spec.startswith(prefix):
				return "{}::{}".format(namespace, spec)
		# These are for the old (2017) public PPRs which don't always have a namespace map
		if spec == "IOx0CF8" or spec == "IOx0CFC":
			return "IO::{}".format(spec)
		elif spec.startswith("SMMxFEC"):
			return "Core::X86::Smm::{}".format(spec)
		elif spec.startswith("APICx"):
			return "Core::X86::Apic::{}".format(spec)
		elif spec.startswith("PMCx"):
			return "Core::X86::Pmc::Core::{}".format(spec)
		elif spec.startswith("L3PMCx06"):
			return "Core::X86::Pmc::L3::{}".format(spec)
		elif spec.startswith("GPUF0REGx03"):
			return "OSS::HDP::{}".format(spec)
		elif spec.startswith("GPUF0REGx049") or spec.startswith("GPUF0REGx050"):
			return "OSS::SDMA0::{}".format(spec)
		elif spec.startswith("GPUF0REGx"):
			return "OSS::OSSSYS::{}".format(spec)
		assert False, spec # match for prefix in namespace map
		return spec

		# return spec.strip().rstrip(")").strip()

re_bit_range = re.compile(r"^([0-9]+):([0-9]+)$")

RegisterInstanceSpec = namedtuple("RegisterInstanceSpec", ["logical_mnemonic", "physical_mnemonic", "variable_definitions"])
re_alias = re.compile(r"(_alias[A-Za-z]+)")
re_direct_instance_number = re.compile(r"^_n[0-9]+$")

def parse_RegisterInstanceSpecs(prefix, context_string):
        """
        $ grep _alias prefix |sed -e 's@^.*\(_alias[^;: []*\)[;: [].*$@\1@' |sort |uniq
        _alias
        _aliasHOST
        _aliasHOSTLEGACY
        _aliasHOSTPRI
        _aliasHOSTSEC
        _aliasHOSTSWUS
        _aliasIO
        _aliasMSR
        _aliasMSRLEGACY
        _aliasMSRLSLEGACY
        _aliasSMN
        _aliasSMNCCD
        _aliasSMNPCI
        """
        prefix = prefix.split("\n")
        instances = {} # alias kind -> list of RegisterInstanceSpec
        in_instance_part = False
        for row in prefix:
            _, row = strip_off_rwops(row) # TODO: check that rwops is only given once
            #info("ROW {}".format(row))
            if not in_instance_part:
                if row.startswith("_"):
                    in_instance_part = True
                else:
                    continue
            x = list(reversed(list(unroll_inst_pattern(row))))
            aliaskind = row.split(";")[0].strip()
            if aliaskind.find("_alias") != -1:
                aliaskind = aliaskind[aliaskind.find("_alias") + len("_alias"):]
            elif len(x) > 0 and all(item.physical_mnemonic.startswith("MSR") for item in x): # Work around AMD doc bug where "_aliasMSR" is missing
                info("Unknown access method {} in context {}--assuming 'MSR'".format(aliaskind, context_string))
                aliaskind = "MSR"
            elif len(x) > 0 and all(item.physical_mnemonic.startswith("APICx") for item in x): # Work around AMD doc bug where "_aliasHOST" is missing
                info("Unknown access method {} in context {}--assuming 'HOST'".format(aliaskind, context_string))
                aliaskind = "HOST"
            elif len(x) > 0 and all(item.physical_mnemonic.startswith("CPUID_") for item in x): # Put "CPUID" into its own address space
                info("Note: Unknown access method {} in context {}--assuming 'CPUID'".format(aliaskind, context_string))
                aliaskind = "CPUID"
            #elif len(x) > 0 and all(item.physical_mnemonic.startswith("D18") for item in x) and aliaskind.startswith("FabricIndirectConfigAccessAddress"): # Genoa
            #    assert False, x
            #    aliaskind = "HOST" # FIXME:could also be SMN
            #    # TODO: We could process a lot more of aliaskind.
            #    # (Format: "FabricIndirectConfigAccessAddress[CfgRegInstID=0x2C, IndCfgAccFuncNum=0, IndCfgAccRegNum=0x024]")
            #    # Synth Milan-style DataPortWrite for now
            #    row.append("DataPortWrite=DF::FabricConfigAccessControl")
            else:
                warning("Unknown access method {} in context {}--the user probably won't be able to use the register. Prefix: {!r}".format(aliaskind, context_string, prefix))
                #if aliaskind.startswith("FabricIndirectConfigAccessAddress"): # Genoa
                #    import pdb
                #    pdb.set_trace()
            if aliaskind not in instances:
                instances[aliaskind] = []
            instances[aliaskind] += x #.append(x)
        return instances

class TableDefinition(object):
    def __init__(self, spectuple, context_string=None):
        prefix, spec = spectuple
        extra = {}
        for line in prefix.split("\n"):
            extra, _ = strip_off_rwops(line.strip())
            if extra:
                break
        self.access = extra.get("access")
        self.resetValue = extra.get("Reset")
        # Note: strip_off_rwops also strips off the access mode and reset value.
        # ("\n".join(line for line in prefix.split("\n") if not strip_off_rwops(line.strip())[1].strip().startswith("_"))).strip()
        description = []
        for line in prefix.split("\n"):
            q = strip_off_rwops(line.strip())[1]
            if q.strip().startswith("_"):
                if q.find("MSR") != -1: # it's useful to know whether those are per-thread, per-core or whatever.
                    description.append(q)
            else:
                description.append(line)
        self.description = "\n".join(description).strip()
        if spec[-1:] == [[]]:
          spec = spec[:-1]
        self.spec = spec
        self.bits = None
        self.size = None
        self.resetMask = 0
        if spec[0] == ["Bits", "Description"]: # and (context_string or "").find("D18F0x050") == -1 and context_string.find("D18F1x200") == -1:
            self.bits = []
            bitspecs = []
            #info("context_string {}, spec {}".format(context_string, spec))
            unused_bits = None
            for bits, description in spec[1:]:
                name, *_ = description.split(".")
                name = name.strip()
                name, *_ = name.split(":")
                name = name.strip()
                multi_bits = re_bit_range.match(bits)
                if multi_bits:
                  max_bit = int(multi_bits.group(1))
                  min_bit = int(multi_bits.group(2))
                else:
                  max_bit = int(bits)
                  min_bit = int(bits)
                if unused_bits is None:
                  assert max_bit == 31 or max_bit == 63 or max_bit == 7 or max_bit == 15, max_bit
                  self.size = max_bit + 1
                  # assumes that the first bit parsed is not mangled
                  unused_bits = set([i for i in range(max_bit + 1)])
                for bit in range(min_bit, max_bit + 1):
                  assert bit in unused_bits, context_string
                  unused_bits.remove(bit)
                if name == "Reserved":
                  for bit in range(min_bit, max_bit + 1):
                    self.resetMask |= 1 << bit
                else:
                  bitspecs.append(((max_bit, min_bit), name, description))
            self.bits = bitspecs
            assert self.size in [8, 16, 32, 64], (self.size, context_string, prefix)
            self.resetMask = (2 ** self.size - 1) - self.resetMask
            if unused_bits:
              # Problems:
              # * MSRC001_023[0...A] (subtable)
              # * MSRC001_0294 (subtables)
              warning("{}: bits {} not specified.".format(context_string, unused_bits))
        # context_string is a really complete spec, so use it to extract instance information, if possible.
        items = list(unroll_pattern(context_string))
        instance_specs = parse_RegisterInstanceSpecs(prefix, context_string)
        assert instance_specs != {} or (instance_specs == {} and (items is None or len(items) == 0)), (context_string, instance_specs, items)
        self.instances = instance_specs
    def __repr__(self):
        return ";".join(["{}={}".format("{}:{}".format(*bits) if bits[1] != bits[0] else bits[0], name) for bits, name, description in self.bits]) if self.bits is not None else ""
    def __lt__(self, other):
        return self.spec < other.spec

tree = {}
def resolve_path(tree, path, create=False):
	if len(path) == 0:
		return tree
	else:
		key = path[0]
		if key not in tree and create:
			tree[key] = {}
		return resolve_path(tree[key], path[1:], create=create)

names = sorted([((extract_nice_name(v) or v).split("::"), TableDefinition(getattr(phase2_result, k), v)) for k, v in __names.items()])
#print(names)
for path, table_definition in names:
	leaf_name = path[-1].replace("AUDIO_AZ_", "AUDIOAZ").replace("AudioAZ", "AUDIOAZ").replace("Audio_Az", "AUDIOAZ").replace("IOMMU_MMIO", "IOMMUMMIO").replace("SATA_AHCI_P_", "SATA_PORT_").replace("AHCI_SGPIO_", "SATA_SGPIO_").replace("APICx", "Apicx")
	#assert len(path) < 2 or path[1] != "SATA", (path, leaf_name)
	for part in path[:-1]:
		if leaf_name.startswith(part) and leaf_name != "PCS_PERF_COUNTER_DEBUG": # the latter would not be unique after truncation (in Genoa)
			leaf_name = leaf_name[len(part):]
		if leaf_name.startswith("_"):
			leaf_name = leaf_name[1:]
	leaf_name = leaf_name.strip()
	if leaf_name.startswith("x"):
		leaf_name = leaf_name[1:]
	if leaf_name[0] in "0123456789" or (len(leaf_name) > 1 and leaf_name[1] in "0123456789"):
		leaf_name = "I" + leaf_name
	node = resolve_path(tree, path[:-1], create=True)
	assert leaf_name not in node, leaf_name
	node[leaf_name] = table_definition

for toplevel in tree.keys():
	if toplevel.find("x") != -1:
		warning("{} is toplevel.".format(toplevel))

#sys.stdout.reconfigure(encoding='utf-8')
#sys.stdin = sys.stdin.detach()
#sys.stdout = sys.stdout.detach()

from lxml import etree

def text_element(key, text):
  result = etree.Element(key)
  #result.append(etree.TextNode(text))
  result.text = str(text)
  return result

svd_root = etree.Element("device")
svd_root.attrib["schemaVersion"] = "1.3"

svd_root.append(text_element("vendor", "Advanced Micro Devices"))
svd_root.append(text_element("vendorID", "AMD"))
svd_root.append(text_element("name", __model.replace(" ", "_")))
svd_root.append(text_element("series", "AMD Epyc"))
svd_root.append(text_element("version", "0.1")) # FIXME: version of this description, adding CMSIS-SVD 1.1 tags
svd_root.append(text_element("description", __model))
svd_root.append(text_element("licenseText", "AMD devhub under NDA\nDo not distribute"))
# TODO: <cpu> with: <name>, <revision>, <endian>little</endian>, <mpuPresent>, <fpuPresent>, <nvicPrioBits>, <vendorSystickConfig>
svd_root.append(text_element("addressUnitBits", 8)) # min. addressable
svd_root.append(text_element("width", 64)) # bus width # FIXME.

# Set defaults for registers:
svd_root.append(text_element("size", 32))
svd_root.append(text_element("access", "read-write"))
#svd_root.append(text_element("resetValue", "0"))
svd_root.append(text_element("resetMask", "0xFFFFFFFF"))


svd_peripherals = etree.Element("peripherals")
svd_root.append(svd_peripherals)

# TODO: Read "Memory Map - MSR" in tree.
# TODO: Read "Memory Map - Main Memory" in tree.
# Memory_Map___MSR
# Memory_Map___Main_Memory
# Memory_Map___PCICFG
# Memory_Map___SMN
# Memory_Map___SMNCCD
#  It has: IOAPIC, SPI, ESPI, HPET, HCE, SMI, PM, RTCHOST, ASF, SMBUS, WDT, IOIMUX, MISC, GPIO, ACDC, AOAC, I2C, UART, EMMCHC, EMMCCFG
# TODO: Read "Memory Map - PCICFG" in tree.
# TODO: Read "Memory Map - SMN" in tree.

def create_peripheral(name, baseAddress, access="read-write", description=None, groupName=None):
  result = etree.Element("peripheral")
  result.append(text_element("name", name))
  result.append(text_element("description", description or name))
  result.append(text_element("groupName", groupName or "generic"))
  result.append(text_element("baseAddress", baseAddress))
  result.append(text_element("access", access))
  return result

def create_addressBlock(offset, size, usage="registers"):
  result = etree.Element("addressBlock")
  result.append(text_element("offset", offset))
  result.append(text_element("size", size))
  result.append(text_element("usage", usage))
  return result

offset = 0

svd_peripherals_by_path = {}

# This exists in order to be able to emit <alternateRegister> tags
primary_registers_by_absolute_address = {
}

def create_register(table_definition, name, addressOffset, description=None):
  result = etree.Element("register")
  result.append(text_element("name", name))
  result.append(text_element("description", description or name))
  if addressOffset in primary_registers_by_absolute_address:
    result.append(text_element("alternateRegister", primary_registers_by_absolute_address[addressOffset]))
  else:
    primary_registers_by_absolute_address[addressOffset] = name
  result.append(text_element("addressOffset", "0x{:X}".format(addressOffset)))
  result.append(text_element("size", table_definition.size))
  if table_definition.access:
    access = table_definition.access
    # Only put the ones SVD defined (read-only, write-only, read-write, writeOnce, read-writeOnce)
    if access in [
      "Read-write",
      "Read,Write-1-to-clear",
      "Read-write,Volatile",
      "Read-write,Reserved",
      "Read,Error-on-write-1"
      "Volatile",
      "Read-write,Read,Write-1-to-clear",
      "Read,Write-1-to-clear,Volatile",
    ]:
      access = "read-write"
    elif access in [
      "Read-only",
      "Read-only,Volatile",
      "Inaccessible",
    ]:
      access = "read-only"
    elif access in [
      "Write-only",
      "Write-1-to-clear",
    ]:
      access = "write-only"
    else:
      access = access.lower()
    result.append(text_element("access", access))
  if table_definition.resetValue:
    resetValue = table_definition.resetValue
    if resetValue.endswith("h"):
        resetValue = "0x" + resetValue[:-len("h")]
    result.append(text_element("resetValue", resetValue.replace("_", "")))
  result.append(text_element("resetMask", "0x{:X}".format(table_definition.resetMask)))
  if table_definition.access and table_definition.access in [
    "Read,Write-1-to-clear",
    "Read-write,Read,Write-1-to-clear",
    "Read,Write-1-to-clear,Volatile",
  ]:
    result.append(text_element("modifiedWriteValues", "oneToClear"))
  fields = etree.Element("fields")
  result.append(fields)
  bits = table_definition.bits
  for (max_bit, min_bit), name, description in bits:
    field = etree.Element("field")
    field.append(text_element("name", name.replace("[", "_").replace(":", "_").replace("]", "_")))
    field.append(text_element("description", description))
    field.append(text_element("bitRange", "[{}:{}]".format(max_bit, min_bit)))
    # FIXME: access
    # TODO: enumeratedValues, enumeratedValue
    fields.append(field)
  return result

#import pprint
#pprint.pprint(tree)

def clean_up_logical_name(s):
    if s.startswith("_inst"):
        s = s[len("_inst"):]
    if s.endswith("_alias" + selected_access_method):
        s = s[: -len("_alias" + selected_access_method)]
    if s.startswith("_"):
        s = s[1:]
    return s
    #svd_register.append(text_element("dimIndex", ",".join(clean_up(instance.logical_mnemonic) for instance in instances)))

def data_port_encode_error(spec, data_port_base):
    raise Exception("unknown DataPortWrite")

def data_port_encode_ignore(spec, data_port_base):
    return "{}_x{:x}".format(spec, data_port_base)

re_ficaa_offset_pattern = re.compile(r"^D([0-9A-Fa-f]+)F([0-9A-Fa-f]+)x([0-9A-Fa-f_]+)")

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

def data_port_encode_abindex(spec, data_port_base):
    addr = calculate_hex_instance_value(spec)
    # For some reason, AMD docs have 0xCDC in the address *behind* the data port, too.  That's obviously wrong, so drop it.
    assert addr == 0xCDC, addr
    return data_port_base

data_port_encoders = {
    "DF::FabricConfigAccessControl": data_port_encode_ficaa,
    "FCH::AB::ABIndex": data_port_encode_abindex,
}

def process_TableDefinition(peripheral_path, name, vv):
    global offset
    path = *peripheral_path, name
    description = "::".join(path) + "\n" + vv.description
    prefixname = name
    basename = None

    assert selected_access_method in vv.instances
    instances = vv.instances[selected_access_method]

    if selected_alias_reduction_method == "default":
        if selected_access_method == "SMN":
            if "HOST" in vv.instances: # prefer HOST to SMN (i.e. suppress SMN)
                if len(vv.instances["HOST"]) != len(instances):
                    #assert len(vv.instances["HOST"]) == len(instances), (path, vv.instances["HOST"], instances)
                    warning("Register {} has different instances accessible via SMN vs HOST.  Therefore, providing both aliases.".format(path))
                else:
                    return
        elif selected_access_method == "IO":
            if "HOST" in vv.instances:
                assert len(vv.instances["HOST"]) == len(instances)
                return
            if "SMN" in vv.instances:
                assert len(vv.instances["SMN"]) == len(instances)
                return

    selected_instances = []
    for instance in instances:
        vars = dict(definition.split("=", 1) for definition in instance.variable_definitions)
        FabricIndirectConfigAccessAddresses = [(k, v) for k, v in vars.items() if k.startswith("FabricIndirectConfigAccessAddress")]
        data_port_write = vars.get("DataPortWrite", "direct")
        if data_port_write == "direct" and len(FabricIndirectConfigAccessAddresses) == 1: # Genoa: Fake a data port write so our handling picks it up.
            data_port_write = "DF::FabricConfigAccessControl"
            # TODO: We could also check FabricIndirectConfigAccessAddresses[0] for sanity.
        # Assumption: all the data port write are the same for one register
        if selected_data_port_write == data_port_write:
            selected_instances.append(instance)
    if selected_instances == []:
        #info("Skipping {} because of different data port write".format(name))
        return
    instances = selected_instances
    data_port_encoder = data_port_encoders.get(selected_data_port_write, data_port_encode_error)

    try:
        addresses = [calculate_hex_instance_value(instance.resolve_physical_mnemonic(data_port_encoder)) for instance in instances]
        addressOffset = addresses[0]
    except Exception as e:
        #import traceback
        #traceback.print_exc()
        addresses = []
        error("Could not calculate addresses of register {}: {}: {}.".format(name, e.__class__.__name__, e))
        if selected_error_handling != "keep-registers-with-errors":
            return
        info("^: Defaulting to nonsense (very low) value for a dummy entry.")
        offset += 4
        description = description + "\n(This register was misdetected--and for debugging, all the instances follow here in the description)\n{}\n".format(traceback.format_exc()) + ("\n".join(instance.resolve_physical_mnemonic(data_port_encode_ignore) for instance in instances))
        addressOffset = offset

    if len(addresses) > 1:
        name = "{}_{}".format(prefixname, clean_up_logical_name(instances[0].logical_mnemonic))
        basename = name
    if peripheral_path not in svd_peripherals_by_path:
        svd_peripheral = create_peripheral("_".join(peripheral_path), 0, "read-write")
        #svd_addressBlock = create_addressBlock(0, 100, "registers") # FIXME
        # TODO: <interrupt> as child of peripheral.
        #svd_peripheral.append(svd_addressBlock)
        svd_peripherals.append(svd_peripheral)
        svd_registers = etree.Element("registers")
        svd_peripheral.append(svd_registers)
        peripheral_state = {} # for detecting strides etc.
        svd_peripherals_by_path[peripheral_path] = svd_peripheral, svd_registers, peripheral_state
    else:
        svd_peripheral, svd_registers, peripheral_state = svd_peripherals_by_path[peripheral_path]

    svd_register = create_register(vv, name, addressOffset, description=description)
    svd_registers.append(svd_register)

    reference_peripheral_name = "_".join(peripheral_path)
    for instance, addressOffset in zip(instances[1:], addresses[1:]):
        derived_register = etree.Element("register")
        derived_register.attrib["derivedFrom"] = "{}.{}".format(reference_peripheral_name, basename)
        name = "{}_{}".format(prefixname, clean_up_logical_name(instance.logical_mnemonic))
        derived_register.append(text_element("name", name))
        #derived_register.append(text_element("description", description)
        #addressOffset = calculate_hex_instance_value(instance.resolved_physical_mnemonic)
        derived_register.append(text_element("addressOffset", "0x{:X}".format(addressOffset)))
        derived_register.append(text_element("size", vv.size)) # To make phase4 easier
        svd_registers.append(derived_register)
        #svd_register.append(text_element("dimIndex", ",".join(clean_up_logical_name(instance.logical_mnemonic) for instance in instances)))

def finish_TableDefinition(peripheral_path):
    if peripheral_path in svd_peripherals_by_path:
        svd_peripheral, svd_registers, peripheral_state = svd_peripherals_by_path[peripheral_path]

def traverse1(tree, path):
  global offset
  for k, v in tree.items():
    if isinstance(v, TableDefinition): # assume already processed
      continue
    if k.startswith("Table "): # skip for now
      continue

    # traverse so far down that one of the children is a tabledefinition.  That then is (at least) a peripheral.

    has_peripheral = False
    for kk, vv in v.items():
      if isinstance(vv, TableDefinition):
        has_peripheral = True

    if has_peripheral:
      peripheral_path = tuple(path + [k])
      assert peripheral_path not in svd_peripherals_by_path
      for kk, vv in v.items():
        if isinstance(vv, TableDefinition):
          if selected_access_method in vv.instances and vv.bits:
            process_TableDefinition(peripheral_path, kk, vv)
          elif len(vv.instances) == 0:
            warning("Register {} has no instances at all.  It thus cannot be accessed by the user.".format("::".join(path + [k, kk])))

      finish_TableDefinition(peripheral_path)
    else:
      traverse1(v, path + [k])

traverse1(tree, [])

sys.stdout.flush()
et = etree.ElementTree(svd_root)
#etree.register_namespace("", "urn:iso:std:iso:20022:tech:xsd:CMSIS-SVD.xsd")
#etree.register_namespace("xs", "http://www.w3.org/2001/XMLSchema-instance")
XS = "http://www.w3.org/2001/XMLSchema-instance"
svd_root.set("{%s}noNamespaceSchemaLocation" % XS, "CMSIS-SVD.xsd")
#svd_root.attrib["xmlns:xs"] = "http://www.w3.org/2001/XMLSchema-instance"
#svd_root.attrib["xs:noNamespaceSchemaLocation"] = "CMSIS-SVD.xsd"
#svd_root.set("xmlns", "urn:iso:std:iso:20022:tech:xsd:CMSIS-SVD.xsd")
#svd_root.set("xmlns:xs", "http://www.w3.org/2001/XMLSchema-instance")

et.write(sys.stdout.buffer, pretty_print=True)
sys.stdout.flush()

#with etree.xmlfile(sys.stdout, close=False) as SVD:
#  with SVD.element("A"):
#     SVD.write(b"hello")
