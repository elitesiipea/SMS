from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import redirection
from parents.views import parents_home

from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from ajax_select import urls as ajax_select_urls

admin.autodiscover()

urlpatterns = [

    path('admin/', admin.site.urls),
    path("admin/lookups/", include(ajax_select_urls)),
    path('',                     include("authentication.urls")     ),
    path('administration/',      include("administration.urls")     ),
    path('bibliotheque/',        include("bibliotheque.urls")       ),
    path('comptabilite/',        include("comptabilite.urls")       ),
    path('curriculum/',          include("curriculum.urls")         ),
    path('emplois_du_temps/',    include("emplois_du_temps.urls")   ),
    path('enseignant/',          include("enseignant.urls")         ),
    path('etudiants/',           include("etudiants.urls")          ),
    path('evaluations/',         include("evaluations.urls")        ),
    path('gestion_academique/',  include("gestion_academique.urls") ),
    path('inscription/',         include("inscription.urls")        ),
    path('parents/',             include("parents.urls")            ),
    path('ressources_humaines/', include("ressources_humaines.urls")),
    path('medicale/',            include("medicale.urls"           )),
    path('noitify/',             include("notification.urls"       )),
    path('transport/',             include("transport.urls"       )),
    path('stock/',             include("gestion_stock.urls"       )),

    path('dashboard/redirect/',   redirection),
    path('dashboard/parents/SchoolHome/',   parents_home),
   
]

urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)