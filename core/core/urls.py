from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def home_redirect(request):
    if request.user.is_authenticated:
        return redirect("contact-list")
    return redirect("login")


urlpatterns = [
    path("", home_redirect, name="home"),

    path("admin/", admin.site.urls),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("accounts/", include("accounts.urls")),
    path("contacts/", include("contacts.urls")),
    path("deals/", include("deals.urls")),
    path("activities/", include("activities.urls")),
    path("customers/", include("customers.urls")),
    path("staff/", include("staff.urls")),
    path("chat/", include("chat.urls")),
    path("contracts/", include("contracts.urls")),
    path("tasks/", include("tasks.urls")),
    path("projects/", include("projects.urls")),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)