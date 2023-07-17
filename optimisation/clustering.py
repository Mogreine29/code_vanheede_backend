# -*- coding: utf-8 -*-
""""
Created on Fri Nov 26 13:44:18 2021
@author: antoi
"""

import logging
import pandas as pd
from sklearn import cluster
from k_means_constrained import KMeansConstrained

try:  # Si depuis Web
    from optimisation.utils import main_bulles, get_depot, getTimeMatrix, truck, two_opt, get_time
    from optimisation.data.constante_config import *
except ImportError:  # Si depuis code
    from utils import main_bulles, get_depot, getTimeMatrix, truck, two_opt, get_time
    from data.constante_config import *




# fonction de calcul de poids par cluster (apd objet cluster)
def get_weight_from_cluster(cluster):
    return sum([bulle.poids for bulle in cluster])


# fonction de calcul de poids pour tous les clusters
def get_weight_all_clusters(clusters):
    clusters_weights = []
    for cluster in clusters:
        clusters_weights.append(get_weight_from_cluster(cluster))

    return clusters_weights




# fonction permettant de trier une liste de bulles (prend dict_bulles en entrée)
def sort_bulles(dict_bulles):
    # tri des bulles selon les poids de façon décroissante -> liste de bulles
    bulles = sorted(dict_bulles.values(), key=lambda bulle: bulle.poids, reverse=True)
    bulles = [bulle for bulle in bulles if bulle.Id <= 573]
    return bulles



def clusters(nbre_clusters, bulles, dico_bulles, bulles_urgentes):
    """
    :param nbre_clusters: nombre de cluster à créer (from how_many_clusters(trucks))
    :type nbre_clusters: int
    :param bulles: bulles sélectionnées pour la simulation
    :type bulles: dataframe
    :param dico_bulles: toutes les bulles
    :type dico_bulles: dict [id_bulle] = objet_bulle
    :param bulles_urgentes: bulles contenant les bulles urgentes de la semaines qui vont déborder
    :type bulles_urgentes: list
    :return: les clusters de bulles et leurs centroid (centre géographique du cluster)
    :rtype: list, ndarray
    """
    bulles_ = bulles.copy()
    if nbre_clusters > 1:
        # on définit les tailles min et max des clusters en fonction du nombre de bulles à prendre et du nombre de clusters
        cluster_size_min = int(len(bulles) / nbre_clusters) - 1
        cluster_size_max = int(len(bulles) / nbre_clusters) + 1
        # modèle de clustering où l'on contraint le nombre de bulles par clusters entre 2 bornes
        constrained_model = KMeansConstrained(
            n_clusters=nbre_clusters,
            size_min=cluster_size_min,
            size_max=cluster_size_max,
            random_state=0)
        # Compute cluster centers and predict cluster index for each sample.
        bulles['cluster'] = constrained_model.fit_predict(
            bulles_[["Latitude", "Longitude"]])
        '''
        mise des bulles urgentes débordante dans le même cluster afin que celui-ci soit ramassé le premier jour de la simulation
        '''
        try:
            which_cluster = []
            for bulle in bulles_urgentes:
                id = bulles.loc[bulles['bin_index'] == bulle.Id]
                which_cluster.append(int(id["cluster"]))
            if which_cluster.count(which_cluster[0]) != len(which_cluster):
                for bulle in bulles_urgentes:
                    id_row = bulles.index[bulles['bin_index'] == bulle.Id].tolist()[0]
                    bulles.at[id_row, 'cluster'] = which_cluster[0]
        except IndexError:  # veut dire qu'aucune bulle n'est urgente débordante
            pass

        centroids = constrained_model.cluster_centers_

    else:  # le cluster contient toutes les bulles (création d'un seul cluster)
        bulles['cluster'] = 0
        x = [bulles_['Latitude'][i] for i in bulles_.index]  # x = la latitude des bulles
        y = [bulles_['Longitude'][i] for i in bulles_.index]
        centroids = (sum(x) / len(bulles_), sum(y) / len(bulles_))  # centre du cluster = moyenne des coordonnées x et y

    clusters = []
    for i in range(nbre_clusters):  # ajout des clusters dans un dict
        key_list = bulles["bin_index"][bulles["cluster"] == i]
        clusters.append([dico_bulles[i] for i in key_list if i in dico_bulles])

    return clusters, centroids


