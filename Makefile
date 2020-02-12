.POSIX:
.SILENT:
.PHONY: install format

install:
	cp firefox_cli.py "${DESTDIR}/${PREFIX}/bin/firefox_cli"
	chmod +x "${DESTDIR}/${PREFIX}/bin/firefox_cli"

format:
	yapf -i -r .
