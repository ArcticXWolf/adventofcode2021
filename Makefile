INPUT ?= testinput

FORCE:

day%: FORCE
	cd $@ && python code.py $(INPUT)
