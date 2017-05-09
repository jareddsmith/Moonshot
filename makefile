install:
	pip install arrow
	pip install flask
	pip install pymongo

tidy:
	rm -rf env
	rm -rf __pycache__

clean:
	rm -rf __pycache__
	rm -rf env
	rm -rf CONFIG.py
