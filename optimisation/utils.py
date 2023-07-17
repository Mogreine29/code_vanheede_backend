import logging
from datetime import date, timedelta, datetime
import calendar
import mysql.connector
import json
import random
from math import *
from holidays import country_holidays
import numpy as np
import pandas as pd

try:  # import depuis serveur
    from optimisation.data.constante_config import *
    from global_var import ON_SERVER
except ImportError:  # import pour le main de la partie opti
    from data.constante_config import *
    try:
        from backend.global_var import ON_SERVER
    except ImportError:
        from Vanheede_VF.backend.global_var import ON_SERVER


"""
Classe Truck
"""


class truck():
    def __init__(self, depot, capacity, Id, is26T):
        self.Id = Id
        self.depot = depot
        self.capacity = capacity
        self.route = []  # trajet du camion
        self.is26T = is26T
        self.isRouted = False
        self.remplissage = 0
        self.remplissagec = 0
        self.remplissageb = 0
        self.time = 0
        self.day = 1

    def time_road(self, time_mat):
        """
        calcul du temps de tournée d'un camion
        :param time_mat: matrice des temps
        :type time_mat: ndarray
        :return: ajout du temps de trajet d'un objet_camion
        :rtype: objet_camion
        """
        route = self.route
        bulles = []
        temps = 0
        bulles = route


        for i, bulle in enumerate(bulles[0:-2]):
            s = time_mat[route[i].id_site][route[i + 1].id_site]  # temps de trajet de la bulle i à j
            temps += s
            temps += TEMPS_DE_VIDANGE * 60  # temps de vidange d'une bulle
            if i != 0 and i != (len(bulles) - 1) and bulle.Id < 0 :
                temps += DICT_TEMPS_DEPOTS[(- bulle.Id)]
        temps += TEMPS_DE_PAUSE * 60  # temps de pause d'un chauffeur
        if not self.is26T:
            temps += TEMPS_DEPOT_BENNE * 60
            temps += TEMPS_REPRISE_BENNE * 60
            if route[-2].Id == -3 or route[-2].Id == -4:  # si on passe par la recyclerie dans le trajet
                t = time_mat[route[-3].id_site][route[-2].id_site]  # retire le temps de trajet dernière bulle -> recyclerie
                temps -= t
            else:
                t = time_mat[route[-2].id_site][route[-1].id_site]  # retire le temps de trajet dernière bulle -> depot init
                temps -= t
            """recherche de première bulle qui va faire déborder la première benne du 44T"""
            pds = 0
            idx_site = 0  # me donne le site contenant la bulle qui va faire déborder la première benne du 44T
            for i, bulle in enumerate(bulles[0:-1]):
                if not bulle.isDepot:
                    pds += bulle.poids_week[-1]
                if pds >= CAMION_44T_CAPACITE_EN_KG/2:
                    idx_site = bulle.id_site
                    break
            if route[-2].Id == -3 or route[-2].Id == -4:  # si on passe par la recyclerie dans le trajet
                t1 = time_mat[route[-3].id_site][idx_site]
                temps += t1
                t2 = time_mat[idx_site][route[-2].id_site]
                temps += t2
            else:
                t1 = time_mat[route[-2].id_site][idx_site]
                temps += t1
                t2 = time_mat[idx_site][route[-1].id_site]
                temps += t2

        try:
            if route[-2].Id == -3:  # si Quévy ajouter Minérales en plus (c'est le temps de vider le camion)
                temps += TEMPS_DEPOT_MINERAL * 60
        except IndexError:
            print("No route found")
        self.time = temps
        return self.time


"""
Classe Bulles
"""


class Bulle:
# variable static pour le constructeur pour incrémenter l'id négative
    def __init__(self, Id, poidsb, poidsc,latitude, longitude, type_bulle, poids_utile, couleur, vit_remplissageb,
                 vit_remplissagec,vitb_mois,vitc_mois,last_vidange, site, id_site, limit_delta, dateref, isDepot = False):
        if isDepot :  # due à un artéfact de code, les dépots doivent être mis dans des objets bulles, on leur mets une id négative pour les distinguer des vraies bulles (déso)
            self.Id = -Id
            self.id_site = -Id
            self.isDepot = isDepot
        else :
            self.Id = Id
            self.id_site = id_site
            self.isDepot = isDepot
        self.poidsb = poidsb
        self.poidsc = poidsc
        self.poids = poidsb + poidsc
        self.poidsb_week = []
        self.poidsc_week = []
        self.poids_week = []
        self.latitude = latitude
        self.longitude = longitude
        self.site = site
        self.type_bulle = type_bulle
        self.poids_utile = poids_utile
        self.couleur = couleur
        self.vit_remplissageb = vit_remplissageb
        self.vit_remplissagec = vit_remplissagec
        self.vitb_mois= vitb_mois# vitesse moyenne par mois
        self.vitc_mois=vitc_mois
        self.last_vidange = last_vidange
        self.limit_delta = limit_delta
        self.Truck = 0
        self.dateref = dateref
        self.is_emergency = 0 # 0 si bulle pas urgente
    def assignToTruck(self, IdTruck):
        self.Truck = IdTruck

    def __lt__(self, other):  # magic method timopisse tu m'as trahis       #FIXME  c'est quoi ça ??
        return self.poids < other.poids


