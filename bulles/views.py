from django.db.models import Max
from django.db.models.query import QuerySet
from rest_framework.response    import Response
from rest_framework.views       import APIView
from bulles.models              import Bulles
from django.shortcuts           import render, redirect, get_object_or_404
from bulles.serializers import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, renderer_classes, parser_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.parsers import JSONParser, FileUploadParser, MultiPartParser
from django.contrib import messages
from django.views.generic import TemplateView
from django.conf import settings
from django.http import *
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import BinForm, SiteForm

from django.template import Context, Template
from Creations_matrices.maj import maj
from Creations_matrices.maj_auto_vitesse_remplissage import maj_automatisation
from optimisation.main import main
import pickle
from datetime import datetime, timedelta
from time import strftime
import json
from django.db import connection
import pandas as pd
from datetime import datetime, timedelta
from datetime import date
import random
from bulles.forms import User
import time

def Index(request):  
    submitted = False
    form = User()
    if request.method == 'POST':

        form = User(request.POST)
        if form.is_valid():

            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None and user.is_active:
                submitted = False
                login(request, user)
                request.session.set_expiry(0)
                time.sleep(2)
                return redirect('accueil')
            else:
                submitted = True
                
                

        
    return render(request,'index.html', context={'form':form, 'submitted':submitted})


def Logout(request):
    logout(request)


@login_required
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def Accueil(request):
    return render(request, 'accueil.html')


