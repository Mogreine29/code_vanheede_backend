""" Fichier de test de la time_matrix, elle se construit sur base de la list Depots"""

from utils import getTimeMatrix
from utils import get_depot
from utils import main_bulles
from datetime import datetime as dt  # Laiser les deux!!!
import datetime

'''creation time_mat'''
date_debut = "2022-12-05"
if date_debut != "":
    date_debut = dt.strptime(date_debut, '%Y-%m-%d').date()
    if date_debut.weekday() == 5:
        date_debut += datetime.timedelta(
            2)  # si date de debut est samedi, on commence la simulation a partir de lundi
    elif date_debut.weekday() == 6:
        date_debut += datetime.timedelta(1)
Depot_id = [1, 3, 1]  # à modifier pour tester les différentes configuration. Ex : [1,3,1] = tournée à quévy passant par minérale et retournant à quévy
Dict_Bulles = main_bulles(Depot_id[0], date_debut, 0.75)  # extrait ensemble des bulles du depot correspondant, Depot_id[0] = id de la tournée
Depots = []
for id in Depot_id:
    dep, _ = get_depot(id)
    Depots.append(dep)  # récupére infos du depot (soit quévy soit dottignies)
Time_Matrix = getTimeMatrix(Depots)

"""Vérification de la time_mat"""
for bulle in Dict_Bulles.values():  # test entre tous les sites
    ids1 = bulle.id_site
    for bulle2 in Dict_Bulles.values():
        ids2 = bulle2.id_site
        print(f"test entre tous les sites : {Time_Matrix[ids1][ids2]}")

for depot in Depots:  # test entre tous les depots
    ids1 = depot.id_site
    for depot2 in Depots:
        ids2 = depot2.id_site
        print(f"test entre tous les depots : {Time_Matrix[ids1][ids2]}")

for depot in Depots:  # test entre tous les depots vers toutes les bulles
    ids1 = depot.id_site
    for bulle2 in Dict_Bulles.values():
        ids2 = bulle2.id_site
        print(f"test entre tous les depots vers toutes les bulles : {Time_Matrix[ids1][ids2]}, ids1 = {ids1}, ids2 = {ids2}")

for bulle in Dict_Bulles.values():  # test entre toutes les bulles vers tous les depots
    ids1 = bulle.id_site
    for depot2 in Depots:
        ids2 = depot2.id_site
        print(f"test entre toutes les bulles vers tous les depots : {Time_Matrix[ids1][ids2]}, ids1 = {ids1}, ids2 = {ids2}")




