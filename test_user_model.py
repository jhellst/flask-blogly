"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follow, Like
from sqlalchemy.exc import IntegrityError

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        Like.query.delete()
        Message.query.delete()
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        u2 = db.session.query(User).filter_by(id = self.u2_id).one_or_none()

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

        # Both users should not be following each other at this point
        self.assertEqual(u2.is_followed_by(u1), False)
        self.assertEqual(u1.is_followed_by(u2), False)

        # After following u2, u1 should be following u2. Check using is_followed_by()
        # Check that u2 is not following u1.
        follow1 = Follow(user_being_followed_id=self.u2_id, user_following_id=self.u1_id)
        db.session.add_all([follow1])
        db.session.commit()

        self.assertEqual(u2.is_followed_by(u1), True)
        self.assertEqual(u1.is_followed_by(u2), False)

        # Tests that User.signup successfully creates a new user instance in the database
        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.commit()

        u3 = db.session.query(User).filter_by(username="u3").one_or_none()
        self.assertIsInstance(u3, User)
        # Test for property values here, can also compare entered password != password (because of hashing)
        self.assertEqual(u3.username, "u3")
        self.assertEqual(u3.email, "u3@email.com")
        self.assertNotEqual(u3.password, "password")

        # Tests that User.signup fails to create a new user instance in the database given invalid inputs.
        # "These indented lines of code will raise the specified error"
        with self.assertRaises(ValueError):
            User.signup("u5", "password", None)
            User.signup("u6", "a@gmail.com", "", None)
            User.signup("u7", "a@gmail.com", 123, None)
            db.session.commit()

        db.session.commit()

        # Tests User.authenticate to see if 1) finds existing users and 2) fails to find users not in db where a) username does not exist and b) password is incorrect.
        u3_auth = User.authenticate("u3", "password")
        self.assertIsInstance(u3_auth, User)
        self.assertEqual(User.authenticate(u3.username, "asdgfsadgf"), False)
        self.assertEqual(User.authenticate("asdfgasdgasgd", "asdgfsadgf"), False)
        self.assertEqual(User.authenticate(u3.username, "password1"), False)

    def test_user_model(self):
        # Tests that a unique username cannot be created again.
        with self.assertRaises(IntegrityError):
            User.signup("u1", "u1@email.com", "password", None)
            User.signup("u2", "u1@email.com", "password", None)
            db.session.commit()