"""
Connexion a la base de données + toutes les fonctions
"""


def connect_to_db():
    if ON_SERVER :
      host="webmaster.ig.umons.ac.be"
      user="vanheede"
      password="xXZq25d74zsn2-a"
    else :
      host="db"
      user="vanheede"
      password="xXZq25d74zsn2-a"
      
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database="vanheede",
        port="3306")
    mycursor = mydb.cursor()
    return mydb, mycursor


class Depot:
    def __init__(self, Id, vect_temps, latitude, longitude):
        self.Id = Id
        self.vect_temps = vect_temps
        self.latitude = latitude
        self.longitude = longitude





def byte_to_list(b):
    b = b.strip("[")
    b = b.strip("]")
    b = b.split(",")
    try:
        b = [float(x) for x in b]
    except ValueError:  # si jamais None est présent dans la list
        idx = []
        while ' None' in b:  # identification et remplacement de tous les None
            idx.append(b.index(' None'))
            b[idx[-1]] = '0.0'
        b = [float(x) for x in b]
        moy = np.mean(b)
        for i in idx:  # remplace chaque None par la valeur moyenne de la list
            b[i] = moy
    return b


def del_bulles(liste_bulles, remove_indices):
    liste_bulles = [i for j, i in enumerate(liste_bulles) if j not in remove_indices]
    return liste_bulles


def get_infos(id_depot, type_):
    mydb, mycursor = connect_to_db()
    if type_ == "site":
        # Récupération des ID des sites
        if id_depot == 1:
            mycursor.execute("SELECT * FROM site WHERE id_depot = 1")
        else:
            mycursor.execute("SELECT * FROM site WHERE id_depot = 2")
    else:
        if id_depot == 1:
            mycursor.execute("SELECT * FROM bulles where id_depot = 1")
        else:
            mycursor.execute("SELECT * FROM bulles where id_depot = 2")
    myresult = mycursor.fetchall()
    mycursor.close()
    mydb.close()
    return myresult


def get_depot(id_depot):
    mydb, mycursor = connect_to_db()
    mycursor.execute(f"SELECT time_vector, latitude, longitude FROM depot WHERE id_depot={id_depot}")
    myresult = mycursor.fetchall()
    for x in myresult:
        dateref = date.today()
        depot = Bulle(Id=id_depot, poidsb=0, poidsc=0, latitude=float(x[1]), longitude=float(x[2]),type_bulle="depot", poids_utile=0, couleur="depot", vit_remplissageb=0, vit_remplissagec=0,vitb_mois=[],vitc_mois=[], last_vidange=0, site=0, id_site=id_depot, limit_delta=999, dateref=dateref, isDepot=True)
    mycursor.close()
    mydb.close()
    return depot, byte_to_list(x[0])


def get_ids(id_depot):
    mydb, mycursor = connect_to_db()
    # Récupération des ID des sites
    if id_depot == 1:
        mycursor.execute("SELECT Id_site FROM site WHERE Id_site IN (SELECT Id_site FROM bulles WHERE id_depot = 1)")
    else:
        mycursor.execute("SELECT Id_site FROM site WHERE Id_site IN (SELECT Id_site FROM bulles WHERE id_depot = 1)")
    myresult = mycursor.fetchall()
    sites = [x[0] for x in myresult]
    mycursor.close()
    mydb.close()
    return sites


def clean_matrix(vect_temps, vect_dist, id_depot):
    if id_depot == 1:
        bulles = get_ids(2)  # recupere id des bulles de l'autre zone
    else:
        bulles = get_ids(1)  # recupere id des bulles de l'autre zone
    # Construction de la matrice des distances
    dist = byte_to_list(vect_dist, "distance")
    dist = del_bulles(dist, bulles)
    # Construction de la matrice des temps
    time = byte_to_list(vect_temps, "temps")
    time = del_bulles(time, bulles)
    return time, dist


def look_bulles(id_site):
    mydb, mycursor = connect_to_db()
    # Récupération des ID des sites
    mycursor.execute("SELECT id_bulle,colories FROM bulles where id_site = {}".format(id_site))
    myresult = mycursor.fetchall()
    tuple_ = []
    for x in myresult:
        tuple_.append((x[0], x[1]))
    mycursor.close()
    mydb.close()
    return tuple_


