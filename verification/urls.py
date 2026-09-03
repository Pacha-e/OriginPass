from django.urls import path

from . import views

app_name = "verification"

urlpatterns = [
    path("", views.lookup, name="lookup"),
    path("<str:code>/", views.verify, name="verify"),
]
