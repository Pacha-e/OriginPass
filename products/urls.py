from django.urls import path

from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("new/", views.product_create, name="product_create"),
    path("transfers/", views.transfer_list, name="transfer_list"),
    path("transfers/claim/", views.transfer_claim, name="transfer_claim"),
    path("transfers/<int:pk>/respond/", views.transfer_respond, name="transfer_respond"),
    path("analytics/", views.company_analytics, name="analytics"),
    path("analytics/csv/", views.company_analytics_csv, name="analytics_csv"),
    path("admin/overview/", views.admin_overview, name="admin_overview"),
    path("admin/<int:pk>/revoke/", views.admin_revoke_product, name="admin_revoke"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/qr/", views.qr_download, name="qr_download"),
    path("<int:pk>/transfer/", views.transfer_initiate, name="transfer_initiate"),
    path("<int:pk>/revoke/", views.product_revoke, name="product_revoke"),
]
