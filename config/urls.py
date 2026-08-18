from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from apps.core.sitemaps import PostSitemap, ProjectSitemap, StaticViewSitemap

sitemaps = {
    "static": StaticViewSitemap,
    "portfolio": ProjectSitemap,
    "blog": PostSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", include("apps.core.urls")),
    path("portfolio/", include("apps.portfolio.urls")),
    path("blog/", include("apps.blog.urls")),
    path("orders/", include("apps.orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

handler404 = "apps.core.views.error_404"
handler500 = "apps.core.views.error_500"
