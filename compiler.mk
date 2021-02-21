# Given result.txt, makes a phase3_host.svd out of it.

partsvol1/a.xml: $(PPRVOL1)
	mkdir -p partsvol1
	pdftohtml -xml $< partsvol1/a

partsvol2/a.xml: $(PPRVOL2)
	mkdir -p partsvol2
	pdftohtml -xml $< partsvol2/a

partsvol3/a.xml: $(PPRVOL3)
	mkdir -p partsvol3
	pdftohtml -xml $< partsvol3/a

partsvol4/a.xml: $(PPRVOL4)
	mkdir -p partsvol4
	pdftohtml -xml $< partsvol4/a

partsvol5/a.xml: $(PPRVOL5)
	mkdir -p partsvol5
	pdftohtml -xml $< partsvol5/a

resultvol1.txt: partsvol1/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol2.txt: partsvol2/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol3.txt: partsvol3/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol4.txt: partsvol4/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol5.txt: partsvol5/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

phase2_result.py: result.txt phase2.py
	./phase2.py $< > $@.new && mv $@.new $@

phase3_host.svd: phase2_result.py phase3.py unroller.py rwops.py settings.py
	./phase3.py -m HOST $< > $@.new && mv $@.new $@

phase3_io.svd: phase2_result.py phase3.py unroller.py rwops.py settings.py
	./phase3.py -m IO $< > $@.new && mv $@.new $@
