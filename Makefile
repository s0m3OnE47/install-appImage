PREFIX ?= /usr/local

.PHONY: install uninstall

install:
	install -m 755 install-appimage "$(DESTDIR)$(PREFIX)/bin/install-appimage"

uninstall:
	rm -f "$(DESTDIR)$(PREFIX)/bin/install-appimage"
