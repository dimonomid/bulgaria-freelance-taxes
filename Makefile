
all: output/2018_foreigner.png \
     output/2018_citizen.png   \
     output/2019_foreigner.png \
     output/2019_citizen.png   \
     output/2020_foreigner.png \
     output/2020_citizen.png   \
     output/2021_foreigner.png \
     output/2021_citizen.png   \
     output/2022_foreigner.png \
     output/2022_citizen.png \
     output/2023_foreigner.png \
     output/2023_citizen.png

.PHONY: clean
clean:
	rm -rf output

output:
	mkdir -p output

output/2018_%: | output
	python3 ./bulgaria-freelance-taxes.py --year 2018 --socsec-base-min 510 --socsec-base-max 2600 $(if $(findstring citizen,$@),--citizen,) --output $@

output/2019_%: | output
	python3 ./bulgaria-freelance-taxes.py --year 2019 --socsec-base-min 560 --socsec-base-max 3000 $(if $(findstring citizen,$@),--citizen,) --output $@

output/2020_%: | output
	python3 ./bulgaria-freelance-taxes.py --year 2020 --socsec-base-min 610 --socsec-base-max 3000 $(if $(findstring citizen,$@),--citizen,) --output $@

output/2021_%: | output
	python3 ./bulgaria-freelance-taxes.py --year 2021 --socsec-base-min 650 --socsec-base-max 3000 $(if $(findstring citizen,$@),--citizen,) --output $@

output/2022_%: | output
	python3 ./bulgaria-freelance-taxes.py --year 2022 --socsec-base-min 710 --socsec-base-max 3400 $(if $(findstring citizen,$@),--citizen,) --output $@

output/2023_%: | output
	python3 ./bulgaria-freelance-taxes.py --year 2023 --socsec-base-min 710 --socsec-base-max 3400 $(if $(findstring citizen,$@),--citizen,) --output $@
