# Access methods that are out of scope

* `HOSTLEGACY` access method
  * `DataPortWrite=FCH::PM::RTCEXTINDEX` data port write
  * `DataPortWrite=FCH::IOAPIC::IO_REGISTER_SELECT_REGISTER[indirect_address_offset]` data port write
* `DataPortWrite=FCH::AB::ABIndex` (via `IO` access method)
* `DataPortWrite=FCH::IO::PCI_INTR_INDEX` (via `IO` access method)
* `DataPortWrite=UMC::CTRL::ApbCmd[Address]` (via `SMN` access method)
