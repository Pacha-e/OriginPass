# ---- External imports ----
from django.urls import path

# ---- Internal imports ----
from . import handover_views, views

# ---- Constants ----

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("new/", views.product_create, name="product_create"),
    path("custody/", views.custody, name="custody"),
    path("analytics/", views.company_analytics, name="analytics"),
    path("analytics/csv/", views.company_analytics_csv, name="analytics_csv"),
    path("admin/overview/", views.admin_overview, name="admin_overview"),
    path("admin/<int:pk>/revoke/", views.admin_revoke_product, name="admin_revoke"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("<int:pk>/qr/", views.qr_download, name="qr_download"),
    path("<int:pk>/revoke/", views.product_revoke, name="product_revoke"),
    path("<int:pk>/entregar/", handover_views.handover, name="handover"),
    path(
        "<int:pk>/entregar/codigo.json",
        handover_views.handover_code_json,
        name="handover_code",
    ),
    path("recibir/", handover_views.receive_start, name="receive_start"),
    path("recibir/<str:passport_code>/", handover_views.receive, name="receive"),
]
