FROM python:3.7-alpine

ENV BASE_URL="http://localhost:5000"
ENV PORT=5000

RUN mkdir /drip-mock
COPY ./ /drip-mock
WORKDIR /drip-mock
RUN pip install pipenv
RUN pipenv install --ignore-pipfile

CMD pipenv run flask run --host=0.0.0.0 --port $PORT
EXPOSE $PORT
