# Minimal Makefile with start/stop
APP = app.main:app
PID_FILE = .uvicorn.pid

install:
	pip install -r requirements.txt
run:
	python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
test:
	pytest --cov=app --cov-fail-under=80