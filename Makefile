
.PHONY: all clean distclean validate

all: phase3_host.svd phase3_io.svd phase3_msr.svd phase3_smn.svd

include config.mk
include compiler.mk

result.txt: $(if $(PPRVOL1),resultvol1.txt,) $(if $(PPRVOL2),resultvol2.txt,) $(if $(PPRVOL3),resultvol3.txt,) $(if $(PPRVOL4),resultvol4.txt,) $(if $(PPRVOL5),resultvol5.txt,) $(if $(PPRVOL6),resultvol6.txt,) $(if $(PPRVOL7),resultvol7.txt,) $(if $(PPRVOL8),resultvol8.txt,) $(if $(PPRVOL9),resultvol9.txt,)
	cat $^ > "$@.new" && mv "$@.new" "$@"

clean:
	rm -rf result.txt resultvol1.txt resultvol2.txt resultvol3.txt resultvol4.txt resultvol5.txt resultvol6.txt resultvol7.txt resultvol8.txt resultvol9.txt phase2_result.py phase3_*.svd partsvol1 partsvol2 partsvol3 partsvol4 partsvol5 partsvol6 partsvol7 partsvol8 partsvol9

distclean: clean

validate: phase3_host.svd CMSIS-SVD.xsd
	xmllint --schema CMSIS-SVD.xsd phase3_host.svd
