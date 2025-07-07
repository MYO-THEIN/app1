from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from six import text_type


class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return text_type(user.is_active) + text_type(user.pk) + text_type(timestamp)

account_activation_token = AppTokenGenerator()


def send_activation_email(user, request):
        current_site = get_current_site(request)
        email_info = {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': account_activation_token.make_token(user) 
        }
        link = reverse('activate', kwargs={
            'uidb64': email_info['uid'],
            'token': email_info['token']
        })

        email_subject = 'Activate Your Account'
        activate_url = 'https://' + current_site.domain + link
        email_message = EmailMessage(
            subject=email_subject,
            body=f'Hi {user.username}, please click the link below to activate your account\n{activate_url}',
            from_email='noreply@mydomain.com',
            to=[user.email]
        )

        email_message.send(fail_silently=False)
