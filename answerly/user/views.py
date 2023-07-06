from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView


class RegisterView(CreateView):
    success_url = reverse_lazy("user:login")
    template_name = "registration/register.html"
    form_class = UserCreationForm
