from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView

from core.forms import CustomUserCreationForm
from iihf.models import Cup


class Home(TemplateView):
    template_name = 'core/home.html'


class User(TemplateView):
    template_name = 'core/user.html'


class Cups(TemplateView):
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

