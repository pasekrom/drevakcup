from django.views.generic import TemplateView

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
