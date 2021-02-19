#!/usr/bin/env python3

import sys

import re
import shutil
import phase2_result
from phase2_result import __names, __model
import os
import pprint
from collections import namedtuple
from rwops import strip_off_rwops
from unroller import unroll_inst_pattern, RegisterInstanceSpec

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
	if spec.find("::") != -1 and spec.find(".") == -1 and spec.find("[") == -1 and spec.count("(") <= spec.count(")") and spec.count("(") > 0:
		#print("SPEC", spec, file=sys.stderr)
		_, name = spec.split("(", 1)
		name, *_ = name.split(")", 1)
		assert name.find("::") != -1
		#assert not spec.startswith("BXXD00"), (spec, name)
		name = name.rstrip(")").strip()
		return name
	else:
		# See page 2946 "List of Namespaces"
		# See page 2953 "Memory Map - Main Memory"
		if spec.startswith("ABx"):
			return "FCH::AB::{}".format(spec) # Not that nice...
		elif spec.startswith("ACDCx"):
			return "FCH::TMR::{}".format(spec) # Not that nice...
		elif spec.startswith("AOACx"):
			return "FCH::AOAC::{}".format(spec) # Not that nice...
		elif spec.startswith("APICx"):
			return "Core::X86::Apic::{}".format(spec) # Not that nice...
		elif spec.startswith("ASFx"):
			return "FCH::ASF::{}".format(spec) # Not that nice...
		elif spec.startswith("CPUID_"):
			return "Core::X86::Cpuid::{}".format(spec)
		elif spec.startswith("D14F0x"):
			return "FCH::SMBUSPCI::{}".format(spec) # Not that nice...
		elif spec.startswith("D14F3x"):
			return "FCH::ITF::LPC::{}".format(spec) # Not that nice...
		elif spec.startswith("D18F0x") or spec.startswith("D18F1x") or spec.startswith("D18F2x") or spec.startswith("D18F3x") or spec.startswith("D18F4x") or spec.startswith("D18F5x") or spec.startswith("D18F6x"):
			return "DF::{}".format(spec) # Not that nice...
		elif spec.startswith("DFPMCx"):
			return "DF::PMC::{}".format(spec) # Not that nice...
		elif spec.startswith("HPETx"):
			return "FCH::TMR::HPET::{}".format(spec)
		elif spec.startswith("GPIOx"): # FIXME.
			return "GPIOx::{}".format(spec) # FIXME.
		elif spec.startswith("HDTx"): # TWO
			return "HDT::{}".format(spec) # Not that nice...
		elif spec.startswith("HCEx"):
			return "FCH::USBLEGACY::{}".format(spec) # Not that nic
		elif spec.startswith("FCHSDPx"):
			return "FCH::SDP::{}".format(spec.replace("FCHSDPx00004_x", "")) # not that nice...

		elif spec.startswith("SMBUSx"):
			return "FCH::SMBUS::{}".format(spec) # Not that nice...
		elif spec.startswith("SMIx"):
			return "FCH::SMI::{}".format(spec) # Not that nice...
		elif spec.startswith("SMMx"):
			return "Core::X86::Smm::{}".format(spec) # Not that nic
		elif spec.startswith("UMC0CHx"):
			return "UMC::CH::{}".format(spec) # Not that nice...
		elif spec.startswith("UMC0CTLx"):
			return "UMC::CTRL::{}".format(spec) # Not that nice...
		elif spec.startswith("PMx"):
			return "FCH::PM::{}".format(spec)
		elif spec.startswith("PM2x"):
			return "FCH::PM2::{}".format(spec) # Not that nice...
		elif spec.startswith("PMCx"):
			return "Core::X86::Pmc::Core::{}".format(spec)
		elif spec.startswith("SPIx"):
			return "FCH::ITF::SPI::{}".format(spec) # Not that.
		elif spec.startswith("SBTSIx"):
			return "SBTSI::{}".format(spec) # Not that nice...
		elif spec.startswith("SBRMIx"):
			return "SBRMI::{}".format(spec) # Not that nice...
		elif spec.startswith("UARTx"):
			return "FCH::UART::{}".format(spec) # Not that nice...
		elif spec.startswith("UMC0CHx"):
			return "UMC::CH::{}".format(spec) # Not that nice...
		elif spec.startswith("UMC0CTLx"):
			return "UMC::CTRL::{}".format(spec) # Not that nice...
		elif spec.startswith("MISCx"):
			return "FCH::MISC::{}".format(spec)
		elif spec.startswith("IOx"):
			return "IO::{}".format(spec) # Not that nice...
		elif spec.startswith("UMCPMCx"): # Performance counters...
			return "UMC::PMC::{}".format(spec) # Not that nice...
		elif spec.startswith("IOAPICx") or spec.startswith("IOApicx"):
			return "IOAPIC::{}".format(spec) # Not that nice...
		elif spec.startswith("I2Cx"):
			return "FCH::I2C::{}".format(spec) # Not that nice...

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
            #print("ROW", row, file=sys.stderr)
            if not in_instance_part:
                if row.startswith("_"):
                    in_instance_part = True
                else:
                    continue
            x = list(unroll_inst_pattern(row))
            aliaskind = row.split(";")[0].strip()
            if aliaskind.find("_alias") != -1:
                aliaskind = aliaskind[aliaskind.find("_alias") + len("_alias"):]
            if aliaskind not in instances:
                instances[aliaskind] = []
            instances[aliaskind] += x #.append(x)
        return instances

