from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

customeruser = get_user_model()


class JWTAuthentication(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user_phone = '09102597202'
        cls.test_user_password = '1234'
        cls.user = customeruser.objects.create_user(
            phone = cls.test_user_phone,
            password = cls.test_user_password,
            email = 'yousef.mokhtar1384@gmail.com',
        )
        cls.token_obtain_url = reverse('token_obtain_pair')
        cls.profile_me_url = reverse('profile-me')
    
    def test_login_and_token_issuance(self):

        print("--- Test start for token ---")

        login_data = {
            'phone': self.test_user_phone,
            'password': self.test_user_password
        }

        response = self.client.post(self.token_obtain_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        self.assertIsNotNone(access_token)
        self.assertIsNotNone(refresh_token) 
        print(f"Access Token Granted : {access_token[:30]}...")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        profile_response = self.client.get(self.profile_me_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data['phone'], self.test_user_phone)
        print(f"Access to user {profile_response.data['phone']} Successfully.")
        print("--- Test Terminated ---")