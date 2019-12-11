from http import HTTPStatus

import pytest
from webtest.app import AppError


@pytest.mark.usefixtures("db")
def test_login__successful(user, testapp, user_password):
    data = {"username": user.username, "password": user_password}
    response = testapp.post_json("/auth/get_token/", data)

    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json


@pytest.mark.usefixtures("db")
def test_login__no_username(testapp, user_password):
    data = {"password": user_password}

    with pytest.raises(AppError):
        testapp.post_json("/auth/get_token/", data)


@pytest.mark.usefixtures("db")
def test_login__no_password(user, testapp):
    data = {
        "username": user.username,
    }

    with pytest.raises(AppError):
        testapp.post_json("/auth/get_token/", data)


def test_login__empty_username(testapp):

    with pytest.raises(AppError):
        testapp.post_json("/auth/get_token/", {"username": ""})


def test_login__empty_password(testapp):

    with pytest.raises(AppError):
        testapp.post_json("/auth/get_token/", {"password": ""})


@pytest.mark.usefixtures("db")
def test_login__user_not_found(testapp):
    data = {"username": "i-do-not-exist", "password": "something-secret"}

    with pytest.raises(AppError):
        testapp.post_json("/auth/get_token/", data)


@pytest.mark.usefixtures("db")
def test_login__wrong_password(testapp, user):
    data = {"username": user.username, "password": "certainly-a-bad-password"}

    with pytest.raises(AppError):
        testapp.post_json("/auth/get_token/", data)
