Drip mock API
=============

Simple drip mock api implemented with Flask. Currently supports only following endpoints:
* /events (POST)
* /event_actions (GET)
* /subscribers (POST, GET)

Requirements
------------

* python
* pipenv

Installation
------------

``` 
$ pipenv install --ignore-pipfile
```

Usage
-----

``` 
$ pipenv run flask run 
```

Docker
------

```
$ docker build -t drip-mock .
$ docker run -it --rm -p5000:5000 drip-mock
```