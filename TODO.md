* Handle "_msi64bit1" addresses.
* Handle SMN FICAA registers.
* SVDs for weird access methods: HOSTPRI, HOSTSEC, MSRLEGACY, MSRLSLEGACY
* Infer peripheral from groups of adjacent registers.
* Some PCIInfo blocks are not yet grouped.  Add settings to settings.py.  Find them by: grep VENDOR_ID.*unsorted phase4_host.svd  |wc -l: HOST: 68 (DEVICE_VENDOR_ID: 24); SMN: 142 (DEVICE_VENDOR_ID: 28)
