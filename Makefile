test:
	DB_TEST=True pytest -s

lint: clean
	isort ./api ./tests ./bot
	pylint ./api ./tests ./bot

db_setup:
	alembic upgrade head

clean:
	find . -name "*.pyc" -delete