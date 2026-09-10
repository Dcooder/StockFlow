from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from re import search


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="stockkeeper",
            email="stockkeeper@example.com",
            password="safe-password-123",
        )

    def test_landing_page_is_public_and_login_button_is_present(self):
        response = self.client.get(reverse("landing"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Know what you have")
        self.assertContains(response, reverse("login"))

    def test_authenticated_root_redirects_to_dashboard(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("landing"))

        self.assertRedirects(response, reverse("dashboard"))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('dashboard')}",
        )

    def test_password_reset_sends_email_and_updates_password(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": self.user.email},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("password reset", mail.outbox[0].subject.lower())

        reset_link = search(r"https?://\S+/accounts/reset/\S+", mail.outbox[0].body).group(0)
        response = self.client.get(reset_link, follow=True)
        self.assertEqual(response.status_code, 200)

        confirm_url = response.request["PATH_INFO"]
        response = self.client.post(
            confirm_url,
            {"new_password1": "new-safe-password-456", "new_password2": "new-safe-password-456"},
        )

        self.assertRedirects(response, reverse("password_reset_complete"))
        self.assertTrue(
            self.client.login(
                username="stockkeeper",
                password="new-safe-password-456",
            )
        )

    def test_unknown_email_does_not_reveal_account_or_send_email(self):
        response = self.client.post(
            reverse("password_reset"),
            {"email": "unknown@example.com"},
        )

        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)
