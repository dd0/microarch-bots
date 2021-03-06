all: frontend/docs/isa.html frontend/docs/tools.html

PARAMS=-s --css=/style.css

frontend/docs/isa.html: docs/isa.md
	pandoc $(PARAMS) $< -o $@

frontend/docs/tools.html: docs/tools.md
	pandoc $(PARAMS) $< -o $@

clean:
	rm -f frontend/docs/isa.html frontend/docs/tools.html
