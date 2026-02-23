# Variables make it easy to update paths later
PY = python
SCRIPT = uml2code.py
INPUT = tests/model.puml
OUT_DIR = tests/output
LANGS = Cpp Java Python

# .PHONY tells Make these aren't actual files
.PHONY: all test clean

all: test

test:
	@mkdir -p $(OUT_DIR)
	@for lang in $(LANGS); do \
		echo "Generating $$lang..."; \
		$(PY) $(SCRIPT) -l $$lang -o $(OUT_DIR) $(INPUT); \
	done

clean:
	rm -rf $(OUT_DIR)/*