def getTimeMatrix(depots):
    sites = main_site(abs(depots[0].Id))  # les id des depot sont en positif dans la DB
    timeMat = {}

    # ajout de vecteur temps sites dans la time matrix
    for id_site, site in sites.items():
        temp = {}
        timeVec = site.time_vector
        len_time_vec_site = len(timeVec)
        for i, id_site1 in enumerate(sites.keys()):
            temp[id_site1] = timeVec[i]
        timeMat[id_site] = temp

    # ajout des vecteurs temps depôts dans la time matrix
    for dep in depots:
        temp = {}
        _, timeVec = get_depot(abs(dep.Id))
        if dep.Id == -3 and depots[0].Id == -1:  # je suis à quevy et mineral est dans la tournée
            timeVec = timeVec[-len_time_vec_site:]
        elif dep.Id == -3 and depots[0].Id == -2:  # je suis à dottignies et mineral est dans la tournée
            timeVec = timeVec[1:len_time_vec_site + 1]  # j'enlève le premier élément car c'est le temps mineral -> mineral
        else:
            timeVec.remove(timeVec[0])  # permet d'avoir en première position le temps entre le depot et le premier site
        for i, id_site1 in enumerate(sites.keys()):
            temp[id_site1] = timeVec[i]  # ajout du trajet entre depot et site
            try:
                timeMat[id_site1][dep.Id] = timeVec[i]  # ajout du trajet entre site et depot () (temps aller = temps retour car j'ai pas accès au vrai temps)
            except KeyError:
                pass
        timeMat[dep.Id] = temp

    # ajout du temps de trajet entre les depots
    try:
        df = pd.read_excel(r'optimisation/data/time_depots.xlsx', sheet_name='Feuil1')
    except FileNotFoundError:
        df = pd.read_excel(r'data/time_depots.xlsx', sheet_name='Feuil1')
    for dep in MAP_DEPOT_NAME_TO_DEPOT_ID.keys():  # ordre = quévy, dottignies, mineral, renaix
        id_dep = - MAP_DEPOT_NAME_TO_DEPOT_ID[dep]  # les id sont négatifs
        for i in range(len(MAP_DEPOT_NAME_TO_DEPOT_ID)):
            try:
                timeMat[id_dep][-(i + 1)] = df[dep][i]
            except KeyError:  # si jamais je suis dans le cas quévy, il est normal que l'id site de dottignies ne soit pas dans la matrice
                pass
    return timeMat


class site:
    def __init__(self, id_site, time_vector, vitesse_b, vitesse_c, variance_b, variance_c, longitude,
                 latitude, nombre_bulles, last_vidange, idsBulles_colors):
        self.id_site = id_site
        self.time_vector = time_vector
        self.vitesse_b = vitesse_b
        self.vitesse_c = vitesse_c
        self.variance_b = variance_b
        self.variance_c = variance_c
        self.longitude = longitude
        self.latitude = latitude
        self.nombre_bulles = nombre_bulles
        self.last_vidange = last_vidange
        self.idsBulles_colors = idsBulles_colors


def main_site(id_depot):  # ajouter capacité totale a la place de nombre bulle?
    sites = {}
    sites_ok = get_infos(id_depot, "site")
    for elem in sites_ok:
        id_site = elem[0]
        vect_temps = byte_to_list(elem[3])
        if elem[5] is None:
            vitesse_b = 0.0
            vitesse_c = 0.0
            variance_b = 0.0
            variance_c = 0.0
        else:
            vitesse_b = float(elem[5])
            vitesse_c = float(elem[6])
            variance_b = float(elem[7])
            variance_c = float(elem[8])
        longitude = float(elem[10])
        latitude = float(elem[11])
        nombre_bulles = float(elem[12])
        last_vidange = elem[13]
        idsBulles_colors = look_bulles(id_site)
        a = site(id_site, vect_temps, vitesse_b, vitesse_c, variance_b, variance_c, longitude, latitude,
                 nombre_bulles, last_vidange, idsBulles_colors)
        sites[id_site] = a
    return sites
def string_to_list(string_var):
    string_var =  string_var[1:len( string_var) - 1]
    string_list=string_var.split(',')
    float_list=[float(i) for i in string_list if i !='']
    return float_list