@login_required
@api_view(('GET',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def Parametre(request):
    return render(request, 'parametres.html')


@login_required
@api_view(('GET','POST'))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def Bulle(request):
    
    submitted = False
    
    if (request.method == "POST") :
        form = BinForm(request.POST)
        if form.is_valid():
            form.save()
            latest_id = Bulles.objects.all().values_list('id_bulle', flat=True).order_by('-id_bulle').first()
            
            bulle = get_object_or_404(Bulles, pk=latest_id)

            duo = [100.0001,100.0001,100.0001,100.0001,100.0001,100.0001,100.0001,100.0001,100.0001,100.0001,100.0001,100.0001]
            mono = [200.0001,200.0001,200.0001,200.0001,200.0001,200.0001,200.0001,200.0001,200.0001,200.0001,200.0001,200.0001]
            if bulle.type_bulle == "Mono" or bulle.type_bulle == "Mono ent":
                
                bulle.vitesse_remplissage_blanc = mono
                bulle.vitesse_remplissage_colore = mono
                bulle.save(update_fields=['vitesse_remplissage_blanc','vitesse_remplissage_colore'])

            elif bulle.type_bulle == "Double" or bulle.type_bulle == "Double ent":
                bulle.vitesse_remplissage_blanc = duo
                bulle.vitesse_remplissage_colore = duo
                bulle.save(update_fields=['vitesse_remplissage_blanc','vitesse_remplissage_colore'])
                
            site = bulle.id_site
            site.nombre_bulles = site.bul.count()
            site.save(update_fields=['nombre_bulles'])
            return redirect('/bulles')
    else :
        form = BinForm
        if 'submitted' in request.GET:
            submitted = True
    
    
    
    return render(request, 'bulles.html', {'form': form, 'submitted': submitted})


class UpdateBin(APIView):
    def get(self, request,id_bulle, *args, **kwargs):
        qs = Bulles.objects.get(pk=id_bulle)
        serializer = BullesSerializer(qs)
        return Response(serializer.data)
    
@login_required
@api_view(('GET', 'POST',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def UpdateBin2(request):

    if request.method == "POST" :
        if request.POST.get("Id_depot_M") == "Quévy" :
            Id_depot_M = 1
        else :
            Id_depot_M = 2
            
        Bulles.objects.filter(id_bulle =request.POST.get("Id_bulle_M")).update(id_depot=Id_depot_M,id_site=request.POST.get("Id_site_M"),num_bulle=request.POST.get("Nom_M"),latitude=request.POST.get("latitude_M"), longitude=request.POST.get("longitude_M"),type_bulle =request.POST.get("Type_bulle_M"),date_vidange=request.POST.get("date_vidange_M"),colories=request.POST.get("Colories_M"))
        return render(request, 'sites.html')


@login_required
@api_view(('GET','POST'))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def SiteV(request):
    submitted = False
    
    if request.method == "POST" :
        form = SiteForm(request.POST)
        if form.is_valid():
            form.save()
            latest_id = Site.objects.all().values_list('id_site', flat=True).order_by('-id_site').first()
            site = get_object_or_404(Site, pk=latest_id)
            maj(site)
            return redirect('/sites')
    else:
        form = SiteForm
        if 'submitted' in request.GET:
            submitted = True
        
    return render(request, 'sites.html', {'form': form, 'submitted': submitted})  

class UpdateSite(APIView):
    def get(self, request,Id_site, *args, **kwargs):
        qs = Site.objects.get(pk=Id_site)
        serializer = SiteSerializer(qs)
        return Response(serializer.data)
    
@login_required
@api_view(('GET', 'POST',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def UpdateSite2(request):

    if request.method == "POST" :
        if request.POST.get("Id_depot_M") == "Quévy" :
            Id_depot_M = 1
        else :
            Id_depot_M = 2
            
        Site.objects.filter(id_site =request.POST.get("Id_site_M")).update(id_depot=Id_depot_M,nom=request.POST.get("Nom_M"),latitude=request.POST.get("latitude_M"), longitude=request.POST.get("longitude_M"),type_site =request.POST.get("Type_site_M"),date_vidange=request.POST.get("date_vidange_M"))
        return render(request, 'sites.html')

@login_required
def Simulations(request):
    return render(request, 'simulations.html')


@login_required
@api_view(('GET',))
def tournees(request):
    return render(request, 'tournees.html')


@login_required
@api_view(('GET', 'POST',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def ValidateTrip(request):
    print("VALIDATING")

    bins = request.POST.get("bins_validate").split(",")
    tripdate = datetime.strptime(request.POST.get("tripdate"), "%Y-%m-%d")
    liste_b = request.POST.get("poidsB_validate").split(",")
    liste_c = request.POST.get("poidsC_validate").split(",")
    automatisation = []
    
    for i in range(len(liste_b)):
        automatisation.append((tripdate.date(),bins[i],int(liste_b[i]),int(liste_c[i])))
    
    maj_automatisation(automatisation)
    
    for bin in bins:
        bin_to_update = Bulles.objects.get(num_bulle=bin)
        bin_to_update.date_vidange = tripdate
        bin_to_update.save()
    
    serializerResponse = {
        "trip": request.POST.get("tripdate"),
        "bins": request.POST.get("bins_validate")
    }

    return Response(serializerResponse)


@login_required
def updateDatabase(starting_date, depot_id, file_name):
    ids_to_delta = {}
    with connection.cursor() as cursor:
        cursor.execute("SELECT num_bulle FROM bulles where id_depot=" + str(depot_id))
        myresult = cursor.fetchall()
        for x in myresult:
            ids_to_delta[x[0]] = -1

        print("ids from db is ", ids_to_delta)

        f = "files/" + file_name
        df = pd.read_excel(f, skiprows=[0, 1])

        df = df.iloc[::-1]
        try:
            df = df.loc[df["Weighing Date"] <= pd.to_datetime(starting_date)]
            today = df.iloc[0]["Weighing Date"]
        except:
            print("can't use weighing date")
        try:
            df = df.loc[df["Collection Date"] <= pd.to_datetime(starting_date)]
            today = df.iloc[0]["Collection Date"]
        except:
            print("can't use collection date")

        print("the starting day is ", today)
        for index, row in df.iterrows():
            try:
                date_of_empty = row["Weighing Date"]
            except:
                print("can't use weighing date")
            try:
                date_of_empty = row["Collection Date"]
            except:
                print("can't use Collection date")
            delta = abs((date_of_empty - today).days)
            if row["Glass Bin Number"].strip() in ids_to_delta:
                if ids_to_delta[row["Glass Bin Number"].strip()] == -1:
                    print("we detected minus one, we replace with ", date_of_empty)
                    ids_to_delta[row["Glass Bin Number"].strip()] = date_of_empty

        print(ids_to_delta)
        print("len of dic is ", len(ids_to_delta))

        for key, value in ids_to_delta.items():
            if value == -1:
                print("bad one ", key)
                ids_to_delta[key] = date.today() - timedelta(days=random.randint(0, 5))
                print(date.today())
                print(ids_to_delta[key])
            request = "UPDATE bulles SET date_vidange = '" + str(ids_to_delta[key]) + "' WHERE num_bulle='" + str(
                key) + "'"
            cursor.execute(request)

@login_required
def DeleteSimu(request, id_simu):
    try:
        id_simu
        with connection.cursor() as cursor:
            request = f"SELECT id_para FROM simulation WHERE Id_simu = {id_simu}"
            cursor.execute(request)
            id_para = cursor.fetchall()[0][0]
            request = f"DELETE FROM profil_param WHERE id = {id_para}"
            cursor.execute(request)
            request = f"DELETE FROM trajet_simu WHERE simu_id = {id_simu}" 
            cursor.execute(request)
        param = Simulation.objects.get(pk=id_simu)
        param.delete()            
        print("Simu supprimé")

    except:
        print("Cette simu n'existe pas")
        return redirect('accueil')
    return redirect('accueil')


class FileUploadView(APIView):
    parser_classes = [MultiPartParser]

    def put(self, request, filename, format=None):
        up_file = request.data['file']
        # ...
        # do some stuff with uploaded file
        # ...
        destination = open('files/' + up_file.name, 'wb+')
        for chunk in up_file.chunks():
            destination.write(chunk)
        destination.close()
        updateDatabase(date.today(), 1, up_file.name)

        return Response(up_file.name)

@login_required
@api_view(('GET', 'POST',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def Change44T(request):
    def swap_words(s, x, y):
        return y.join(part.replace(y, x) for part in s.split(x))

    bin_id = request.POST.get("bin_id")
    trajet_id = request.POST.get("trajet_id")
    responseObject = {}
    new_depot = Bulles.objects.get(num_bulle=bin_id)
    serializerBin = BullesSerializer(new_depot)
    new_depot_id = serializerBin["id_bulle"].value

    # Here, we request trajet from trajet serializer then we change it in trajet_simu table
    # trajets_queryset = Trajet.objects.filter(id_trajet=trajet_id)
    # trajets = TrajetSerializer(trajets_queryset, many=True)
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM trajet_simu WHERE trajet_id ={};"
            cursor.execute(query.format(trajet_id))
            results = cursor.fetchone()
            for bin in json.loads(results[2]):
                if bin[0] == new_depot_id:
                    new_depot_blob = bin
            bin_to_swap = json.loads(results[2])[1]
            swapped_trajet = swap_words(results[2], str(bin_to_swap), str(new_depot_blob))
            print(swapped_trajet)
            query = "UPDATE trajet_simu SET tournee='{}' WHERE trajet_id={};"
            cursor.execute(query.format(swapped_trajet, trajet_id))
        responseObject["status"] = "Changement effectué avec succès <br/> Veuillez recharger la page"
    except:
        responseObject["status"] = "Erreur dans l'opération"
    return Response(responseObject)


@login_required
@api_view(('GET', 'POST',))
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def RunSimulation(request):
    if request.POST.get("spike") == "Activé":
        spike = 1
    else:
        spike = 0
    
    if request.POST.get("mode") == "Activé":
        mode = 1
    else:
        mode = 0
    urgent_bins = []
    if request.POST.get("bins_urgent"):
        # print("there are urgent bins")
        temp = request.POST.get("bins_urgent")

        # we convert to a list when there is only one urgent bin
        if "," in temp:
            temp = temp.split(",")
        if type(temp) != list:
            temp = [temp]
        for bin in temp:
            try:
                print("bin is ", bin)
                urgent_bin = Bulles.objects.get(num_bulle=bin)
                serializerBin = BullesSerializer(urgent_bin)
                urgent_bins.append(serializerBin["id_bulle"].value)
                print(serializerBin["id_bulle"].value)
            except:
                print("error with fetching bulle")
    if request.POST.get("bins_validate"):
        bins = request.POST.get("bins_validate").split(",")
        tripdate = datetime.strptime(request.POST.get("tripdate"), "%Y-%m-%d")
        liste_b = request.POST.get("poidsB_validate").split(",")
        liste_c = request.POST.get("poidsC_validate").split(",")
        automatisation = []
        
        for i in range(len(liste_b)):
            automatisation.append((tripdate.date(),bins[i],int(liste_b[i]),int(liste_c[i])))
        
        maj_automatisation(automatisation)
        
        for bin in bins:
            bin_to_update = Bulles.objects.get(num_bulle=bin)
            bin_to_update.date_vidange = tripdate
            bin_to_update.save()
    
    date_debut = request.POST.get("date-debut")
    param = {
        "Depot": request.POST.get("depot"),
        "Vidange": request.POST.get("vidange"),
        "Max time": float(request.POST.get("temps")) * 3600,
        "Number of weeks": int(request.POST.get("semaine")),
        "Number of days": int(request.POST.get("jours")),
        "date_debut": request.POST.get("date-debut"),
        "26 Tonnes": int(request.POST.get("26T")),
        "44 Tonnes": int(request.POST.get("44T")),
        "Spikes remplissage": spike,
        "Remplissage limite": float(request.POST.get("remplissage")),
        "Remplissage limite camions": request.POST.get("remplissage-truck"),
        "Mode camions adaptatifs": mode,
        "urgent_bins": urgent_bins,
    }

    Sol, bulles_debordent = main(param)

    liste = []

    for elem in bulles_debordent:
        liste.append(elem.Id)
    liste_json = json.dumps(liste)
    nom_recu = request.POST.get("Nom"),
    nom_recu = ''.join(nom_recu)
    nom_recu.replace('(', '')
    nom_recu.replace(')', '')
    nom_recu.replace("'", '')
    nom_recu.replace(',', '')
    new_param = Profil_Param.objects.create(Nom=nom_recu, parametre=param)
    new_param.save()
    now = datetime.now()
    date = now.strftime("%m/%d/%Y, %H:%M:%S")
    new_sim = Simulation.objects.create(nom=nom_recu, date_creation=date, bulles_debordent=liste_json,
                                        id_para=new_param, date_debut=date_debut)
    new_sim.save()
    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT * FROM simulation")
    #     print(cursor.fetchall())

    # calcul de la date du trajet
    # calcul de la différence de semaine
    date_debut = datetime.strptime(date_debut, '%Y-%m-%d')  # on convertit au format date

    for j in range(len(Sol)):

        for i in range(len(Sol[j])):
            print("on est à la semaine ", j, " on save la tournée du jour ", Sol[j][i].day)
            new_trajet = Trajet.objects.create(semaine=j, jour=Sol[j][i].day, id_simu=new_sim)

            semaine_debut = date_debut + (
                timedelta(days=(7 * j)))  # on récupère un jour dans la semaine où le trajet à lieu
            lundi_debut = semaine_debut - timedelta(
                days=semaine_debut.weekday())  # on trouve le lundi de cette semaine en soustrayant le weekday
            trajet_date = lundi_debut + timedelta(days=Sol[j][
                i].day)  # une fois qu'on a le lundi, on ajoute le numéro de jour de l'objet camion. C'est messy mais ça marche

            new_trajet.save()
            tournee = []

            type_camion = None

            if Sol[j][i].capacity[0] > 7000: # 44T
                type_camion = 2
            elif Sol[j][i].capacity[0] <= 6927.5: # 26T
                type_camion = 1
            
            if type_camion != None:
                for idx_elem,elem in enumerate(Sol[j][i].route):
                    if type(elem) == list:
                        for idx_t,t in enumerate(elem):
                            tournee.append([t.Id, int(t.poids), t.latitude, t.longitude])

                            if idx_t!=0:
                                if t.Id >= 0:  # avant 596 et pas le dépot
                                    bulle_obj = Bulles.objects.get(id_bulle=t.Id)
                                    new_trajet.bulle.add(bulle_obj)
                    else:
                        tournee.append([elem.Id, int(elem.poids), elem.latitude, elem.longitude])

                        if idx_elem!=0:
                            if elem.Id >= 0:  # avant 596 et pas le dépot
                                bulle_obj = Bulles.objects.get(id_bulle=elem.Id)
                                new_trajet.bulle.add(bulle_obj)

            poidsb, poidsc = Sol[j][i].remplissageb, Sol[j][i].remplissagec
            temps_tournee = Sol[j][i].time
            trn = str(tournee)

            bb = []
            bc = []
            for elem in Sol[j][i].route:
                if type(elem) == list:
                        for t in elem:
                            bb.append(t.poidsb)
                            bc.append(t.poidsc)
                else:
                    bb.append(elem.poidsb)
                    bc.append(elem.poidsc)
            # On insère dans la table custom le trajet
            with connection.cursor() as cursor:
                query = "INSERT INTO trajet_simu (simu_id, trajet_id, tournee, temps, poids_colore, poids_blanc, date_trajet, type_camion, liste_poids_blanc, liste_poids_colore) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');"
                cursor.execute(
                    query.format(new_sim.id_simu, new_trajet.id_trajet, trn, temps_tournee, poidsc, poidsb, trajet_date,
                                 type_camion, bb, bc))

    serializer = SimulationSerializer(new_sim)
    responseObject = serializer.data
    responseObject["simulation_result"] = "La simulation a été effectuée avec succès. </br> Veuillez recharger la page pour voir apparaitre la nouvelle simulation."
    return Response(responseObject)
    

@login_required
def DeleteBulle (request, id_bulle):
    #on prend l'objet (en fonction de l'ID) s'il existe et sinon on retourne une erreur
    bulle = get_object_or_404(Bulles, pk=id_bulle)
    #on récupère l'id site associé
    site = bulle.id_site
    #on supprime la bulle
    bulle.delete()
    #on compte le nombre de bulles avec le même site et on l'impose à "nombre_bulles"
    site.nombre_bulles = site.bul.count()
    #on update le nombre de bulles dans la table
    site.save(update_fields=['nombre_bulles'])
    #redirection
    return redirect('/bulles')


@login_required
def DeleteSite(request, Id_site):
    try:
        Id_site
        param = Site.objects.get(pk=Id_site)
        param.delete()
        #maj(param)
        print("Site supprimé")
    except:
        print("Ce site n'existe pas")
        return redirect('api_sites_frontend')
    return redirect('/sites')


class SimulationsInfoReturn(APIView):
    def get(self, request, *args, **kwargs):
        qs = Simulation.objects.all()
        serializer = SimulationInfoSerializer(qs, many=True)
        return Response(serializer.data)


class allParamReturn(APIView):
    def get(self, request, *args, **kwargs):
        qs = Profil_Param.objects.all()
        serializer = Profil_ParamSerializer(qs, many=True)
        return Response(serializer.data)


class SimulationReturn(APIView):
    def get(self, request, pk, dt, *args, **kwargs):

        try:
            date_to_lookup = datetime.strptime(dt, "%d%m%y")
        except:
            print("problem with time format")
            return Response(404)
        bin_to_site = {}
        json_object = {}
        json_object["trajets"] = {}
        with connection.cursor() as cursor:
            query = "SELECT * FROM trajet_simu WHERE simu_id={} AND date_trajet='{}'"
            print(query.format(pk, date_to_lookup))
            cursor.execute(query.format(pk, date_to_lookup))
            results = cursor.fetchall()
            temp_dic = {}
            for result in results:
                # On utilise l'id du trajet pour récupérer les objets bulles associés.
                trajets_queryset = Trajet.objects.filter(id_trajet=result[1])
                trajets = TrajetSerializer(trajets_queryset, many=True)
                for trj in trajets.data:
                    for value in trj["bulle"]:
                        temp_dic[value["id_bulle"]] = value
                        querySite = Site.objects.get(id_site=value["id_site"])
                        assigned_site = SiteSerializer(querySite)
                        bin_to_site[value["num_bulle"]] = assigned_site["nom"].value
                json_object["trajets"][trj["id_trajet"]] = {
                    "temps": round(float(result[3]), 2),
                    "poidsc": result[4],
                    "poidsb": result[5],
                    "tournee": result[2],
                    "infos_bulles": temp_dic,
                    "bin_to_site": bin_to_site,
                    "type": result[7],
                    "liste_poids_blanc": [round(float(x)) for x in result[8].strip('][').split(',')] if not result[8] == '' else None,
                    "liste_poids_colore": [round(float(x)) for x in result[9].strip('][').split(',')] if not result[9] == '' else None,
                }

        """for bidule in qs:
            print(bidule.site_depart)
        data = {"tamer": "oui"}"""
        json_object[
            "simulation_result"] = "La simulation a été effectuée avec succès. </br> Veuillez recharger la page pour voir apparaitre la nouvelle simulation."
        return Response(json_object)


class FullSimulationReturn(APIView):
    def get(self, request, pk, *args, **kwargs):
        qs = Simulation.objects.get(id_simu=pk)
        serializer = SimulationInfoSerializer(qs)

        trajets_queryset = Trajet.objects.filter(id_simu=pk)
        trajets = TrajetSerializer(trajets_queryset, many=True)
        json_object = {}
        bin_to_site = {}
        json_object["trajets"] = {}
        with connection.cursor() as cursor:
            for trj in trajets.data:
                trj_to_lookup = trj["id_trajet"]
                query = "SELECT * FROM trajet_simu WHERE trajet_id={}"
                cursor.execute(query.format(trj_to_lookup))
                result = cursor.fetchone()
                temp_dic = {}
                for value in trj["bulle"]:
                    temp_dic[value["id_bulle"]] = value
                    querySite = Site.objects.get(id_site=value["id_site"])
                    assigned_site = SiteSerializer(querySite)
                    bin_to_site[value["num_bulle"]] = assigned_site["nom"].value
                json_object["trajets"][trj["id_trajet"]] = {
                    "type_camion": result[7],
                    "temps": round(float(result[3]), 2),
                    "poidsc": result[4],
                    "poidsb": result[5],
                    "tournee": result[2],
                    "infos_bulles": temp_dic,
                    "bin_to_site": bin_to_site,
                    "semaine": trj["semaine"],
                    "jour": trj["jour"],
                    "trajet_date": result[6],
                    "liste_poids_blanc": [round(float(x)) for x in result[8].strip('][').split(',')] if not result[
                                                                                                                8] == '' else None,
                    # transform string list to list
                    "liste_poids_colore": [round(float(x)) for x in result[9].strip('][').split(',')] if not result[
                                                                                                                 9] == '' else None,
                    # transform string list to list
                }

        return Response(json_object)


class ParamReturn(ModelViewSet):
    serializer_class = Profil_ParamSerializer
    queryset = Profil_Param.objects.all()

    def get_serializer(self, *args, **kwargs):
        if "data" in kwargs:
            data = kwargs["data"]

            # check if many is required
            if isinstance(data, list):
                kwargs["many"] = True

        return super(ParamReturn, self).get_serializer(*args, **kwargs)

    def get(self, request, pk=None):
        # qs = Profil_Param.objects.get(Nom=pk)
        qs = Profil_Param.objects.all()
        serializer = Profil_ParamSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ParamReturn(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request, pk=None):
        param = self.get_object(pk)
        serializer = ParamReturn(param, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        param = self.get_object(pk)
        serializer = ParamReturn(param, data=request.data,
                                 partial=True)  # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return Response(code=201, data=serializer.data)

        return Response(code=400, data="wrong parameters")

    def delete(self, request, pk):
        param = self.get_object(pk)
        param.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LastVidange(APIView):
    def get(self, request, *args, **kwargs):
        yay = Bulles.objects.aggregate(Max('date_vidange'))
        print(yay)
        # return Response(serializer.data)