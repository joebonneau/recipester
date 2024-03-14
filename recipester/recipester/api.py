import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from django.contrib.auth import get_user_model
from recipester.models import Ingredient, Recipe, User

from django.http import HttpResponse
from django.shortcuts import render


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


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


def add_recipe(request):
    url = request.POST["url"]
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.content, "html.parser")
    site_name = ""
    site_name_obj: Tag | NavigableString | None = soup.find(
        "meta", attrs={"property": "og:site_name"}
    )
    if isinstance(site_name_obj, Tag):
        site_name = site_name_obj.get("content", "")
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
    user = User.objects.get(id=request.user.id)
    Recipe.objects.create(
        title=title, site_name=site_name, url=url, description=description, user=user
    )
    recipes = Recipe.objects.filter(user=user)
    return render(request, "partials/recipe_list.dhtml", {"recipes": recipes})
