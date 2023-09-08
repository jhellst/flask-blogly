"""Message model tests."""

import os
from unittest import TestCase

from models import db, User, Message, Follow, Like

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):

        # Like.query.delete()

        User.query.delete()
        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        Message.query.delete()

        m1 = Message(text="m1_text", user_id=self.u1_id)
        m2 = Message(text="m2_text", user_id=self.u2_id)

        db.session.add_all([m1, m2])

        db.session.commit()
        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()
        Like.query.delete()

    def test_message_model(self):
        u1 = User.query.get(self.u1_id)
        u2 = db.session.query(User).filter_by(id = self.u2_id).one_or_none()

        m1 = Message.query.get(self.m1_id)
        m2 = db.session.query(Message).filter_by(id = self.m2_id).one_or_none()

        # User should have no users_liked_by at first
        self.assertEqual(len(m1.users_liked_by), 0)
        self.assertEqual(len(m2.users_liked_by), 0)

        # Both users should not have any liked messages at this point
        self.assertEqual(len(u1.liked_messages), 0)
        self.assertEqual(len(u2.liked_messages), 0)

        # After liking m1, u1 should have m1 in liked_messages.
        # Check that u2 still has no liked_messages.
        # Check that there is 1 total like in table.
        l1 = Like(user_id=self.u1_id, message_id=self.m1_id)
        db.session.add_all([l1])

        self.assertEqual(len(Like.query.all()), 1)

        u1 = User.query.get(self.u1_id)
        db.session.commit()

        self.assertEqual(len(u1.liked_messages), 1)


        # Tests that a like can be removed, and the resulting user will have that removed from liked_messages
        #   and that the users_liked_by will have that user removed.

        l1 = Like.query.filter(Like.user_id == self.u1_id).one_or_none()
        db.session.delete(l1)
        db.session.commit()

        self.assertEqual(len(Like.query.all()), 0)

        self.assertEqual(len(Like.query.all()), 0)
        self.assertEqual(u1.liked_messages, [])
        self.assertEqual(m1.users_liked_by, [])

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(len(u1.liked_messages), 0)
        self.assertEqual(len(u2.liked_messages), 0)

        # Tests that messages can be deleted.
        db.session.delete(m1)
        db.session.commit()

        self.assertEqual(Message.query.get(self.m1_id), None)
        self.assertEqual(Message.query.get(self.m1_id), None)