from django.contrib.auth import login
from django.contrib.auth.models import Group
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import RegistrationForm


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "landing.html")


class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")
    success_message = "Your account was created. Please sign in."
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.groups.add(Group.objects.get_or_create(name="Staff")[0])
        return response
