"""URLs raiz do sistema CEJA Gestão"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import path, include, re_path
from totem import views as totem_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('totem/', totem_views.view_totem_publico, name='totem_publico'),
    path('api/totem/', include('totem.urls')),
    path('', include('usuarios.urls')),
    path('professores/', include('professores.urls')),
    path('funcionarios/', include('funcionarios.urls')),
    path('agenda/', include('agenda.urls')),
    path('cerebro/', include('orientador_ia.urls')),

    # Servir arquivos do totem (CSS, JS, imagens)
    re_path(r'^totem/(?P<path>.*\.(png|jpg|jpeg|gif|css|js|ico|svg|txt))$', serve, {'document_root': settings.BASE_DIR}),
    re_path(r'^(?P<path>(logo|character|beth|cartaz|style|script|dados_escola).*\.(png|jpg|jpeg|gif|css|js|ico|svg|txt))$', serve, {'document_root': settings.BASE_DIR}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customiza o Django Admin
admin.site.site_header = 'CEJA Profa Rosa Soares — Administração'
admin.site.site_title = 'CEJA Gestão'
admin.site.index_title = 'Painel de Administração'

handler500 = 'usuarios.views.custom_500_view'
