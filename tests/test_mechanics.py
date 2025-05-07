
import unittest
from app import create_app

from app.models import db, Mechanic
from app.utils.auth import encode_token
from werkzeug.security import generate_password_hash

class TestMechanic(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.mechanic = Mechanic(
            name="Test",
            email="test@test.com",
            salary=10000.00,
            password='123'
        )
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.mechanic)
            db.session.commit()
        self.token = encode_token(1)
        self.client = self.app.test_client()


    def test_login_mechanic(self):
        payload = {
            "email": "test@test.com",
            "password": "123"
        }

        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)


    def test_mechanic_update(self):
        update_payload = {
            "name": "NEW MECHANIC",
            "email": "test@test.com",
            "salary": 1000000000.00,
            "password": "123"
        }

        headers = {'Authorization': "Bearer "+ self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'NEW MECHANIC')