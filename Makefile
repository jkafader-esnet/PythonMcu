PYTHON=venv/bin/python

.PHONY: test
test:
	     PYTHON python_mcu/tests.py
