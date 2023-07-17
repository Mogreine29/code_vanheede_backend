#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                            Clustering
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# fonction qui appelle la formation des clusters
def initiate_clusters(depot_id, nbre_camions, initial_bulles_par_jour, max_limit_delta, nbre_jours, target_mean_weight,
                      max_weight_per_cluster, dict_bulles):
    # récupération des données des bulles
    dict_bulles = dict_bulles

    # tri des bulles selon les poids de façon décroissante -> liste de bulles
    bulles = sorted(dict_bulles.values(), key=lambda bulle: bulle.poids, reverse=True)

    # construction d'un dataframe pour le clustering (plus pratique)
    df = pd.DataFrame(columns=["Latitude", "Longitude", "bin_index", "demand", "limit_delta", "cluster"])
    df["Latitude"] = [bulle.latitude for bulle in bulles]
    df["Longitude"] = [bulle.longitude for bulle in bulles]
    df["bin_index"] = [bulle.Id for bulle in bulles]
    df["demand"] = [bulle.poids for bulle in bulles]
    df["limit_delta"] = [bulle.limit_delta for bulle in bulles]

    # définition de paramètres pour le nombre de bulles à prendre en compte et la simulation
    bulles_par_jour = initial_bulles_par_jour
    bulles_par_semaine = nbre_jours * bulles_par_jour
    # nbre_camions       = 2
    nbre_clusters = nbre_camions * 5

    # sélection des bulles absolument prioritaires (date limite dans la semaine)
    bulles_prio = df[df["limit_delta"] <= max_limit_delta]

    # si on a pas assez de bulles prio pour un bon clustering, on prend des bulles supplémentaires
    if len(bulles_prio) < bulles_par_semaine:
        bulles_week = df.head(bulles_par_semaine)
    else:
        bulles_week = bulles_prio

    # on crée des clusters avec de plus en plus de bulles tant que le moyenne des poids des clusters n'est pas supérieure à un seuil
    clusters_mean_weight = 0
    i = 0
    while clusters_mean_weight < target_mean_weight:
        bulles_par_jour += 2
        bulles_par_semaine = nbre_jours * bulles_par_jour
        bulles_week = df.head(bulles_par_semaine)

        # clusterisation sur toutes les bulles de la semaine, 1 seule clusterisation
        model = cluster.KMeans(n_clusters=nbre_clusters, init='k-means++')
        bulles_week_ = bulles_week.copy()
        bulles_week['cluster'] = model.fit_predict(bulles_week_[["Latitude", "Longitude"]])
        # plotCluster(bulles_week, "cluster_week.html")

        # calcul des poids par clusters
        cluster_weights = []
        for i in range(nbre_clusters):
            cluster_weights.append(get_total_weight_from_cluster(bulles_week, i))
        clusters_mean_weight = sum(cluster_weights) / len(cluster_weights)

        # filtration des clusters : on retire les bulles ayant le limit_delta le plus élevé pour les clusters dépassant un seuil de poids
        for i in range(nbre_clusters):
            while cluster_weights[i] > max_weight_per_cluster:
                cluster_i = bulles_week[bulles_week["cluster"] == i]
                cluster_i = cluster_i[cluster_i["limit_delta"] < cluster_i["limit_delta"].max()]
                bulles_week = pd.concat([bulles_week[bulles_week["cluster"] != i], cluster_i])
                cluster_weights[i] = get_total_weight_from_cluster(bulles_week, i)

        # for i in range(nbre_clusters):
        #     cluster_weights.append(get_total_weight_from_cluster(bulles_week, i))
        # clusters_mean_weight = sum(cluster_weights)/len(cluster_weights)
        i += 1

    # création d'une liste de liste de bulles correspondant aux clusters
    final_clusters = []
    for i in range(nbre_clusters):
        key_list = bulles_week["bin_index"][bulles_week["cluster"] == i]
        final_clusters.append([dict_bulles[i] for i in key_list if i in dict_bulles])
    final_clusters = sort_cluster_by_weight(final_clusters)
    return final_clusters



