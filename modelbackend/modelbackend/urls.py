from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('model_api.urls')),
    path('', include('user_gui.urls'))
]
