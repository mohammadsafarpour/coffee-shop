from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

User = get_user_model()

class JWTAuthenticationTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            phone="09102597202",
            email="yousef.mokhtar1384@gmail.com",
            password="testpassword123"
        )

        self.token_obtain_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')

        self.profile_api_url = reverse('profile-favorites', kwargs={'user_id': self.user.id})

    def login_and_get_tokens(self):

        response = self.client.post(self.token_obtain_url, {
            "phone": "09102597202",
            "password": "testpassword123"
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data["access"], response.data["refresh"]

    def test_login_and_relogin_invalidate_old_tokens(self):

        access1, refresh1 = self.login_and_get_tokens()

        self.assertTrue(
            OutstandingToken.objects.filter(user=self.user).exists(),
            "هیچ توکنی در دیتابیس برای کاربر ذخیره نشد!"
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access1}")
        response1 = self.client.get(self.profile_api_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK, "دسترسی با توکن اولیه موفق نبود!")

        access2, refresh2 = self.login_and_get_tokens()

        old_tokens = OutstandingToken.objects.filter(user=self.user).exclude(token=refresh2)
        self.assertTrue(
            all(BlacklistedToken.objects.filter(token=t).exists() for t in old_tokens),
            "توکن‌های قدیمی هنوز بلاک نشده‌اند!"
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access1}")
        response2 = self.client.get(self.profile_api_url)
        self.assertIn(response2.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                      "توکن قدیمی هنوز معتبر است!")

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access2}")
        response3 = self.client.get(self.profile_api_url)
        self.assertEqual(response3.status_code, status.HTTP_200_OK, "توکن جدید دسترسی نمی‌دهد!")