# fonction qui calcule le remplissage total des bulles sur 1 semaine sur base de leurs vitesses de remplissage
def compute_weekly_weight_coverage(dico_bulles, daystosimulate=7):
    """
    Fonction qui retourne le poids à ramasser au bout de daystosimulate jours
    :param dico_bulles: dictionnaire de bulles, [id_bulles] = objet_bulle
    :type dico_bulles: dict
    :param daystosimulate: Nombre de jours à simuler
    :type daystosimulate: int
    :return: poids total à ramasser dans n jours
    :rtype: int
    """
    bulles = dico_bulles.values()
    predicted_coverage = 0

    for b in bulles:
        predicted_coverage += b.vit_remplissageb * daystosimulate
        predicted_coverage += b.vit_remplissagec * daystosimulate

    return predicted_coverage

def select_bulles(dico_bulles, weekly_weight_coverage, max_cluster_size, nbre_clusters, remplissage_limite,total_capacity,sum_weigth,days = 7):
    """
    sélection de bulles pour la semaine en fonction de la masse totale à couvrir en 1 semaine
    :param dico_bulles: dictionnaire de bulles, [id_bulles] = objet_bulle
    :type dico_bulles: dict
    :param weekly_weight_coverage: Fonction qui retourne le poids à ramasser sur la semaine
    :type: int
    :param max_cluster_size: pour l'instant c'est 18 mais à revoir #FIXME
    :type: int
    :param nbre_clusters: nombre de cluster créé pour la semaine en cours
    :type: int
    :param remplissage_limite: paramètre utilisateur, pourcentage de la capacité max au dela duquel la bulle est considéré comme remplie (ex : 0.6 * capacité max bulle)
    :type: int (entre 0 et 1)
    :param: daystosimulate
    :returns: dataframe avec les bulles sélectionnées pour la simulation
    :rtype: dataframe
    """
