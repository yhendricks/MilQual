from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pcb_tracker import views as pcb_tracker_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', pcb_tracker_views.register, name='register'),
    path('profile/', pcb_tracker_views.profile, name='profile'),
    path('', include('pcb_tracker.urls')),
]