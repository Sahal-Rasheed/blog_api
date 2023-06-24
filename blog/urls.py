from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import UserRegistrationView, BlogView, CommentView, CommentUpdateDeleteView

# Define the router for the api using viewset
router = DefaultRouter()
router.register('api/v1/register', UserRegistrationView, basename='register')
router.register('api/v1/blogs', BlogView, basename='blogs')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/login/', views.obtain_auth_token),
    path('api/v1/blogs/<int:pk>/comments/', CommentView.as_view()),
    path('api/v1/comments/<int:pk>/', CommentUpdateDeleteView.as_view())

] + router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
