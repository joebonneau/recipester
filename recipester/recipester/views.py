import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django_htmx.http import retarget, trigger_client_event

from recipester.forms import RecipeForm, RegisterForm
from recipester.models import Ingredient, Recipe, User


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


class Login(LoginView):
    template_name = "registration/login.dhtml"


def check_username(request):
    username = request.POST.get("username")
    correct_length = 3 <= len(username) <= 25
    if get_user_model().objects.filter(username=username).exists():
        return HttpResponse("<div class='text-red-500'>Username already exists.</div>")
    elif correct_length:
        return HttpResponse("<div class='text-green-500'>Username is available.</div>")
    return HttpResponse(
        "<div class='text-red-500'>Username must be between 3 and 25 characters.</div>"
    )


def save_recipe(request):
    url = request.POST["url"]
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    h1 = soup.h1
    title = ""
    if isinstance(h1, Tag):
        title = h1.get_text().strip()
    ingredients_div: Tag | NavigableString | None = soup.find(
        "div", class_=lambda x: "ingredient" in x if x is not None else False
    )
    ingredients = []
    if isinstance(ingredients_div, Tag):
        ingredients_li = ingredients_div.find_all("li")
        ingredients = [ingredient.get_text().strip() for ingredient in ingredients_li]
    description_obj: Tag | NavigableString | None = soup.find(
        "meta", attrs={"name": "description"}
    )
    description = ""
    if isinstance(description_obj, Tag):
        description = description_obj.get("content", "")
    Recipe.objects.create(title=title, url=url, description=description)
    Ingredient.objects.bulk_create(ingredients)
    return HttpResponse(f"Saved {title}!")