def main_bulles(id_depot, date_debut, treshold):
    compter_bulle = 0
    bulles = {}
    bulles_ok = get_infos(id_depot, "bulle")
    sites = main_site(id_depot)
    
    print("import des données...")

    Affichage_progression = 0
    for elem in bulles_ok:
        Affichage_progression +=1
        if Affichage_progression == len(bulles_ok)//4:
            print("25 %")
        if Affichage_progression == len(bulles_ok)//2:
            print("50 %")
        if Affichage_progression == 3*len(bulles_ok)//4:
            print("75 %")
        id_bulle = elem[0]
        id_site = int(elem[10])
        last_vidange = elem[4]
        
        latitude = elem[7]
        longitude = elem[8]
        # vect_temps, vect_distance = clean_matrix(elem[2], elem[3], id_depot)
        type_bulle = elem[5]
        couleur = elem[6]
       

        vitb_mois= string_to_list(elem[11])
        vitc_mois=string_to_list(elem[12])
        poidsMaxVerreBlanc = 0
        poidsMaxVerreCouleur = 0
        if type_bulle == "Double":
            poidsMaxVerreBlanc = BULLES_CAPACITE_EN_KG / 2
            poidsMaxVerreCouleur = BULLES_CAPACITE_EN_KG / 2
        elif couleur == "White":
            poidsMaxVerreBlanc = BULLES_CAPACITE_EN_KG
        else:
            poidsMaxVerreCouleur = BULLES_CAPACITE_EN_KG


        dateref = date_debut
        vit_remplissageb=vitb_mois[dateref.month-1]
        vit_remplissagec=vitc_mois[dateref.month-1]


        nbj_passe = abs(date_debut - last_vidange).days

        # estimation précise avec les différentes vitesses par mois:
        poidsb = 0
        poidsc = 0

        month_D = (last_vidange.month) - 1
        month_F = (dateref.month)

        date_Diff_C = last_vidange
        # attention si changement d'années

        if month_D>month_F:
            rngmonths = []
            rngmonths.append(month_D)
            m=1
            while (month_D+m) % 12 !=month_F:
                rngmonths.append((month_D+m) % 12)
                m+=1
        else:
            rngmonths = range(month_D, month_F)


        for i in rngmonths:
            vitesse_b = vitb_mois[i]
            vitesse_c = vitc_mois[i]

            year = date_Diff_C.year
            month = date_Diff_C.month

            rng = calendar.monthrange(year, month)
            date_Diff_F = date(year, month, rng[1])

            diff_jour = date_Diff_F - date_Diff_C
            diff_jour = diff_jour.days


            if (dateref - date_Diff_F).days < 0:
                date_Diff_F = dateref
                diff_jour = date_Diff_F - date_Diff_C
                diff_jour = diff_jour.days
            else:
                date_Diff_C = date_Diff_F + timedelta(days=1)


            poidsb += diff_jour * vitesse_b
            poidsc += diff_jour * vitesse_c

        deltab = 1000

        if poidsMaxVerreBlanc != 0:
            if poidsMaxVerreBlanc > poidsb >= (treshold * poidsMaxVerreBlanc):
                logging.info("Bulle en surcharge")
                deltab = 0
            elif poidsb >= poidsMaxVerreBlanc:
                deltab = 0
                poidsb = poidsMaxVerreBlanc
            else:
                deltab = ((treshold * poidsMaxVerreBlanc) - poidsb) / (vit_remplissageb + 0.01)
        deltac = 1000

        if poidsMaxVerreCouleur != 0:
            if poidsMaxVerreCouleur > poidsc >= treshold * poidsMaxVerreCouleur:
                logging.info("Bulle en surcharge")
                deltac = 0
            elif poidsc >= poidsMaxVerreCouleur:
                deltac = 0
                poidsc = poidsMaxVerreCouleur
            else:
                deltac = ((treshold * poidsMaxVerreCouleur - poidsc)) / (vit_remplissagec + 0.01)
        limit_delta = int(min(deltab, deltac))


        if len(type_bulle.split(" "))>1:
           poids_utile = BULLES_ENTERREE_CAPACITE_EN_KG
        else:
           poids_utile = BULLES_CAPACITE_EN_KG

        b = Bulle(id_bulle, poidsb, poidsc, latitude, longitude, type_bulle, poids_utile, couleur, vit_remplissageb,
                  vit_remplissagec,vitb_mois,vitc_mois, last_vidange, site, id_site, limit_delta, dateref, isDepot=False)

        bulles[id_bulle] = b
    print("100 %")   
    return bulles


"""
Code concernant le Two-Opt
"""



def get_time(time_mat, route):
    obj = 0
    for i in range(len(route) - 1):
        obj += time_mat[route[i].id_site][route[i + 1].id_site]
    return obj


def two_opt(route, time_mat):
    """
    Algorithme qui trouve les meilleures permutations de bulles dans un trajet pour minimiser le temps
    méthode : https://fr.wikipedia.org/wiki/2-opt
    :param route: liste d'objets contenant bulles et dépots pour la simulation (un cluster dans notre cas)
    :type route: list
    :param time_mat: la matrice des temps entre les dépots
    :type time_mat: list
    :return: best = chemin le plus court entre les bulles (le chemin à prendre = ordre de objets dans best)
    :rtype: list
    """
    best = route
    improved = True
    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                if j - i == 1:
                    continue
                if get_time(time_mat, best[:i] + best[j - 1:i - 1:-1] + best[j:]) - get_time(time_mat, best) < -0.01:
                    best[i:j] = best[j - 1:i - 1:-1]
                    improved = True
        route = best
    return best


