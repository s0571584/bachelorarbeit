"""
Unit Tests für user_api.py
"""

import unittest
import json
from user_api import app, reset_data


class TestUserAPI(unittest.TestCase):

    def setUp(self):
        """Setup - Erstelle Test-Client und setze Daten zurück"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        reset_data()

    def test_create_user(self):
        """Test: User erstellen"""
        response = self.client.post('/users',
                                    data=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Alice')
        self.assertEqual(data['email'], 'alice@example.com')
        self.assertIn('id', data)

    def test_create_user_missing_fields(self):
        """Test: User erstellen ohne erforderliche Felder"""
        response = self.client.post('/users',
                                    data=json.dumps({'name': 'Alice'}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_get_all_users_empty(self):
        """Test: Alle Users abrufen (leer)"""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, [])

    def test_get_all_users(self):
        """Test: Alle Users abrufen"""
        # Erstelle zwei Users
        self.client.post('/users',
                        data=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
                        content_type='application/json')
        self.client.post('/users',
                        data=json.dumps({'name': 'Bob', 'email': 'bob@example.com'}),
                        content_type='application/json')

        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)

    def test_get_user(self):
        """Test: Einzelnen User abrufen"""
        # Erstelle User
        create_response = self.client.post('/users',
                                          data=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
                                          content_type='application/json')
        user_id = json.loads(create_response.data)['id']

        # Rufe User ab
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Alice')

    def test_get_user_not_found(self):
        """Test: User abrufen (nicht gefunden)"""
        response = self.client.get('/users/999')
        self.assertEqual(response.status_code, 404)

    def test_update_user(self):
        """Test: User aktualisieren"""
        # Erstelle User
        create_response = self.client.post('/users',
                                          data=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
                                          content_type='application/json')
        user_id = json.loads(create_response.data)['id']

        # Aktualisiere User
        response = self.client.put(f'/users/{user_id}',
                                   data=json.dumps({'name': 'Alice Updated', 'email': 'alice.new@example.com'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Alice Updated')
        self.assertEqual(data['email'], 'alice.new@example.com')

    def test_update_user_partial(self):
        """Test: User teilweise aktualisieren"""
        # Erstelle User
        create_response = self.client.post('/users',
                                          data=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
                                          content_type='application/json')
        user_id = json.loads(create_response.data)['id']

        # Aktualisiere nur Name
        response = self.client.put(f'/users/{user_id}',
                                   data=json.dumps({'name': 'Alice Updated'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['name'], 'Alice Updated')
        self.assertEqual(data['email'], 'alice@example.com')  # Email unverändert

    def test_update_user_not_found(self):
        """Test: User aktualisieren (nicht gefunden)"""
        response = self.client.put('/users/999',
                                   data=json.dumps({'name': 'Test'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_delete_user(self):
        """Test: User löschen"""
        # Erstelle User
        create_response = self.client.post('/users',
                                          data=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
                                          content_type='application/json')
        user_id = json.loads(create_response.data)['id']

        # Lösche User
        response = self.client.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)

        # Prüfe, ob User wirklich gelöscht wurde
        get_response = self.client.get(f'/users/{user_id}')
        self.assertEqual(get_response.status_code, 404)

    def test_delete_user_not_found(self):
        """Test: User löschen (nicht gefunden)"""
        response = self.client.delete('/users/999')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
