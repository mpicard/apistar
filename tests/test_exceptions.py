from unittest.mock import MagicMock

import pytest

from apistar import App, Route
from apistar.exceptions import APIException, ConfigurationError
from apistar.test import TestClient


def handled_exception():
    raise APIException(detail='error', status_code=400)


def unhandled_exception():
    raise Exception('Oh noes!')


app = App(routes=[
    Route('/handled_exception/', 'GET', handled_exception),
    Route('/unhandled_exception/', 'GET', unhandled_exception),
])


client = TestClient(app)


def test_handled_exception():
    response = client.get('/handled_exception/')
    assert response.status_code == 400
    assert response.json() == {
        'message': 'error'
    }


def test_unhandled_exception():
    with pytest.raises(Exception):
        client.get('/unhandled_exception/')


def test_unhandled_exception_as_500():
    client = TestClient(app, raise_500_exc=False)
    response = client.get('/unhandled_exception/')
    assert response.status_code == 500
    assert 'Traceback' in response.text


def test_custom_exception_handler():
    custom_exception_handler = MagicMock()

    def unhandled_exception():
        raise Exception('What the ????')
    routes = [
        Route('/unhandled_exception/', 'GET', unhandled_exception),
    ]
    settings = {'exception_handler': custom_exception_handler}
    app = App(routes=routes, settings=settings)
    client = TestClient(app, raise_500_exc=False)
    response = client.get('/unhandled_exception/')
    assert response.status_code == 500
    custom_exception_handler.assert_called()


def test_custom_exception_handler_not_callable():
    custom_exception_handler = 1

    routes = [
        Route('/unhandled_exception/', 'GET', unhandled_exception),
    ]
    settings = {'exception_handler': custom_exception_handler}
    app = App(routes=routes, settings=settings)
    client = TestClient(app, raise_500_exc=False)
    with pytest.raises(ConfigurationError):
        client.get('/unhandled_exception/')
