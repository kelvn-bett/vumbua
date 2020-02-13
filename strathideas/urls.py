"""strathideas URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from strathideasapp.views import IdeaListView, home,login_view
from django.contrib.auth import views as auth_views
from strathideasapp import views as user_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('trial/', user_views.TrialView.as_view(), name='trial'),
    path('api-auth/', include('rest_framework.urls')),
    path('', include(('strathideasapp.urls', 'strathideasapp'), namespace=None)),
    path('register/', user_views.register, name='register'),
    path('activate/<uidb64>/<token>', user_views.activate, name='activate'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='strathideasapp/password_reset.html'),
         name='password_reset'),
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name=
                                                                         'strathideasapp/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='strathideasapp/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='strathideasapp/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/', user_views.profile, name='profile'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='strathideasapp/user_logout.html'), name='logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# we are adding our media url and media patterns to the url it allows the media to work within the server
