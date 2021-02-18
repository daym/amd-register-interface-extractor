
.PHONY: all clean distclean validate

all: phase3_result.svd

include config.mk
include compiler.mk

result.txt: $(if $(PPRVOL1),resultvol1.txt,) $(if $(PPRVOL2),resultvol2.txt,) $(if $(PPRVOL3),resultvol3.txt,)
	cat $^ > "$@.new" && mv "$@.new" "$@"

clean:
	rm -rf result.txt resultvol1.txt resultvol2.txt resultvol3.txt resultvol4.txt resultvol5.txt phase2_result.py phase3_result.svd partsvol1 partsvol2 partsvol3 partsvol4 partsvol5

distclean: clean

validate: phase3_result.svd
	xmllint --schema cmsis-svd.xsd phase3_result.svd
