from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import json
from validate_email import validate_email
from .utils import account_activation_token, send_activation_email

class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        context = { 'fieldValues': request.POST }

        # validate the form data
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'authentication/register.html', context)
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return render(request, 'authentication/register.html', context)
        elif len(password) < 6:
            messages.error(request, 'Password must be at least six characters in length')
            return render(request, 'authentication/register.html', context)
        
        try:
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password)
            user.is_active = False  # User must activate account via email 
            user.save()

            send_activation_email(user, request)
            messages.success(request, 'User Account successfully created. Please check your email to activate your account.')
            return render(request, 'authentication/login.html')
        except Exception as e:
            messages.error(request, 'An error occurred while creating your account. Please try again later.')
            return render(request, 'authentication/register.html', context)


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if username and password:
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, f'Welcome {user.username}, you are now logged in.')
                    return redirect('expenses')
                else:
                    messages.error(request, 'Your account is not active. Please check your email to activate your account.')
                    return render(request, 'authentication/login.html')
            else:
                messages.error(request, 'Invalid credentials. Try again.')
                return render(request, 'authentication/login.html')
        else:
            messages.error(request, 'Please fill in both fields.')
            return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    

class UserNameValidationView(View):
    def post(self, request):
        username = request.POST.get('username', '').strip()
        if not username.isalnum():
            return JsonResponse({'username_error': 'Username must be alphanumeric'}, status=400)
        elif User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Username already exists'}, status=400)
        return JsonResponse({'username_valid': True}, status=200)


class EmailValidationView(View):
    def post(self, request):
        email = request.POST.get('email', '').strip()
        if not validate_email(email):
            return JsonResponse({'email_error': 'Invalid email format'}, status=400)
        elif User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Email already exists'}, status=400)
        return JsonResponse({'email_valid': True}, status=200)


class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated successfully. You can now log in.')
            return redirect('login')
        elif user is None:
            messages.error(request, 'User does not exist. Please register again.')
            return redirect('register')
        else:
            messages.error(request, 'Activation link is invalid or has expired.\nWe have sent you a new activation link. Please check your email.')
            send_activation_email(user, request)
