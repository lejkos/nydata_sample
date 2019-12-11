# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from ..database import Column, Model, SurrogatePK, db, reference_col, relationship, get_or_create
from ..error import DbError, InvalidUserConfiguration
from ..extensions import bcrypt


class Role(SurrogatePK, Model):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        """Create instance."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class User(UserMixin, SurrogatePK, Model):
    """A user of the app."""

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)

    #: The hashed password
    password = Column(db.LargeBinary(128), nullable=True)

    created_at = Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    def __init__(self, username, email, password=None, **kwargs):
        """Create instance."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        """Set password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<User({self.username!r})>"


def add_user(username: str, password: str, email: str, is_admin: bool = False) -> User:
    """
    Add an user to the database.

    """
    if not email or not username:
        raise InvalidUserConfiguration("[-] Please provide an email and username")

    password_length = len(password)
    if not password_length >= 12:
        msg = f"[-] Password is too short, length={password_length} chars! Minimal length 12 chars!"
        raise InvalidUserConfiguration(msg)

    try:
        user_obj = User.query.filter_by(username=username).first()

        if user_obj:
            print(f'[+] Already found user in db with username={username}')
            return user_obj

        user_obj = User.create(username=username, password=password, email=email, active=True,
                               is_admin=is_admin,)

        if user_obj.is_admin:
            print(
                f"[+] Admin with username={user_obj.username} and email={user_obj.email} was created!"
            )
        else:
            print(
                f"[+] User with username={user_obj.username} and email={user_obj.email} was created!"
            )

        return user_obj

    except Exception as error:
        msg = "[-] Could not create user!\n" + "#" * 40 + f"\n{error}"
        raise DbError(msg)
