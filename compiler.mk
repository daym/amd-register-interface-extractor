# Given result.txt, makes a phase3_result.svd out of it.

partsvol1/a.xml: $(PPRVOL1)
	mkdir -p partsvol1
	pdftohtml -xml $< partsvol1/a

partsvol2/a.xml: $(PPRVOL2)
	mkdir -p partsvol2
	pdftohtml -xml $< partsvol2/a

partsvol3/a.xml: $(PPRVOL3)
	mkdir -p partsvol3
	pdftohtml -xml $< partsvol3/a

resultvol1.txt: partsvol1/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol2.txt: partsvol2/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol3.txt: partsvol3/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

phase2_result.py: result.txt phase2.py
	./phase2.py $< > $@.new && mv $@.new $@

phase3_result.svd: phase2_result.py phase3.py
	./phase3.py $< > $@.new && mv $@.new $@
