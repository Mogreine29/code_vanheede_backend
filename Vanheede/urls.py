"""Vanheede URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include, re_path
from bulles.views import *
from bulles.views import Accueil,Parametre,Bulle,Site,Simulations,Index
from bulles.api import BullesReturn,BullesViewSet,SitesReturn,SiteViewSet
from bulles import api
from rest_framework.routers import DefaultRouter
from django.contrib.auth.decorators import login_required

router = DefaultRouter()
router.register('param', ParamReturn)

urlpatterns = [
    re_path(r'^upload/(?P<filename>[^/]+)$', FileUploadView.as_view()),
    path('api_auth/',include('rest_framework.urls')),
    #path('logout/', Logout),
    path('admin/', admin.site.urls),
    path('',Index,name="index"),
    path('parametres/',Parametre,name="parametre"),
    path('accueil/',Accueil,name="accueil"),
    path('bulles/',Bulle,name="bulle"),
    path('sites/',SiteV,name="site"),
    path('simulations/',Simulations,name="simulation"),
    path('tournees/',tournees,name="tournees"),
    path('simu_infos/<int:pk>/<str:dt>',SimulationReturn.as_view(),name="simulation"),
    path('full_simu/<int:pk>',FullSimulationReturn.as_view(),name="full_simulation"),
    path('all_simu_infos/',SimulationsInfoReturn.as_view(),name="simulation_infos"),
    path('Change44T/',Change44T,name="Change44T"),
    path('RunSimulation/',RunSimulation,name="RunSimulation"),
    #path('RestartSimulation/',RestartSimulation,name="RestartSimulation"),
    path('ValidateTrip/',ValidateTrip,name="ValidateTrip"),
    path('api_b/',BullesReturn.as_view(),name="api_bulles"),
    path('api_bulles/',BullesViewSet.as_view(), name="api_bulles_frontend"),
    path('api_bulles/<int:pk>/',BullesViewSet.as_view(), name="api_bulles_int"),
    path('api_sim/', SimulationReturn.as_view(), name = "api_simulation"),
    # path('api/',SitesReturn.as_view(),name="api_sites"),
    path('api_sites/',SiteViewSet.as_view(), name="api_sites_frontend"),
    path('api_para/<int:pk>/', ParamReturn, name = "api_parametre"),
    path('get_all_params/', allParamReturn.as_view(), name = "api_all_parametre"),
    # path('api_para/<str:pk>/', ParamReturn.as_view(), name = "api_parametre"),
    path('api/', include(router.urls)),
    path('api_para/', include(router.urls)),

    #Ajout et suppression site et bulle
    #path('add_bin/',addBin,name="add-bin"),
    #path('add_site/',addSite,name="add-site"),
    path('suppbulle/<id_bulle>',DeleteBulle, name="bulles_supp"),
    path('suppsite/<Id_site>',DeleteSite, name="site_supp"),
    path('update_bin/<id_bulle>',UpdateBin.as_view(),name="update-bin"),
    path('update_bin2/',UpdateBin2,name="update-site2"),
    path('update_site/<Id_site>',UpdateSite.as_view(),name="update-site"),
    path('update_site2/',UpdateSite2,name="update-site2"),
    path('delete_simu/<id_simu>',DeleteSimu, name="delete-simu"),
    #path('api_bulles/',api.bulles_list),
    path('last_vidange/<id_depot>',LastVidange,name="last-vidange"),
   
]
