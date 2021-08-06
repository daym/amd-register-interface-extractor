
.PHONY: all clean distclean validate3 validate4

all: phase7_host.svd phase7_host_ficaa.svd phase7_io.svd phase7_io_abindex.svd phase7_msr.svd phase7_smn.svd phase7_smn_ficaa.svd phase7_smnccd.svd phase7_smnccd_ficaa.svd

include config.mk
include compiler.mk

result.txt: $(if $(PPRVOL1),resultvol1.txt,) $(if $(PPRVOL2),resultvol2.txt,) $(if $(PPRVOL3),resultvol3.txt,) $(if $(PPRVOL4),resultvol4.txt,) $(if $(PPRVOL5),resultvol5.txt,) $(if $(PPRVOL6),resultvol6.txt,) $(if $(PPRVOL7),resultvol7.txt,) $(if $(PPRVOL8),resultvol8.txt,) $(if $(PPRVOL9),resultvol9.txt,)
	cat $^ > "$@.new" && mv "$@.new" "$@"

clean:
	rm -rf result.txt resultvol1.txt resultvol2.txt resultvol3.txt resultvol4.txt resultvol5.txt resultvol6.txt resultvol7.txt resultvol8.txt resultvol9.txt phase2_result.py phase3_*.svd phase4_*.svd partsvol1 partsvol2 partsvol3 partsvol4 partsvol5 partsvol6 partsvol7 partsvol8 partsvol9

distclean: clean

validate3: phase3_host.svd phase3_host_ficaa.svd phase3_io.svd phase3_io_abindex.svd phase3_msr.svd phase3_smn.svd phase3_smnccd.svd CMSIS-SVD.xsd
	xmllint --schema CMSIS-SVD.xsd phase3_host.svd
	xmllint --schema CMSIS-SVD.xsd phase3_host_ficaa.svd
	xmllint --schema CMSIS-SVD.xsd phase3_io.svd
	xmllint --schema CMSIS-SVD.xsd phase3_io_abindex.svd
	xmllint --schema CMSIS-SVD.xsd phase3_msr.svd
	xmllint --schema CMSIS-SVD.xsd phase3_smn.svd
	xmllint --schema CMSIS-SVD.xsd phase3_smnccd.svd

validate4: phase4_host.svd phase4_host_ficaa.svd phase4_io.svd phase4_io_abindex.svd phase4_msr.svd phase4_smn.svd phase4_smnccd.svd CMSIS-SVD.xsd
	xmllint --schema CMSIS-SVD.xsd phase4_host.svd
	xmllint --schema CMSIS-SVD.xsd phase4_host_ficaa.svd
	xmllint --schema CMSIS-SVD.xsd phase4_io.svd
	xmllint --schema CMSIS-SVD.xsd phase4_io_abindex.svd
	xmllint --schema CMSIS-SVD.xsd phase4_msr.svd
	xmllint --schema CMSIS-SVD.xsd phase4_smn.svd
	xmllint --schema CMSIS-SVD.xsd phase4_smnccd.svd

validate5: phase5_host.svd phase5_host_ficaa.svd phase5_io.svd phase5_io_abindex.svd phase5_msr.svd phase5_smn.svd phase5_smnccd.svd CMSIS-SVD.xsd
	xmllint --schema CMSIS-SVD.xsd phase5_host.svd
	xmllint --schema CMSIS-SVD.xsd phase5_host_ficaa.svd
	xmllint --schema CMSIS-SVD.xsd phase5_io.svd
	xmllint --schema CMSIS-SVD.xsd phase5_io_abindex.svd
	xmllint --schema CMSIS-SVD.xsd phase5_msr.svd
	xmllint --schema CMSIS-SVD.xsd phase5_smn.svd
	xmllint --schema CMSIS-SVD.xsd phase5_smnccd.svd

validate6: phase6_host.svd phase6_host_ficaa.svd phase6_io.svd phase6_io_abindex.svd phase6_msr.svd phase6_smn.svd phase6_smnccd.svd CMSIS-SVD.xsd
	xmllint --schema CMSIS-SVD.xsd phase6_host.svd
	xmllint --schema CMSIS-SVD.xsd phase6_host_ficaa.svd
	xmllint --schema CMSIS-SVD.xsd phase6_io.svd
	xmllint --schema CMSIS-SVD.xsd phase6_io_abindex.svd
	xmllint --schema CMSIS-SVD.xsd phase6_msr.svd
	xmllint --schema CMSIS-SVD.xsd phase6_smn.svd
	xmllint --schema CMSIS-SVD.xsd phase6_smnccd.svd

svd_viewer: svd_viewer.c
	$(CC) -g3 -o $@ $< `pkg-config --cflags --libs gtk+-3.0 libxml-2.0`
