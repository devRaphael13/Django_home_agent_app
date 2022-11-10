from django.urls import path
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from core import views

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="home"),
    path("properties/", views.HouseIndexView.as_view(), name="properties"),
    path("contact_us/", views.ContactPageView.as_view(), name="contact-us"),
    path(
        "properties/<int:pk>/", views.HouseDetailView.as_view(), name="property-detail"
    ),
    path(
        "properties/<int:pk>/edit",
        views.HouseUpdateView.as_view(),
        name="property-edit",
    ),
    path(
        "properties/<int:pk>/images",
        views.ImageIndexView.as_view(),
        name="property-images",
    ),
    path("agents/", views.AgentIndexView.as_view(), name="agents"),
    path(
        "properties/add-property/", views.HouseCreateView.as_view(), name="add-property"
    ),
    path("agents/<int:pk>/", views.AgentDetailView.as_view(), name="agent-detail"),
    path("agents/<int:pk>/edit", views.AgentEditView.as_view(), name="agent-update"),

    # Auth
    path("login/", views.AgentLoginView.as_view(), name="login"),
    path("signup/", views.AgentSignUpView.as_view(), name="signup"),
    path("logout/", views.AgentLogoutView.as_view(), name="logout"),
    path("reset_password/", PasswordResetView.as_view(template_name="core/reset_password.html"), name="reset_password"),
    path("reset_password_confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(template_name="core/reset_password_confirm.html"), name="password_reset_confirm"),
    path("reset_password_sent/", PasswordResetDoneView.as_view(template_name="core/reset_password_sent.html"), name="password_reset_done"),
    path("reset_password_complete/", PasswordResetCompleteView.as_view(template_name="core/reset_password_complete.html"), name="password_reset_complete"),

    # Ajax
    path("cities/", views.cities, name="cities"),
    path("delete_images/", views.delete_images, name="delete-image"),
    path("delete_house/", views.delete_house, name="delete-house"),
    path("delete_photo/", views.delete_photo, name="delete-photo"),

]
