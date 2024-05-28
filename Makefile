.PHONY : install clean run

install:
	pip install -r requirements.txt
	pre-commit install
