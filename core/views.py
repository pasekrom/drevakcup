from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import views as auth_views
from core.models import User

from core.forms import CustomUserCreationForm
from iihf.models import Cup


class Home(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        iihf_cup = Cup.objects.order_by('-year').first()

        context['cup'] = iihf_cup
        return context


class UserProfile(LoginRequiredMixin, TemplateView):
    template_name = 'core/user.html'


class Cups(LoginRequiredMixin, TemplateView):
    template_name = 'core/cups.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        iihf_cups = Cup.objects.order_by('-year')

        context['iihf_cups'] = iihf_cups
        return context


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'core/signup.html'


class MyLoginView(LoginView):
    form_class = AuthenticationForm
    redirect_authenticated_user = True
    template_name = 'core/login.html'


def logout_page(request):
    logout(request)
    return redirect('/')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            # Directly call PasswordResetView to trigger the password reset process
            return PasswordResetView.as_view(
                email_template_name='core/password_reset_email.html',
                subject_template_name='core/password_reset_subject.txt',
                success_url=reverse('password_reset_done')
            )(request)
        else:
            messages.error(request, 'User with this email does not exist.')
            return redirect('forgot_password')
    return render(request, 'core/forgot_password.html')
