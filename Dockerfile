FROM python:3.7-alpine

RUN mkdir /drip-mock
COPY ./ /drip-mock
WORKDIR /drip-mock
RUN pip install pipenv
RUN pipenv install --ignore-pipfile

CMD pipenv run flask run --host=0.0.0.0
EXPOSE 5000
