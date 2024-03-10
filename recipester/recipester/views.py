import random

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django_htmx.http import HttpResponseStopPolling, retarget, trigger_client_event

from recipester.forms import RecipeForm, RegisterForm


def index(request):
    if request.htmx:
        # return HttpResponseLocation("/success/", target="#htmx-content")
        # response = render(request, "partial.dhtml")
        # appends the response to the end of the target rather than replacing target's innerHTML
        # return reswap(response, "beforeend")

        form = RecipeForm(request.GET)
        if form.is_valid():
            response = HttpResponse("Success!")
            return trigger_client_event(response, "recipe-added")
        context = {"form": form}
        response = render(request, "form.dhtml", context)
        return retarget(response, "#page-content")
    else:
        context = {"form": RecipeForm()}
        return render(request, "index.dhtml", context)

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = "registration/register.dhtml"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

def success(request):
    if random.random() < 0.35:
        print("Stopping polling")
        return HttpResponseStopPolling()
    return HttpResponse("Success!")

def check_username(request):
    username = request.POST.get("username")
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div class='text-red'>Username already exists.</div>", status=400)
    else:
        # return HttpResponse("<div style='color: green'>Username is available.</div>")
        return HttpResponse("<div class='text-green-500'>Username is available.</div>")
