from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import json
from .utils import account_activation_token


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username, email, password = request.POST['username'], request.POST['email'], request.POST['password']
        context = {'fieldValues': request.POST}

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password must be at least six characters in length')
                    return render(request, 'authentication/register.html', context)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                current_site = get_current_site(request)
                email_body = {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': account_activation_token.make_token(user) 
                }

                link = reverse('activate', kwargs={
                    'uidb64': email_body['uid'],
                    'token': email_body['token']
                })

                email_subject = 'Activate Your Account'
                activate_url = 'https://' + current_site.domain + link

                email = EmailMessage(
                    subject=email_subject,
                    body=f'Hi {user.username}, please click the link below to activate your account\n{activate_url}',
                    from_email='noreply@mydomain.com',
                    to=[email]
                )

                email.send(fail_silently=False)
                messages.success(request, 'User Account successfully created')
                return render(request, 'authentication/register.html')
        
        return render(request, 'authentication/register.html')
