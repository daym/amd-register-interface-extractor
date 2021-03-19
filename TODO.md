* Handle "_msi64bit1" addresses.
* Generate SVDs for weird access methods: HOSTPRI, HOSTSEC, MSRLEGACY, MSRLSLEGACY
* Some PCIInfo blocks are not yet grouped.  Add settings to settings.py.  Find them by: grep VENDOR_ID.*unsorted phase4_host.svd  |wc -l: HOST: 68 (DEVICE_VENDOR_ID: 24); SMN: 142 (DEVICE_VENDOR_ID: 28)
* Handle MSRs and mark them specially (error message "ERROR unrolling: logical instances are.*MSR.*impossible" gives more details)
* Handle HOSTSWUS.*PCIEs and mark them specially (error message "ERROR unrolling: logical instances are.*PCIE.*impossible" gives more details)
* Special-case "_ccd\[7:0\]_pcs1" and "_ccd\[7:0\]_pcs0".  Those are the only NON-implicit ccd patterns (which should, after all, be unrolled).
