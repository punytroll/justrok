all: ui

ui:
	$(MAKE) -C minirok/ui

clean:
	$(MAKE) -C minirok/ui clean