"""
Code pour update du dico bulle après une semaine
"""


def clean_route(liste):
    listef = []
    if isinstance(liste[1], list):
        listef = []
        for i in liste[1][:-1]:
            listef.append(i)
        for i in liste[2][1:-1]:
            listef.append(i)
    else:
        for bulle in liste:  # on supprime les dépots
            if bulle.Id > 0:
                listef.append(bulle)
    return listef


def update_dict_weekly(camions, dict_bulles,date_debut):
    date_debut += timedelta(days=7-date_debut.weekday())
    dictio = dict_bulles.copy()
    for i, j in dictio.items():  # mise a jour des données de l'ensemble des bulles comme si aucune n'avait été vidée
        j.limit_delta -= 7

        j.dateref += timedelta(days=7-j.dateref.weekday())
        j.vit_remplissagec = j.vitc_mois[j.dateref.month - 1]
        j.vit_remplissageb = j.vitb_mois[j.dateref.month - 1]
        j.poidsb += j.vit_remplissageb * 7
        j.poidsc += j.vit_remplissagec * 7
        j.poids = j.poidsb + j.poidsc
        j.is_emergency = False


        #mise à jour des
    routes = [t.route for t in camions]
    bulleslistes = [clean_route(route) for route in routes]
    bulles = []
    for liste in bulleslistes:
        for bulle in liste:
            bulles.append(bulle)
    for bulle in bulles:  # mise à jour des bulles ayant été vidées calcul du poids pour lundi prochain

        a = dictio[bulle.Id]
        a.last_vidange = bulle.last_vidange

        delta = 7 - bulle.last_vidange

        a.poidsb = delta * a.vit_remplissageb
        a.poidsc = delta * a.vit_remplissagec
        a.poids = a.poidsb + a.poidsc

        poidsMaxVerreBlanc = 0
        poidsMaxVerreCouleur = 0
            
        if a.couleur == "White" or a.couleur == "Coloured":
            poidsMaxVerreBlanc = a.poids_utile
        elif a.couleur == "Coloured":
            poidsMaxVerreCouleur = a.poids_utile
        else:
            poidsMaxVerreBlanc = a.poids_utile / 2
            poidsMaxVerreCouleur = a.poids_utile / 2

        a.limit_delta = int(min((poidsMaxVerreBlanc - a.poidsb) / (a.vit_remplissageb + 0.001),
                                (poidsMaxVerreCouleur - a.poidsc) / (a.vit_remplissagec + 0.001)))

        dictio[bulle.Id] = a
    return dictio,date_debut

#TODO correspond à days2 dans le main, n'est plus utilisé pour l'instant
def prevision_days(Trucks, days, Max_time,Time_Matrix,numberOfTruck) :
    """
        Fonction qui va prédir le nombre de jour en regroupant des trajets si le temps est inférieur au temps max ( 2 aller retour de Quévi) sans modifier les objets Trucks
        :param trucks: La liste des camions de la semaine
        :type trucks : list
        :param dict_bulles: dictionaire avec toute les bulles
        :type dict_bulles: dict[id_bulles] = objet_bulles
        :param days: Le nombre de jours de travail actuel
        :type days: int
        :param Max_time: temps max par jour
        :type Max_time: int
        :return: days: Le nombre de jours prédit
        :rtype: int
    """
    # ordonne les camions par ordre décroissant de poids le dernier jour
    sorted_weight_truck = {}


    for truck in Trucks:
        weight = 0
        for bulle in truck.route:
            if bulle.poids > 0:
                weight += bulle.poids_week[-1]  # change
        sorted_weight_truck[truck]=weight # chaque camion va avoir son poids calculé pour chacun des jours de ramassage de la semaine

    trucks_sorted= [truck for truck,weigth in sorted(sorted_weight_truck.items(),key=lambda t:t[1], reverse= True )]

    for num, truck in enumerate( trucks_sorted ):
        if num < len(trucks_sorted)-1 :
            for num2 in range(num+1,len(trucks_sorted)):
               if trucks_sorted[num].time_road(Time_Matrix)+trucks_sorted[num2].time_road(Time_Matrix) < Max_time:

                trucks_sorted.pop(num2)
                break

    days = ceil(len(trucks_sorted)/numberOfTruck)
    return days


"""
Regroupement de trajets 
"""

