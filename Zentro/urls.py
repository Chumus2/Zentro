from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path

from .media_views import serve_media


urlpatterns = [
    path('admin/', admin.site.urls),

    path("", include("Main.urls")),
    path("homepage/", include("HomePage.urls")),
    path("users/", include("Users.urls")),
    path("chat/", include("Chat.urls")),
    path("Messages/", include("Messages.urls")),
    path("Profiles/", include("Profiles.urls"))
]

if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve_media,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
