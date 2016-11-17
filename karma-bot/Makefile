run:
	DEBUG=1 python rt_karma_bot.py

clean:
	find . -name '*.pyc' -type f -delete
	find . -name '__pycache__' -type d | xargs rm -rf

check:
	find . -name "*.py" -not -path "./env/*" | xargs flake8

test: check
	./run_tests.sh

.PHONY: run clean check test
