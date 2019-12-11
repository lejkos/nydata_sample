# -*- coding: utf-8 -*-
"""Model unit tests."""
import datetime as dt

import pytest

from nydata.error import DbError, InvalidUserConfiguration
from nydata.user.models import Role, User, add_user

from .factories import UserFactory


@pytest.mark.usefixtures("db")
class TestUser:
    """User tests."""

    def test_get_by_id(self):
        """Get user by ID."""
        user = User("foo", "foo@bar.com")
        user.save()

        retrieved = User.get_by_id(user.id)
        assert retrieved == user

    def test_created_at_defaults_to_datetime(self):
        """Test creation date."""
        user = User(username="foo", email="foo@bar.com")
        user.save()
        assert bool(user.created_at)
        assert isinstance(user.created_at, dt.datetime)

    def test_password_is_nullable(self):
        """Test null password."""
        user = User(username="foo", email="foo@bar.com")
        user.save()
        assert user.password is None

    def test_factory(self, db):
        """Test user factory."""
        user = UserFactory(password="myprecious")
        db.session.commit()
        assert bool(user.username)
        assert bool(user.email)
        assert bool(user.created_at)
        assert user.is_admin is False
        assert user.active is True
        assert user.check_password("myprecious")

    def test_check_password(self):
        """Check password."""
        user = User.create(username="foo", email="foo@bar.com", password="foobarbaz123")
        assert user.check_password("foobarbaz123") is True
        assert user.check_password("barfoobaz") is False

    def test_full_name(self):
        """User full name."""
        user = UserFactory(first_name="Foo", last_name="Bar")
        assert user.full_name == "Foo Bar"

    def test_roles(self):
        """Add a role to a user."""
        role = Role(name="admin")
        role.save()
        user = UserFactory()
        user.roles.append(role)
        user.save()
        assert role in user.roles


@pytest.mark.usefixtures("db")
def test_add_user__ok(user_data):
    user = add_user(
        user_data.username, user_data.password, user_data.email, user_data.is_admin
    )
    assert user.username == user_data.username
    assert user.check_password(user_data.password)
    assert user.is_admin is False
    assert user.email == user_data.email


@pytest.mark.usefixtures("db")
def test_add_user__ok_admin(user_data):
    user = add_user(
        user_data.username, user_data.password, user_data.email, is_admin=True
    )
    assert user.username == user_data.username
    assert user.check_password(user_data.password)
    assert user.is_admin is True
    assert user.email == user_data.email


@pytest.mark.usefixtures("db")
def test_add_user__cause_error_by_duplicate_user(user_data):
    assert User.query.count() == 0

    u = user_data
    add_user(u.username, u.password, u.email, u.is_admin)
    assert User.query.count() == 1

    # trying to add the same user twice -> but does not add it.
    add_user(u.username, u.password, u.email, u.is_admin)
    assert User.query.count() == 1


@pytest.mark.usefixtures("db")
def test_add_user__assure_password_is_encrypted(user_data):
    user = add_user(
        user_data.username, user_data.password, user_data.email, user_data.is_admin
    )
    assert user.password != user_data.password


def test_add_user__username_is_empty(user_data):
    with pytest.raises(InvalidUserConfiguration):
        add_user("", user_data.password, user_data.email, user_data.is_admin)


def test_add_user__password_is_empty(user_data):
    with pytest.raises(InvalidUserConfiguration):
        add_user(user_data.username, "", user_data.email, user_data.is_admin)


def test_add_user__password_is_too_short(user_data):
    with pytest.raises(InvalidUserConfiguration):
        add_user(user_data.username, "1234", user_data.email, user_data.is_admin)