def launchClustering(id_depot):
    depot_id = id_depot
    target_weight_per_cluster = 4000
    max_limit_delta = 7
    dict_bulles = main_bulles(depot_id)
    time_matrix = getTimeMatrix()
    depot = get_depot(depot_id)

    trucks = [
        truck("dottignies", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_44T_CAPACITE_EN_KG / 2, CAMION_44T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_44T_CAPACITE_EN_KG / 2, CAMION_44T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_44T_CAPACITE_EN_KG / 2, CAMION_44T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_44T_CAPACITE_EN_KG / 2, CAMION_44T_CAPACITE_EN_KG / 2]),
        truck("dottignies", [CAMION_44T_CAPACITE_EN_KG / 2, CAMION_44T_CAPACITE_EN_KG / 2])
    ]

    # trucks = [
    #     truck("quévy", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2]),
    #     truck("quévy", [CAMION_26T_CAPACITE_EN_KG / 2, CAMION_26T_CAPACITE_EN_KG / 2])
    #     ]

    '''A COMMENTER DANS LE CAS REEL'''
    # on tronque les données pour pas avoir trop de bulles (bulles surchargées puisque la bdd est pas mise à jour)
    for i in dict_bulles.keys():
        dict_bulles[i].poids -= 700
        dict_bulles[i].poidsb -= 350
        dict_bulles[i].poidsc -= 350
        dict_bulles[i].limit_delta += 6

    nbre_clusters = how_many_clusters(trucks)

    clusters, centroids = clustering(nbre_clusters, target_weight_per_cluster, dict_bulles, max_limit_delta)

    clusters = cluster_to_route(clusters, time_matrix, depot, minerales)

    sorted_clusters = sort_clusters_dist_depot(depot, clusters, centroids)

    trucks, b = assign_clusters(sorted_clusters, trucks, depot)

    trucks = multi_container_44T(trucks, time_matrix)

    # on fait des permutations entre les camions avant de les plots
    # trucks = permutations(trucks, time_matrix, 9*60*60)

    # plotMap(trucks, dict_bulles, depot, "test.html")

    clusters_time = get_time_all_clusters(clusters, time_matrix)
    cluster_weights = get_weight_all_clusters(clusters)
    return trucks



# fonction du clustering 2.0 on ajuste le nombre de bulles ppour atteindre un poids moyen par cluster
def clustering(nbre_clusters, target_weight, dict_bulles, max_limit_delta):
    nbre_bulles = 0
    # tri des bulles selon les poids de façon décroissante -> liste de bulles
    bulles = sorted(dict_bulles.values(), key=lambda bulle: bulle.poids, reverse=True)

    # construction d'un dataframe pour le clustering (plus pratique)
    df = pd.DataFrame(columns=["Latitude", "Longitude", "bin_index", "demand", "limit_delta", "cluster"])
    df["Latitude"] = [bulle.latitude for bulle in bulles]
    df["Longitude"] = [bulle.longitude for bulle in bulles]
    df["bin_index"] = [bulle.Id for bulle in bulles]
    df["demand"] = [bulle.poids for bulle in bulles]
    df["demand_b"] = [bulle.poidsb for bulle in bulles]
    df["demand_c"] = [bulle.poidsc for bulle in bulles]
    df["limit_delta"] = [bulle.limit_delta for bulle in bulles]

    # sélection des bulles absolument prioritaires (date limite dans la semaine)
    bulles_clusters = df[df["limit_delta"] <= max_limit_delta]
    nbre_bulles = len(bulles_clusters)

    # ajustement du nombre de bulles si trop grand ou trop petit
    while sum(bulles_clusters["demand"]) > nbre_clusters * target_weight + 1000:
        nbre_bulles -= 1
        bulles_clusters = bulles_clusters[:nbre_bulles]

    while sum(bulles_clusters["demand"]) < nbre_clusters * target_weight - 1000:
        nbre_bulles += 1
        bulles_clusters = bulles_clusters[:nbre_bulles]

    # # clustering sur toutes les bulles de la semaine, 1 seule clusterisation
    # model                      = cluster.KMeans(n_clusters = nbre_clusters, init = 'k-means++')
    # bulles_clusters_           = bulles_clusters.copy()
    # bulles_clusters['cluster'] = model.fit_predict(bulles_clusters_[["Latitude", "Longitude"]])
    # #print(model.inertia_)

    # modèle de clustering où l'on contraint le nombre de bulles par clusters entre 2 bornes
    constrained_model = KMeansConstrained(
        n_clusters=nbre_clusters,
        size_min=8,
        size_max=11,
        random_state=0)
    bulles_clusters_ = bulles_clusters.copy()
    bulles_clusters['cluster'] = constrained_model.fit_predict(bulles_clusters_[["Latitude", "Longitude"]])
    # plotCluster(bulles_clusters, "cluster_week_constrained.html")

    clusters = []
    for i in range(nbre_clusters):
        key_list = bulles_clusters["bin_index"][bulles_clusters["cluster"] == i]
        clusters.append([dict_bulles[i] for i in key_list if i in dict_bulles])

    # calcul des poids par clusters
    cluster_weights = get_weight_all_clusters(clusters)

    # plotCluster(bulles_clusters, "cluster_week.html")
    return clusters, constrained_model.cluster_centers_

