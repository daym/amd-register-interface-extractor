* Handle "_msi64bit1" addresses (error message "ValueError: invalid literal.*" gives more details).
* Handle MSRs and mark them specially (error message "ERROR unrolling: logical instances are.*MSR.*impossible" gives more details)
* Handle HOSTSWUS.*PCIEs and mark them specially (error message "ERROR unrolling: logical instances are.*PCIE.*impossible" gives more details)
* Some PCIInfo blocks are not yet grouped.  Add settings to settings.py.  Find them by: grep VENDOR_ID.*unsorted phase4_host.svd  |wc -l: HOST: 68 (DEVICE_VENDOR_ID: 24); SMN: 142 (DEVICE_VENDOR_ID: 28)
* Generate SVDs for weird access methods: HOSTPRI, HOSTSEC, MSRLEGACY, MSRLSLEGACY
