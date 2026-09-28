
clean:
	rm -rf tests/output

check:
	mkdir -p tests/output
	for t in tests/test-[1-7]-*.sh; do sh $$t; done
