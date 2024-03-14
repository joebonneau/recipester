from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView
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


class Login(LoginView):
    template_name = "registration/login.dhtml"


class RecipeList(ListView):
    template_name = "recipes.dhtml"
    model = Recipe
    context_object_name = "recipes"

    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(user=user.id)