def multiroute(Trucks, days, Max_time,Time_Matrix,numberOfTruck) :
    """
        Fonction qui va regrouper des trajets si le temps est inférieur au temps max ( 2 aller retour de Quévi)
        :param trucks: La liste des camions de la semaine
        :type trucks : list
        :param dict_bulles: dictionaire avec toute les bulles
        :type dict_bulles: dict[id_bulles] = objet_bulles
        :param days: Le nombre de jours de travail actuel
        :type days: int
        :param Max_time: temps max par jour
        :type Max_time: int
        :return: trucks: La liste avec les routes mis a jour,
        :rtype: list
    """
    # ordonne les camions par ordre décroissant de poids le dernier jour
    sorted_weight_truck = {}

    for truck in Trucks:
        weight = 0
        for bulle in truck.route:
            if bulle.poids > 0:
                weight += bulle.poids_week[-1]  # change
        sorted_weight_truck[truck]=weight # chaque camion va avoir son poids calculé pour chacun des jours de ramassage de la semaine

    trucks_sorted= [ truck for truck,weigth in sorted(sorted_weight_truck.items(),key=lambda t:t[1], reverse= True )]

    for num, truck in enumerate( trucks_sorted ):
        if num < len(trucks_sorted)-1 :
            for num2 in range(num+1,len(trucks_sorted)):
               if trucks_sorted[num].is26T == trucks_sorted[num2].is26T and trucks_sorted[num].time_road(Time_Matrix)+trucks_sorted[num2].time_road(Time_Matrix)<Max_time:
                # on met les trajets ensembles
                trucks_sorted[num].route += trucks_sorted[num2].route[1:]
                trucks_sorted.pop(num2)
                break

    days = ceil(len(trucks_sorted)/numberOfTruck)
    return trucks_sorted , days
"""
Fonction qui assigne les camions à un jour particulier
"""


def day_assignment(trucks=[], dict_bulles={}, number_of_days=int, Remplissage_camion_limite=int,week = int, date_debut = date):
    """
    Fonction qui va assigner à chaque camion, le meilleur jour pour qu'il fasse sa tournée
    en fonction des autres tournées et des poids des bulles
    :param trucks: La liste des camions de la semaine
    :type trucks : list
    :param dict_bulles: dictionaire avec toute les bulles
    :type dict_bulles: dict[id_bulles] = objet_bulles
    :param number_of_days: Le nombre de jours de travail par semaine
    :type number_of_days: int
    :param Remplissage_camion_limite: ratio de limite de remplissage du camion (de 0 à 1)
    :type Remplissage_camion_limite: int
    :return: trucks: La liste avec l'attribut day mis a jour, dict_bulles: Le dico bulle avec les dates de dernières vidanges mises à jour
    :rtype: list, dict[id_bulles] = objet_bulles
    """
    sorted_weight_26 = {}
    sorted_weight_44 = {}
    small_truck = False
    big_truck = False

    # current year
    currentDateTime = datetime.now()
    date = currentDateTime.date()
    year = date.strftime("%Y")
    # all public holydays for that year
    JOURS_FERIE_BELGIQUE = country_holidays('BE', years = int(year))
    JOURS_FERIE_BELGIQUE.update(country_holidays('BE', years=int(year)+1))



    for truck in trucks:
        if truck.is26T:
            sorted_weight_26[truck] = []
            small_truck = True
        else:
            sorted_weight_44[truck] = []
            big_truck = True


    #Dans cette boucle on pour chaque jour le poids qu'aurait chaque camion si ils font leur tournée ce jour là, ce qui va permettre de dire quel camion fait sa tournée quel jour
    for day in range(5-date_debut.weekday()): #calcul sur toute la semaine
        truckAvecBulleUrgent26 = []
        truckAvecBulleUrgent44 = []
        for truck in trucks:
            road_weight = 0
            if truck.is26T:
                for bulle in truck.route:
                    if bulle.poids > 0:
                        road_weight += bulle.poids_week[day] #change
                    if bulle.is_emergency == 1 and truck not in truckAvecBulleUrgent26:  # Si c'est un camion avec une bulle urgent, on l'identifie UNE fois
                        truckAvecBulleUrgent26.append(truck)
                sorted_weight_26[truck].append(road_weight)  # chaque camion va avoir son poids calculé pour chacun des jours de ramassage de la semaine
            else:
                #FIXME possible que l'utilisation du set ici, mélange la liste qu'ils ont fait et change l'ordre des bulles a ramasser
                road = truck.route  # set pour supprimer les doublons ?
                for bulle in road:
                    if bulle.poids > 0:
                        road_weight += bulle.poids_week[day] #change
                    if bulle.is_emergency == 1 and truck not in truckAvecBulleUrgent44:
                        truckAvecBulleUrgent44.append(truck)
                sorted_weight_44[truck].append(road_weight)

    # pour éviter les divisions par 0
    if number_of_days == 0:
        camions_max_par_jour = 0
    else:
        camions_max_par_jour = ceil(len(trucks) / number_of_days)

    day = 0
    compteur_camion_semaine = 0
    compteur_camions_jour = 0
    emergency = False

    # pour chaque camion disposant d'une bulle urgente sur sa tournée, on lui attribue le premier jour de la semaine
    a = [i.Id for i, j in sorted_weight_26.items()]
    b = [i.Id for i, j in sorted_weight_44.items()]
    for truck in truckAvecBulleUrgent44:
        truck.day = day
        compteur_camions_jour += 1
        if compteur_camions_jour == camions_max_par_jour:
            day += 1
        truck.remplissage = sorted_weight_44[truck][0]
        sorted_weight_44.pop(truck)
        emergency = True
    for truck in truckAvecBulleUrgent26:
        truck.day = day
        compteur_camions_jour += 1
        if compteur_camions_jour == camions_max_par_jour:
            day += 1
        truck.remplissage = sorted_weight_26[truck][0]
        sorted_weight_26.pop(truck)
        emergency = True