# fonction qui calcule le temps pour parcourir tout le cluster
def get_total_time_from_cluster(cluster, time_matrix):
    return get_time(time_matrix, cluster)


# fonction qui calcule le temps de tous les clusters
def get_time_all_clusters(clusters, time_matrix):
    clusters_time = []
    for cluster in clusters:
        clusters_time.append(get_total_time_from_cluster(cluster, time_matrix))

    return clusters_time


def permutations(trucks, time_mat, max_time):
    for t1 in trucks:
        if len(t1.route) == 4:
            to_compare = t1.route[1] + t1.route[2]
        else:
            to_compare = t1.route[1:-1]
        # pour chaque élément de la route à comparer on la compare à chaque camion
        # on ajoute dedans si la somme des temps de trajets est inférieure
        best = 10000000000000000000
        improved = False
        for elem in to_compare:
            for t2 in trucks:
                if len(t2.route) == 4:
                    to_be_compared = t2.route[1] + t2.route[2]
                else:
                    to_be_compared = t2.route[1:-1]
                if t1 != t2:
                    best = 0
                    temp1 = to_compare
                    temp2 = to_be_compared
                    for i in range(len(to_be_compared)):
                        temp2 = to_be_compared
                        temp1 = to_compare
                        temp2.insert(i, elem)
                        temp1.pop(temp1.index(elem))
                        if get_time(time_mat, temp2) + get_time(time_mat, temp1) < best and get_time(time_mat,
                                                                                                     temp2) < max_time and get_time(
                            time_mat, temp1) < max_time:
                            best = get_time(time_mat, temp2) + get_time(time_mat, temp1)

def sort_cluster_by_weight(clusters):
    def sortRow(cluster):
        return sum([bulle.poids for bulle in cluster])

    clusters.sort(key=sortRow, reverse=True)
    return clusters

# fonction de calcul de poids par cluster (apd dataframe)
def get_total_weight_from_cluster(coords, cluster):
    return sum(coords[coords["cluster"] == cluster]["demand"])


#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                UTILS
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


"""
Class Bcolors
"""


class bcolors:  # Utilisée pour #print console colorés
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def main_depot():
    depots = get_depot()
    dict_depots = {}
    for elem in depots:
        dict_depots[elem.Id] = elem
    return dict_depots

def cost_change(time_mat, n1, n2, n3, n4):
    return time_mat[n1][n3] + time_mat[n2][n4] - time_mat[n1][n2] - time_mat[n3][n4]


def bulles_prises(Solution=[]):
    bulles_prises = []
    for liste_trucks in Solution:
        for truck in liste_trucks:
            depot = truck.depot
            if truck.is26T:
                for bulle in truck.route:
                    bulles_prises.append(bulle.Id)
            else:
                road = list(set(truck.route[1] + truck.route[2]))
                for bulle in road:
                    bulles_prises.append(bulle.Id)
    bulles_prises = list(set(bulles_prises))
    if depot == 'Dottignies':
        nombre_bulles = 495
    else:
        nombre_bulles = 95
    # #print(bcolors.UNDERLINE+ f"MONITORING: Pourcentage de bulles récupérées  = {(len(bulles_prises)/nombre_bulles)*100}%." + bcolors.ENDC)



#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                                                Main
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------