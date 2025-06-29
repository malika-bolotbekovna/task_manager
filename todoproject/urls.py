from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from users.views import register_view
from django.contrib.auth.views import LogoutView

# class LogoutGetAllowedView(LogoutView):
#     http_method_names = ['get', 'post']

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tasks.urls')),
    path('users/', include('users.urls')),


    # Авторизация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html')),
    path('register/', register_view, name='register'),  # регистрация отдельно на корне


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
