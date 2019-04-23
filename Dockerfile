FROM python:3.6-slim

ADD . /usr/src/app
WORKDIR /usr/src/app

RUN pip install PyYAML

CMD ["python", "integration_tests.py"]