
.PHONY: clean distclean

all: phase3_result.svd

parts/a.xml: CORRECT_54945_ppr_ZP_B2_specl_nda.pdf
	mkdir -p parts
	pdftohtml -xml $< parts/a

result.txt: extract.py parts/a.xml
	./extract.py > result.txt.new && mv result.txt.new result.txt

phase2_result.py: result.txt phase2.py
	./phase2.py $< > $@.new && mv $@.new $@

phase3_result.svd: phase3.py phase2_result.py
	./phase3.py $< > $@.new && mv $@.new $@

clean:
	rm -f result.txt phase2_result.py phase3_result.svd

distclean: clean
