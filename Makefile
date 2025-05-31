.PHONY: start

start:
	cd backend && uvicorn app.main:app --reload --port 7000 &
	cd frontend && npm start
