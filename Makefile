run:
	python3 Script/Fly_in.py

install:
	python3 -m pip install -r requirements.txt

lint:
	python3 -m flake8
	python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf .mypy_cache Script/__pycache__