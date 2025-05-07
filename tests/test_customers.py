import unittest
from app import create_app
from app.models import db, Customer
from marshmallow import ValidationError


class TestCustomer(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.customer = Customer(name="Test", email="test@test.com", phone="11111111111")
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            db.session.add(self.customer)
            db.session.commit()
        self.client = self.app.test_client()


    def test_create_customer(self):
        payload = {
            "name": "John Doe",
            "email": "jd@email.com",
            "phone": "1234567890"
        }

        response = self.client.post('/customers/', json=payload)
        self.assertRaises(ValidationError)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], "John Doe")


    def test_create_invalid_customer(self):
        payload = {
            "name": "John Doe",
            "phone": "1234567890"
        }

        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json)


    def test_get_customers(self):

        response = self.client.get('/customers/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test')