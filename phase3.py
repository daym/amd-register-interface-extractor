#!/usr/bin/env python3

import sys
import getopt
import re
import shutil
import phase2_result
from phase2_result import __names, __model
import os
import pprint
from collections import namedtuple
from rwops import strip_off_rwops
from unroller import unroll_inst_pattern, RegisterInstanceSpec
from hexcalculator import calculate_hex_instance_value as internal_calculate_hex_instance_value

selected_access_method = "HOST"
selected_data_port_write = "direct"

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
            x = reversed(list(unroll_inst_pattern(row)))
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
        extra = {}
        for line in prefix.split("\n"):
            extra, _ = strip_off_rwops(line.strip())
            if extra:
                break
        self.access = extra.get("access")
        self.resetValue = extra.get("Reset")
        # Note: strip_off_rwops also strips off the access mode and reset value.
        self.description = ("\n".join(line for line in prefix.split("\n") if not strip_off_rwops(line.strip())[1].strip().startswith("_"))).strip()
        if spec[-1:] == [[]]:
          spec = spec[:-1]
        self.spec = spec
        self.bits = None
        self.size = None
        self.resetMask = 0
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

def create_peripheral(name, version, baseAddress, access="read-write", description=None, groupName=None):
  result = etree.Element("peripheral")
  result.append(text_element("name", name))
  result.append(text_element("version", version))
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

def create_register(table_definition, name, addressOffset, description=None):
  result = etree.Element("register")
  result.append(text_element("name", name))
  result.append(text_element("description", description or name))
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
    if table_definition.access in [
      "Read,Write-1-to-clear",
      "Read-write,Read,Write-1-to-clear",
      "Read,Write-1-to-clear,Volatile",
    ]:
      result.append(text_element("modifiedWriteValues", "oneToClear"))
    result.append(text_element("access", access))
  if table_definition.resetValue:
    resetValue = table_definition.resetValue
    if resetValue.endswith("h"):
        resetValue = "0x" + resetValue[:-len("h")]
    result.append(text_element("resetValue", resetValue.replace("_", "")))
  result.append(text_element("resetMask", "0x{:X}".format(table_definition.resetMask)))
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

def induce_access_array(addresses):
    """ Tries to induce a regular array from ADDRESSES.
        Returns (first_address, step, count) if that was possible.
        Otherwise, returns (first_address, None, count). """
    previous_address = addresses[0]
    previous_step = None
    even_steps = True
    for address in addresses[1:]:
        step = address - previous_address
        if previous_step is None:
            previous_step = step
        elif step != previous_step:
            return addresses[0], None, len(addresses)
    if previous_step is not None and previous_step < 0: # negative step is not supported!
        previous_step = None
    return addresses[0], previous_step, len(addresses)

def process_TableDefinition(peripheral_path, name, vv):
    global offset
    path = *peripheral_path, name
    description = "::".join(path) + "\n" + vv.description
    prefixname = name
    basename = None

    assert selected_access_method in vv.instances
    instances = vv.instances[selected_access_method]
    global_data_port_write = None
    for instance in instances:
        vars = dict(definition.split("=", 1) for definition in instance.variable_definitions)
        data_port_write = vars.get("DataPortWrite", "direct")
        if global_data_port_write is None:
            global_data_port_write = data_port_write
        # Assumption: all the data port write are the same for one register
        assert data_port_write == global_data_port_write
    if selected_data_port_write != global_data_port_write:
        #print("info: Skipping {} because of different data port write".format(name), file=sys.stderr)
        return

    try:
        addresses = [calculate_hex_instance_value(instance.resolved_physical_mnemonic) for instance in instances]
        first_address, step, count = induce_access_array(addresses)
        addressOffset = addresses[0]
    except Exception as e:
        #import traceback
        #traceback.print_exc()
        addresses = []
        print("Error: Could not calculate addresses of register {}: {}.  Defaulting to nonsense (very low) value for a dummy entry.".format(name, e), file=sys.stderr)
        offset += 4
        description = description + "\n(This register was misdetected--and for debugging, all the instances follow here in the description:)\n" + ("\n".join(instance.resolved_physical_mnemonic for instance in instances))
        addressOffset = offset
        step = None

    if len(addresses) > 1:
        if step is not None: # regular array
            name = name + "[%s]"
        else: # unroll manually
            name = "{}_{}".format(prefixname, clean_up_logical_name(instances[0].logical_mnemonic))
            basename = name
    if peripheral_path not in svd_peripherals_by_path:
        svd_peripheral = create_peripheral("_".join(peripheral_path), "1.0", 0, "read-write") # FIXME
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

    if step is not None:
        # Create array of registers
        if len(instances) > 1:
            svd_register.append(text_element("dim", len(instances)))
            svd_register.append(text_element("dimIncrement", "0x{:X}".format(step)))
        if step == 0:
            print("Error: step is 0 for register {} instances--only the first register will be able to be accessed".format(name), file=sys.stderr)
    else: # manually unroll
        for instance, addressOffset in zip(instances[1:], addresses[1:]):
            derived_register = etree.Element("register")
            derived_register.attrib["derivedFrom"] = basename
            name = "{}_{}".format(prefixname, clean_up_logical_name(instance.logical_mnemonic))
            derived_register.append(text_element("name", name))
            #derived_register.append(text_element("description", description)
            #addressOffset = calculate_hex_instance_value(instance.resolved_physical_mnemonic)
            derived_register.append(text_element("addressOffset", "0x{:X}".format(addressOffset)))
            #derived_register.append(text_element("size", table_definition.size))
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
      for kk, vv in v.items():
        if isinstance(vv, TableDefinition):
          if selected_access_method in vv.instances and vv.bits:
            process_TableDefinition(peripheral_path, kk, vv)
      finish_TableDefinition(peripheral_path)
    else:
      traverse1(v, path + [k])

opts, args = getopt.getopt(sys.argv[1:], "m:d:", ["mode=", "data-port-write="])
for k,v in opts:
	if k == "-m" or k == "--mode":
		selected_access_method = v
	elif k == "-d" or k == "--data-port-write":
		selected_data_port_write = v

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
