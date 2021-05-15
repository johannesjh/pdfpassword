.PHONY: default
default: clean dist

.PHONY: clean
clean:
	rm -rf build dist

.PHONY: dist
dist: dist/io.github.johannesjh.pdfpassword.flatpak

dist/io.github.johannesjh.pdfpassword.flatpak:
	desktop-file-validate io.github.johannesjh.pdfpassword.desktop
	appstreamcli validate io.github.johannesjh.pdfpassword.appdata.xml
	mkdir -p build dist && rm -rf build/app
	touch build/.trackerignore dist/.trackerignore
	flatpak-builder --state-dir=build/state --repo=build/repo build/app io.github.johannesjh.pdfpassword.yml #--build-shell=pdfpassword
	flatpak build-bundle build/repo dist/io.github.johannesjh.pdfpassword.flatpak io.github.johannesjh.pdfpassword

.PHONY: install
install: uninstall dist/io.github.johannesjh.pdfpassword.flatpak
	flatpak --user install -y dist/io.github.johannesjh.pdfpassword.flatpak

.PHONY: uninstall
uninstall:
	-flatpak --user uninstall -y io.github.johannesjh.pdfpassword

.PHONY: run
run:
	flatpak run io.github.johannesjh.pdfpassword