#    for day in range(number_of_days):  # A quel moment on assigne aux objets de la liste Trucks un jour? Pcq ici rien est sauvé?
    ferie=0
    while day < number_of_days and date_debut.weekday()+day <5 :
        dateSimulated = date_debut + timedelta(days=(day ))
        if not dateSimulated in JOURS_FERIE_BELGIQUE:
            if emergency is False:
              compteur_camions_jour = 0
            else:
                emergency = False
            while compteur_camions_jour < camions_max_par_jour and compteur_camion_semaine < len(trucks):
                if small_truck and sorted_weight_26 and compteur_camions_jour < camions_max_par_jour:  # si y a des 26 T
                    max = [0, -float("inf")]  # Une liste avec truck et poids de la route associé
                    for key, elem in sorted_weight_26.items():  # pour chaque jours en commençant par le pemier, on va assigner le camion pour lequel le poids est le plus grand
                        if elem[day] > max[1]:
                            max = [key, elem[day]]
                    max[0].day =day + date_debut.weekday()
                    max[0].remplissage = max[1]
                    sorted_weight_26.pop(max[0])
                    compteur_camions_jour += 1
                    compteur_camion_semaine += 1
                if big_truck and sorted_weight_44 and compteur_camions_jour < camions_max_par_jour and compteur_camion_semaine < len(
                        trucks):  # si y a des 44T
                    max = [0, -float("inf")]
                    for key, elem in sorted_weight_44.items():
                        if elem[day] > max[1]:
                            max = [key, elem[day]]
                    max[0].day =day + date_debut.weekday()
                    max[0].remplissage = max[1]
                    sorted_weight_44.pop(max[0])
                    compteur_camions_jour += 1
                    compteur_camion_semaine += 1
        else:
            number_of_days += 1
            if number_of_days >= 4:
                number_of_days = 4
        day +=1
    if len(sorted_weight_26.keys()) > 0:
        for key in sorted_weight_26.keys():
            trucks.remove(key)
    if len(sorted_weight_44.keys()) > 0:
        for key in sorted_weight_44.keys():
            trucks.remove(key)
            
            
    for truck in trucks:
        total_b = 0
        total_c = 0

        for bulle in truck.route:
            if len(bulle.poids_week) == 0:
                bulle.poidsb = 0
                bulle.poidsc = 0
                bulle.poids  = 0
            else:
                bulle.poidsb = bulle.poidsb_week[truck.day-date_debut.weekday()]
                bulle.poidsc = bulle.poidsc_week[truck.day-date_debut.weekday()]
                bulle.poids  = bulle.poids_week[truck.day-date_debut.weekday()]
                total_b    += bulle.poidsb
                total_c    += bulle.poidsc

        truck.remplissageb = total_b
        truck.remplissagec = total_c
        truck.remplissage  = truck.remplissagec + truck.remplissageb

    for truck in trucks:

        if truck.is26T:  # 26T
            assigned_day = date_debut.weekday()+ abs(truck.day - (number_of_days - 1))
            for bulle in truck.route:
                if bulle.Id> 0:
                    dict_bulles[bulle.Id].last_vidange = assigned_day
        else:
            assigned_day = date_debut.weekday()+ abs(truck.day - (number_of_days - 1))
            road = truck.route
            for bulle in road:
                if bulle.Id > 0:
                    dict_bulles[bulle.Id].last_vidange = assigned_day

    return trucks, dict_bulles


"""
Fonction de monitoring des bulles qui dépassent
"""



