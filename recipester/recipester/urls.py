from django.contrib import admin
from django.urls import include, path

import recipester.api as api
import recipester.views as views

urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.Login.as_view(), name="login"),
    path("recipes/", views.RecipeList.as_view(), name="recipes"),
]

htmx_urlpatterns = [
    path("check_username/", api.check_username, name="check_username"),
    path("add_recipe/", api.add_recipe, name="add_recipe"),
]

urlpatterns += htmx_urlpatterns
