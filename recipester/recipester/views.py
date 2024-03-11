import requests
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django_htmx.http import retarget, trigger_client_event

from recipester.forms import RecipeForm, RegisterForm
from recipester.models import Recipe


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

def check_username(request):
    username = request.POST.get("username")
    correct_length = 3 <= len(username) <= 25
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div class='text-red-500'>Username already exists.</div>")
    elif correct_length:
        return HttpResponse("<div class='text-green-500'>Username is available.</div>")
    return HttpResponse("<div class='text-red-500'>Username must be between 3 and 25 characters.</div>")

def save_recipe(request):
    url = request.POST.get("url")
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    title = soup.title.string
    description_obj = soup.find("meta", attrs={"name": "description"})
    description = ""
    if description_obj is not None:
        description = description.content
    Recipe.objects.create(title=title, url=url, description=description)
    return HttpResponse(f"Saved {title}!")