def monitoring(trucks=[], dict_bulles={}, bulles_debordent={}, remplissage_limite=int):
    """
    Fonction pour permettre de voir les bulles qui vont déborder dans la semaine
    :param trucks: Liste des camions
    :param dict_bulles: Dictionaire avec toutes les bulles
    :return: # print le monitoring
    """
    to_empty = []
    for id, bulle in dict_bulles.items():
        # Recherche des bulles à vider dans la semaine
            
        if bulle.poids_week[-1] > remplissage_limite * bulle.poids_utile:
            to_empty.append(bulle)
    nbr_bulle = len(to_empty)
    for truck in trucks:
        if truck.is26T:
            for bulle in truck.route:
                if bulle in to_empty:
                    to_empty.remove(bulle)
        else:
            road = truck.route
            for bulle in road:
                if bulle in to_empty:
                    to_empty.remove(bulle)
    for bulle in to_empty:
        bulles_debordent.append(bulle)
        # print(f"Cette semaine, la bulle {bulle.Id} déborde")
    if len(to_empty) == 0:
        logging.info(
            f"MONITORING: Sur les {nbr_bulle} qu'il fallait aller chercher, {len(to_empty)} n'ont pas été ramasées")
    else:
        logging.info(
            f"MONITORING: Sur les {nbr_bulle} qu'il fallait aller chercher, {len(to_empty)} n'ont pas été ramasées")
    return bulles_debordent


"""
Monitoring de la solution finale
"""



"""
Calcul du remplissage moyen 
"""


def remplissage_moyen(camion):
    route = camion.route
    merge_road = []
    for elem in route:
        if isinstance(elem, list):
            merge_road += elem
        else:
            if elem.couleur != "depot":
                merge_road.append(elem)
    merge_road = set(merge_road)
    remplissage = 0
    nbbulles = len(merge_road)
        
    for elem in merge_road:
        remplissage += elem.poids / elem.poids_utile
    remplissage_moyen = remplissage / nbbulles
    return remplissage_moyen


"""
Fonction qui ajoute des spikes aléatoires dans les vitesses de remplissage
"""


def spikes_remplissage(dict_bulles, pourcentage):
    for i in dict_bulles.keys():
        if dict_bulles[i].couleur == "Coloured":
            # random_spike = random.gauss(0,pourcentage*dict_bulles[i].vit_remplissagec)
            # dict_bulles[i].vit_remplissagec += random_spike
            random_spike = random.gauss(0, pourcentage * dict_bulles[i].poidsc)
            dict_bulles[i].poidsc += random_spike
        elif dict_bulles[i].couleur == "White":
            # random_spike = random.gauss(0,pourcentage*dict_bulles[i].vit_remplissageb)
            # dict_bulles[i].vit_remplissageb += random_spike
            random_spike = random.gauss(0, pourcentage * dict_bulles[i].poidsb)
            dict_bulles[i].poidsb += random_spike
        else:
            # random_spike = random.gauss(0,pourcentage*dict_bulles[i].vit_remplissagec)
            # dict_bulles[i].vit_remplissagec += random_spike
            # random_spike = random.gauss(0,pourcentage*dict_bulles[i].vit_remplissageb)
            # dict_bulles[i].vit_remplissageb += random_spike
            random_spike = random.gauss(0, pourcentage * dict_bulles[i].poidsc)
            dict_bulles[i].poidsc += random_spike
            random_spike = random.gauss(0, pourcentage * dict_bulles[i].poidsb)
            dict_bulles[i].poidsb += random_spike
    return dict_bulles



def separation_route_en_plusieurs(solution) :
    """
    Dans les cas où on a plusieurs trajets par jour, les trajets s'accumulent dans le même attribut route.
    Cette fonction le détecte et sépare en une liste de trajets dans l'attribut route

    :param solution: L'objet solution retourné par l'algorithme juste avant la fin de la fonction main
    :type solution: object
    :return: L'objet solution avec les routes séparés si nécessaire
    :rtype: object
    """
    for week in solution :
        for truck in week:
            numberOfDepot = []
            newRoute = []
            for i,bulle in enumerate(truck.route):
                if bulle.Id < 0:
                    numberOfDepot.append(i)
            if len(numberOfDepot) > 2:
                for j in range(len(numberOfDepot)-1):
                    newRoute.append(truck.route[numberOfDepot[j]:numberOfDepot[j+1]])
                newRoute.append(truck.route[numberOfDepot[j+1]])
                truck.route = newRoute
            else :
                truck.route = [truck.route]


    return solution

def tri_solution(solution):
    """
    Lors du calcul du la solution les camions sont calculés et ranger dans le désordre.
    Cette fonction permet de trier et de ranger les camions correctement dans les bons jours de la semaine.
    Tout cela dans le but d'avoir un affichage correct dans l'Excel.
    
    :param solution: L'objet solution retourné par l'algorithme juste avant la fin de la fonction main
    :type solution: object
    :return: L'objet solution avec les camions triés dans l'ordre des jours
    :rtype: object
    """
    solution2 = []
    for truck in solution:
        truck.sort(key=lambda x: x.day)
        solution2.append(truck)
        
    return solution2