class TableDefinition(object):
    def __init__(self, spectuple, context_string=None):
        prefix, spec = spectuple
        if spec[-1:] == [[]]:
          spec = spec[:-1]
        self.spec = spec
        self.bits = None
        self.size = None
        if spec[0] == ["Bits", "Description"]: # and (context_string or "").find("D18F0x050") == -1 and context_string.find("D18F1x200") == -1:
            self.bits = []
            bitspecs = []
            #print(spec, file=sys.stderr)
            #print(context_string, spec, file=sys.stderr)
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
                bitspecs.append(((max_bit, min_bit), name, description))
            self.bits = bitspecs
            if unused_bits:
              # Problems:
              # * MSRC001_023[0...A] (subtable)
              # * MSRC001_0294 (subtables)
              print("warning: {}: bits {} not specified.".format(context_string, unused_bits), file=sys.stderr)
        # context_string is a really complete spec, so use it to extract instance information, if possible.
        items = list(unroll_pattern(context_string))
        instance_specs = parse_RegisterInstanceSpecs(prefix, context_string)
        #print("TABLE_DEFINITION", context_string, instance_specs)
        #print("TABLE_DEFINITION {} ITEMS", items)
        #print("PREFIX {}".format(prefix), file=sys.stderr)
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

# TODO: Unroll the names if specified like "[...]"; also provide one of the things WITHOUT the patterns in it.
# TODO: Autogenerate accessors--if possible--for each of those.
# UARTx[2E...3F]8 [DLL] (FCH::UART::DLL)
#  dim=number of elements
#  dimIncrement=address increment per element
#  dimIndex=? "0-9"|"A-F"|"foo,bar,baz"
#  dimName=? (only valid in <cluster> context)
#  dimArrayIndex=?

names = sorted([((extract_nice_name(v) or v).split("::"), TableDefinition(getattr(phase2_result, k), v)) for k, v in __names.items()])
#print(names)
for path, table_definition in names:
	#sys.stderr.write(repr(path))
	#sys.stderr.write("\n")
	leaf_name = path[-1].replace("AUDIO_AZ_", "AUDIOAZ").replace("AudioAZ", "AUDIOAZ").replace("Audio_Az", "AUDIOAZ").replace("IOMMU_MMIO", "IOMMUMMIO").replace("SATA_AHCI_P_", "SATA_PORT_").replace("AHCI_SGPIO_", "SATA_SGPIO_").replace("APICx", "Apicx")
	#assert len(path) < 2 or path[1] != "SATA", (path, leaf_name)
	for part in path[:-1]:
		if leaf_name.startswith(part):
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
		print("Warning: {} is toplevel.".format(toplevel), file=sys.stderr)

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

def create_peripheral(name, version, baseAddress, size, access="read-write", description=None, groupName=None):
  result = etree.Element("peripheral")
  result.append(text_element("name", name))
  result.append(text_element("version", version))
  result.append(text_element("description", description or name))
  result.append(text_element("groupName", groupName or "generic"))
  result.append(text_element("baseAddress", baseAddress))
  result.append(text_element("size", size))
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

def create_register(peripheral_path, table_definition, name, description=None):
  global offset
  if peripheral_path not in svd_peripherals_by_path:
        svd_peripheral = create_peripheral("_".join(peripheral_path), "1.0", 0, 100, "read-write") # FIXME
        svd_addressBlock = create_addressBlock(0, 100, "registers") # FIXME
        # TODO: <interrupt> as child of peripheral.
        svd_peripheral.append(svd_addressBlock)
        svd_peripherals.append(svd_peripheral)
        svd_registers = etree.Element("registers")
        svd_peripheral.append(svd_registers)
        svd_peripherals_by_path[peripheral_path] = svd_peripheral, svd_addressBlock, svd_registers
  else:
        svd_peripheral, svd_addressBlock, svd_registers = svd_peripherals_by_path[peripheral_path]
  result = etree.Element("register")
  result.append(text_element("name", name))
  result.append(text_element("description", description or name))
  result.append(text_element("addressOffset", str(offset))) # FIXME
  offset += 4
  result.append(text_element("size", table_definition.size))
  # FIXME: access.
  # FIXME: resetValue, resetMask.
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
  svd_registers.append(result)
  return result

#import pprint
#pprint.pprint(tree)

selected_access_method = "HOST"

def traverse1(tree, path):
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
      for kk, vv in v.items():
        if isinstance(vv, TableDefinition):
          if selected_access_method in vv.instances:
            instances = vv.instances[selected_access_method]
            #for instance in instances:
            #  print("INSTANCE", instance, instance.resolved_physical_mnemonic, file=sys.stderr)
            name = kk # "_".join(path + [k, kk])
            if vv.bits:
              svd_register = create_register(peripheral_path, vv, name, description="::".join(path + [k, kk]) + "\n" + "\n".join(instance.resolved_physical_mnemonic for instance in instances))
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
