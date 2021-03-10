# Given result.txt, makes a phase3_host.svd out of it.

partsvol1/a.xml: $(PPRVOL1)
	mkdir -p partsvol1
	pdftohtml -xml $< partsvol1/a >/dev/null

partsvol2/a.xml: $(PPRVOL2)
	mkdir -p partsvol2
	pdftohtml -xml $< partsvol2/a >/dev/null

partsvol3/a.xml: $(PPRVOL3)
	mkdir -p partsvol3
	pdftohtml -xml $< partsvol3/a >/dev/null

partsvol4/a.xml: $(PPRVOL4)
	mkdir -p partsvol4
	pdftohtml -xml $< partsvol4/a >/dev/null

partsvol5/a.xml: $(PPRVOL5)
	mkdir -p partsvol5
	pdftohtml -xml $< partsvol5/a >/dev/null

partsvol6/a.xml: $(PPRVOL6)
	mkdir -p partsvol6
	pdftohtml -xml $< partsvol6/a >/dev/null

partsvol7/a.xml: $(PPRVOL7)
	mkdir -p partsvol7
	pdftohtml -xml $< partsvol7/a >/dev/null

partsvol8/a.xml: $(PPRVOL8)
	mkdir -p partsvol8
	pdftohtml -xml $< partsvol8/a >/dev/null

partsvol9/a.xml: $(PPRVOL9)
	mkdir -p partsvol9
	pdftohtml -xml $< partsvol9/a >/dev/null

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

resultvol6.txt: partsvol6/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol7.txt: partsvol7/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol8.txt: partsvol8/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

resultvol9.txt: partsvol9/a.xml extract.py
	./extract.py $< > "$@".new && mv "$@".new "$@"

phase2_result.py: result.txt phase2.py
	./phase2.py $< > $@.new && mv $@.new $@

phase3_host.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m HOST $< > $@.new && mv $@.new $@

phase3_host_ficaa.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m HOST -d DF::FabricConfigAccessControl $< > $@.new && mv $@.new $@

phase3_io.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m IO $< > $@.new && mv $@.new $@

phase3_io_ficaa.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m IO -d DF::FabricConfigAccessControl $< > $@.new && mv $@.new $@

phase3_msr.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m MSR $< > $@.new && mv $@.new $@

phase3_msr_ficaa.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m MSR -d DF::FabricConfigAccessControl $< > $@.new && mv $@.new $@

phase3_smn.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m SMN $< > $@.new && mv $@.new $@

phase3_smn_ficaa.svd: phase2_result.py phase3.py hexcalculator.py unroller.py rwops.py settings.py
	./phase3.py -m SMN -d DF::FabricConfigAccessControl $< > $@.new && mv $@.new $@
