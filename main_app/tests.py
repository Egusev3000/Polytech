import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .models import StudentProfile, AIChat, AIMessage


def _post_json(client, url, payload):
    return client.post(url, data=json.dumps(payload), content_type='application/json')


class CasinoTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.client.force_login(self.user)

    def test_spin_deducts_balance(self):
        response = _post_json(self.client, '/casino/action/', {'action': 'spin', 'bet': 50})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['balance'], 950)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.balance, 950)

    def test_spin_insufficient_balance(self):
        StudentProfile.objects.filter(user=self.user).update(balance=10)
        response = _post_json(self.client, '/casino/action/', {'action': 'spin', 'bet': 50})
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('Недостаточно', data['error'])

    def test_win_small_returns_half_of_bet(self):
        response = _post_json(self.client, '/casino/action/', {'action': 'win', 'type': 'small', 'bet': 50})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['prize'], 25)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.balance, 1025)

    def test_win_maxwin_returns_twenty_times_bet(self):
        response = _post_json(self.client, '/casino/action/', {'action': 'win', 'type': 'maxwin', 'bet': 50})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['prize'], 1000)
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.balance, 2000)


class DepositTests(TestCase):
    def test_deposit_adds_balance(self):
        user = User.objects.create_user(username='dep', password='testpass123')
        self.client.force_login(user)
        response = self.client.post('/deposit/', {'amount': 500})
        self.assertEqual(response.status_code, 200)
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.balance, 1500)


class PolytechAITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='aiuser', password='testpass123')
        self.chat = AIChat.objects.create(user=self.user, title='Новый диалог')

    @patch('main_app.views.ollama.chat')
    def test_ai_chat_flow(self, mock_chat):
        mock_chat.return_value = {'message': {'content': 'Слава Политеху!'}}

        self.client.force_login(self.user)
        response = self.client.post(
            '/ai/',
            data={'chat_id': str(self.chat.id), 'query': 'Привет, Политех!'},
            **{'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'},
        )
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)
        self.assertEqual(data['response'], 'Слава Политеху!')
        self.chat.refresh_from_db()
        self.assertEqual(self.chat.title, 'Привет, Политех!')
        self.assertEqual(AIMessage.objects.filter(chat=self.chat, role='user').count(), 1)
        self.assertEqual(AIMessage.objects.filter(chat=self.chat, role='ai').count(), 1)