# sélection de bulles pour la semaine 

    # tri des bulles selon les poids de façon décroissante -> liste de bulles
    bulles = sorted(dico_bulles.values(), key=lambda bulle: bulle.poids_week[-1], reverse=True)  # tri selon le poids qu'auront les bulles en fin de semaine
    temp = [bulle for bulle in bulles if bulle.is_emergency == True]  # list des bulles urgentes
    # On considére que les bulles urgentes sont remplies au max, donc on mets leur poids_week = au poids max
    for bulleUrgentes in temp :
        bulleUrgentes.poids_week = [bulleUrgentes.poids_utile]*len(bulleUrgentes.poids_week)

    #temp = sorted(temp, key=lambda bulle: bulle.poids_week[-1], reverse=False)  # reverse = false car dans la boucle en dessous j'ajoute en premier les element les plus petit de temp
    bullesaprendre = [] #added
    for bulle in temp:
        if bulle in bulles:
            #bulles.remove(bulle)
            #bulles.insert(0, bulle)
            if bulle not in bullesaprendre: #added
              bullesaprendre.append(bulle)#added

    nbre_bulles = 0
    # recherche nombre de bulles urgentes 
    for id, bulle in dico_bulles.items():
        #Recherche des bulles à vider dans la semaine
            
        if bulle.poids_week[-1] >= remplissage_limite * bulle.poids_utile:
            if bulle not in bullesaprendre: #added
              bullesaprendre.append(bulle)#added
              nbre_bulles += 1
    #print(f"Nombre de bulles urgente qui doivent être récoltées : {nbre_bulles}")
    urg=nbre_bulles
    
    " ajout de bulles non urgentes si pas rempli  "
    it=0
    #print("coverage",weekly_weight_coverage)
    #print("capacité",total_capacity)
    #print(bulles[nbre_bulles+it].poids_week[-1]>0.5*remplissage_limite*1500)
    while (sum_weigth < total_capacity) and (nbre_bulles+it < len(bulles)) and (bulles[nbre_bulles+it].poids_week[days]> TAUX_LIMIT *remplissage_limite*bulles[nbre_bulles+it].poids_utile):
     if(sum_weigth+bulles[nbre_bulles+it].poids_week[days]<total_capacity) and (bulles[nbre_bulles+it] not in bullesaprendre) :#dernier and added
         nbre_bulles+=1
         sum_weigth+=bulles[nbre_bulles+it].poids_week[days]
         bullesaprendre.append(bulles[nbre_bulles+it]) #added
         #print("bulles rajoutées non urgentes ",bulles[nbre_bulles+it].Id)
     else: 
         it=it+1
    logging.info(f"Nombre de bulles totale qui peuvent être récoltées : {nbre_bulles}")    
    
    # construction d'un dataframe pour le clustering (plus pratique)
    df = pd.DataFrame()
    df["Latitude"] = [bulle.latitude for bulle in bullesaprendre]
    df["Longitude"] = [bulle.longitude for bulle in bullesaprendre]
    df["bin_index"] = [bulle.Id for bulle in bullesaprendre]
    df["demand"] = [bulle.poids_week[days // 2] for bulle in bullesaprendre]
    df["demand_b"] = [bulle.poidsb_week[days // 2] for bulle in bullesaprendre]
    df["demand_c"] = [bulle.poidsc_week[days // 2] for bulle in bullesaprendre]
    df["limit_delta"] = [bulle.limit_delta for bulle in bullesaprendre]
    
   

    bulles_prises = df[:nbre_bulles]
    bulles_non_prises=df[nbre_bulles:]

    # temp = list de bulles urgentes
    return bulles_prises, bulles_non_prises,urg, temp


def how_many_clusters(trucks):
    """
    Retourne le nombre de cluster à créer pour la semaine
    :param trucks: list d'objets camions
    :type: list
    :return: nombre de cluster de la semaine
    :rtype: int
    """
    nbre_clusters = 0
    for t in trucks:
        # camion 26t : +1 cluster
        if t.is26T:
            nbre_clusters += 1
        # camion 44t : +2 clusters
        else:
            nbre_clusters += 2
    return nbre_clusters


def cluster_to_route(clusters, time_matrix, depots):
    """
    fonction qui prend en paramètre la liste des clusters et applique le 2-opt sur chaque cluster
    :param clusters: list de cluster, chaque cluster contient les bulles qui y sont associées
    :type clusters: list
    :param time_matrix: list contenant le temps entre chaque bulles
    :type time_matrix: list contenant le temps entre chaque bulles
    :param depots: list d'objets instancié comme une bulle, tous les dépots associé à une tournée
    :type depots: list
    :return: les clusters, ordre du trajet = ordre des bulles dans chaque cluster
    :rtype: list
    """
    for i in range(len(clusters)):
        clusters[i] = two_opt([depots[0]] + clusters[i] + depots[1:], time_matrix)  # pour l'ordre de la route : depots de départ, cluster, dépot d'arrivée. Dans le cas dottignies, départ et arrivée sont les même
        for depot in depots:
            clusters[i].pop(clusters[i].index(depot))
    return clusters



def sort_clusters_dist_depot(depot, clusters, centroids):
    """
    fonction qui trie les clusters en fonction de leur distance par rapport au dépot
    :param depot: objet instancié comme une bulle
    :type depot: objet_bulle
    :param clusters: liste contenants les clusters
    :type clusters: list
    :param centroids: list des centroid de
    :type centroids: coordonnées x et y (latitude et longitude) du centres des clusters
    :return: liste de tuple (centroid, cluster) triés par rapport à leur distance du dépôt
    :rtype: list
    """
    coords_depot = [depot.latitude, depot.longitude]
    cluster_to_centroid = []
    if len(clusters) == 1:  # si 1 seul cluster
        cluster_to_centroid.append([centroids, clusters])
        sorted_clusters = sorted(cluster_to_centroid,
                                 key=lambda x: (x[0][0] - coords_depot[0]) ** 2 + (x[0][1] - coords_depot[1]) ** 2,
                                 reverse=True)
    else:
        for i in range(len(clusters)):
            cluster_to_centroid.append([centroids[i], clusters[i]])
        sorted_clusters = sorted(cluster_to_centroid,
                                 key=lambda x: (x[0][0] - coords_depot[0]) ** 2 + (x[0][1] - coords_depot[1]) ** 2,
                                 reverse=True)
    return sorted_clusters


def assign_44T(truck, cluster, sorted_clusters, depots, time_mat):
    """
    dans le cas 44T, on assigne 2 clusters au camions. Donc on assigne comme trajet le cluster le plus proche du
    dépot (cluster 1) + le cluster le plus proche du cluster 1
    :param truck: objet_camion
    :type truck: objet_camion
    :param cluster: le cluster le plus proche du dépot
    :type cluster: tuple
    :param sorted_clusters: list de tuple (centroid, cluster) triés par rapport à leur distance du dépôt
    :type sorted_clusters: list
    :param depots: list d'objets instancié comme une bulle, tous les dépots associé à une tournée
    :type depots: list
    :return: le trajet du 44T, cluster le plus proche du dépot, cluster le plus proche du cluster 1
    :rtype: objet_camion, tuple, list
    """
    coords_cluster = cluster[0]  # centroid du cluster le plus proche du dépot
    # pour trouver le cluster le plus proche, on trie les sorted clusters par rapport à leur distance au cluster
    # auquel on veut l'associer et on prend le second élément, le premier étant le cluster en lui-même
    closest_cluster = sorted(sorted_clusters, key=lambda x: (x[0][0] - coords_cluster[0]) ** 2 + (x[0][1] - coords_cluster[1]) ** 2)[1]  # cherche l'hypothénuse la plus petite entre coords_cluster et tous les clusters
    truck.route = two_opt([depots[0]] + closest_cluster[1] + cluster[1] + depots[1:], time_mat)
    return truck, cluster, closest_cluster


def multi_container_44T(trucks, time_matrix, depots):
    """
    fonction qui trouve le dépot fictif pour les 44 Tonnes et leur attribue une route post 2-opt
    :param trucks:
    :type trucks:
    :param time_matrix:
    :type time_matrix:
    :param TAUX_REMPLISSAGE_CAMION:
    :type TAUX_REMPLISSAGE_CAMION:
    :return: Truck.route pour les 44T
    :rtype:
    """
    for t in trucks:
        if not t.is26T:  # check si 44T
            bestdist = float('inf')
            for elem in t.route[1] + t.route[2]:
                dist = 0
                for elem2 in t.route[1] + t.route[2]:
                    if elem != elem2:
                        dist += time_matrix[elem.id_site][elem2.id_site] ** 2
                if dist <= bestdist:
                    bestbulle = elem
                    bestdist = dist

            if bestbulle in t.route[1]:
                t.route[1].pop(t.route[1].index(bestbulle))
            if bestbulle in t.route[2]:
                t.route[2].pop(t.route[2].index(bestbulle))

            t.route = [depots[0],
                       two_opt([bestbulle] + t.route[1] + [bestbulle], time_matrix),
                       two_opt([bestbulle] + t.route[2] + [bestbulle], time_matrix)] \
                      + depots[1:]
    return trucks


def assign_clusters(sorted_clusters, trucks, depots, time_mat):
    """
    fonction qui attribue les clusters à chaque camion
    :param sorted_clusters: liste de tuple (centroid, cluster) triés par rapport à leur distance du dépôt
    :type sorted_clusters: list
    :param trucks: list d'objets camions
    :type trucks: list
    :param depots: list d'objets instancié comme une bulle, tous les dépots associé à une tournée
    :type depots: list
    :return: list trucks avec leur trajet à effectuer (truck.route),
    :rtype:
    """

    # on trie les trucks pour mettre les plus lourds au début (donc d'abord les 44T)
    trucks = sorted(trucks, key=lambda x: x.capacity[0], reverse=True)
    for i in range(len(trucks)):
        if trucks[i].is26T:
            # sorted_clusters[0][1][0] indique la première bulle du premier cluster trié
            if isinstance(sorted_clusters[0][1][0], list):
                sorted_clusters[0][1] = sorted_clusters[0][1][0]

            trucks[i].route = [depots[0]] + sorted_clusters[0][1] + depots[1:]
            del sorted_clusters[0]  # suppression du cluster qui vient d'être assigné

        else:
            # dans le cas 44T, on assigne 2 clusters au camion
            trucks[i], c1, c2 = assign_44T(trucks[i], sorted_clusters[0], sorted_clusters, depots, time_mat)
            for i in range(len(sorted_clusters)):
                if c2[1] == sorted_clusters[i][1]:
                    indice_closest_cluster = i

            to_delete = [sorted_clusters.index(c1), indice_closest_cluster]
            to_delete = sorted(to_delete, reverse=True)

            for indice in to_delete:
                del sorted_clusters[indice]
    return trucks, sorted_clusters



def compute_weights_week(dict_bulles, nbjours=7):
    """
        fonction qui calcule les poids sur tous les jours de la semaine pour toutes les bulles de dict_bulles
        :param dico_bulles: dictionnaire de bulles, [id_bulles] = objet_bulle
        :type dico_bulles: dict
        :param nbjours: int nombre de jousr à calculer
        :type nbjours: int

        :return: dico_bulles: dico avec le poids de la semaine calculé
        :rtype:dict
        """

    for i in dict_bulles.keys():
        dict_bulles[i].poidsb_week = []
        dict_bulles[i].poidsc_week = []
        dict_bulles[i].poids_week = []
            
        for day in range(nbjours):
            dict_bulles[i].poidsb_week.append(min(dict_bulles[i].poids_utile,dict_bulles[i].poidsb + dict_bulles[i].vit_remplissageb * (day)))
            dict_bulles[i].poidsc_week.append(min(dict_bulles[i].poids_utile,dict_bulles[i].poidsc + dict_bulles[i].vit_remplissagec * (day)))
            dict_bulles[i].poids_week.append(min(dict_bulles[i].poids_utile,dict_bulles[i].poidsb_week[day] + dict_bulles[i].poidsc_week[day]))


    return dict_bulles