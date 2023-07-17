"""
Fichier contenant les constantes utiles au projet
"""


CAMION_26T_CAPACITE_EN_KG = 8000
CAMION_44T_CAPACITE_EN_KG = 16000  # vérifier si c'est le bon poids
MAP_DEPOT_NAME_TO_DEPOT_ID = {"Quévy": 1, "Dottignies": 2, "Minérale": 3, "Renaix": 4}  # associations du dépot de départ et d'arrivée d'une tournée (voir database)
BULLES_CAPACITE_EN_KG = 1500
BULLES_ENTERREE_CAPACITE_EN_KG = 1200
TEMPS_DE_PAUSE = 45 # temps de pause par jour en minute
TEMPS_DE_VIDANGE = 7 # temps moyen pour vider une bulle en minute
TEMPS_DEPOT_MINERAL = 20 # temps passé à mineral pour vider la benne chaque jour en minute
TEMPS_DEPOT_RENAIX = 20 # temps passé à renaix pour vider la benne chaque jour en minute
TEMPS_DEPOT_DOTTIGNIES = 15 # temps passé à dottignies pour vider la benne chaque jour en minute
TEMPS_DEPOT_QUEVY = 15 # temps passé à quévy pour vider la benne chaque jour en minute
DICT_TEMPS_DEPOTS = {1 : TEMPS_DEPOT_QUEVY, 2 :TEMPS_DEPOT_DOTTIGNIES, 3 : TEMPS_DEPOT_MINERAL, 4 :  TEMPS_DEPOT_RENAIX }
TAUX_LIMIT=0.3 # taux minimum de remplissage d'une bulle à vider
TEMPS_DEPOT_BENNE = 15  # temps de dépôt de la benne d'un 44T
TEMPS_REPRISE_BENNE = 15  # temps que met un chaffeur pour rattacher la benne à son 44T


