from django.urls import path

from . import views

app_name = "companies"

urlpatterns = [
    path("application/", views.application_detail, name="application_detail"),
    path("application/new/", views.application_create, name="application_create"),
    path("application/edit/", views.application_edit, name="application_edit"),
    path("review/", views.review_list, name="review_list"),
    path("review/<int:pk>/", views.review_detail, name="review_detail"),
    path("review/<int:pk>/approve/", views.review_approve, name="review_approve"),
    path("review/<int:pk>/reject/", views.review_reject, name="review_reject"),
]
