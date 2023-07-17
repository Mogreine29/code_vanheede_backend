import datetime
from datetime import datetime as dt  # Laiser les deux!!!
import json
import logging
import copy
import pandas as pd


try:  # import depuis serveur
    from optimisation import clustering
    from optimisation.utils import main_bulles, get_depot, getTimeMatrix, truck, update_dict_weekly, day_assignment, \
         monitoring, remplissage_moyen, spikes_remplissage, multiroute, prevision_days, separation_route_en_plusieurs,tri_solution
    from optimisation.data.constante_config import *

except ImportError:  # import pour le main de la partie opti
    import clustering
    from utils import main_bulles, get_depot, getTimeMatrix, truck, update_dict_weekly, day_assignment, monitoring, remplissage_moyen, spikes_remplissage, multiroute, prevision_days,separation_route_en_plusieurs,tri_solution
    from data.constante_config import *




def main(parametre):
    # Initialise logging
    # log_filename = f"simulation_{datetime.datetime.now():%Y-%m-%d_%H-%M-%S}.log"
    # logging.basicConfig(format='%(asctime)s %(message)s', filename=log_filename, level=logging.INFO)

    Solution = []
    """
    Lecture des paramètres dans le fichier json
    passé en paramètre
    """
    logging.info('Import des paramètres')
    Depot_id = []
    Depot_Nom = parametre['Depot']  # le dépot de départ
    Depot_arrivee = parametre['Vidange']
    Depot_id.append(MAP_DEPOT_NAME_TO_DEPOT_ID[Depot_Nom])
    Depot_id.append(MAP_DEPOT_NAME_TO_DEPOT_ID[Depot_arrivee])
    if Depot_arrivee == "Minérale" or Depot_arrivee == "Renaix": # si le dépot c'est minéral ou renaix, il faut tout de même retourner à au dépot initial
        Depot_id.append(MAP_DEPOT_NAME_TO_DEPOT_ID[Depot_Nom])
    Max_time = parametre['Max time']
    numberOfWeeks = parametre['Number of weeks']
    numberOfSmallTrucks = parametre['26 Tonnes']
    numberOfBigTrucks = parametre['44 Tonnes']
    numberOfDays = parametre['Number of days']
    TAUX_REMPLISSAGE_CAMION = parametre['Remplissage limite camions']
    MODE_AUTO=False # le mode auto permet de respecter les contraintes de temps sans respecter le taux de remplissage
    if TAUX_REMPLISSAGE_CAMION=="auto":
        MODE_AUTO=True
        TAUX_REMPLISSAGE_CAMION=0.9
    else:
        TAUX_REMPLISSAGE_CAMION=float(TAUX_REMPLISSAGE_CAMION)
    TAUX_REMPLISSAGE_BULLE = parametre['Remplissage limite']

    urgent_bins = parametre['urgent_bins']  # id des potentielles bulles urgentes

    date_debut = parametre['date_debut']
    if date_debut != "":
        date_debut = dt.strptime(date_debut, '%Y-%m-%d').date()
        if date_debut.weekday() == 5:
            date_debut += datetime.timedelta(
                2)  # si date de debut est samedi, on commence la simulation a partir de lundi
        elif date_debut.weekday() == 6:
            date_debut += datetime.timedelta(1)


    logging.info('Paramètres importés')
    ##print('-------------------TEST AFFICHAGE-------------------------')

    """
    Formatage des paramètres
    """
    bulles_debordent = []
    Dict_Bulles = main_bulles(Depot_id[0], date_debut, TAUX_REMPLISSAGE_BULLE)  # extrait ensemble des bulles du depot correspondant, Depot_id[0] = id de la tournée
    Depots = []
    for id in Depot_id:
        dep, _ = get_depot(id)
        Depots.append(dep)  # récupére infos du depot (soit quévy soit dottignies)
    Time_Matrix = getTimeMatrix(Depots)

    '''sélection des bulles urgentes indiqué par l'utilisateur (celle dans le parametres.json)'''
    if not isinstance(urgent_bins, list):
        urgent_bins = [urgent_bins]
    if urgent_bins != None:
        temp = []
        for bin in urgent_bins:
            Dict_Bulles[bin].poids = Dict_Bulles[bin].poids_utile
            Dict_Bulles[bin].is_emergency = 1
            if Dict_Bulles[bin].type_bulle=="Double":
                Dict_Bulles[bin].poidsb=Dict_Bulles[bin].poids/2
                Dict_Bulles[bin].poidsc = Dict_Bulles[bin].poids / 2
            elif Dict_Bulles[bin].couleur=="White" :
                Dict_Bulles[bin].poidsb = Dict_Bulles[bin].poids
                Dict_Bulles[bin].poidsc = 0
            else :
                Dict_Bulles[bin].poidsc = Dict_Bulles[bin].poids
                Dict_Bulles[bin].poidsb = 0





    # urgent_bins = liste d'objets bulles qui sont les bulles urgentes à vider.
    # si cette liste est vide si il n'y a aucune bulle urgente à vider

    '''détermination des bulles qui seront urgentes (calcul poids de chaque bulles jusqu'au premier dimanche après le jour de lancement de la simulation)'''
    if date_debut.weekday() > 0 and date_debut.weekday() < 5:  # Si on relance en cours de semaine
        Sunday = date_debut + datetime.timedelta((6 - date_debut.weekday()) % 7)
        days = (Sunday - date_debut).days
        Dict_Bulles = clustering.compute_weights_week(Dict_Bulles,days)  # Calcule le poids qu'auront les bulles pour les x (diff entre ajd et dimanche) prochains jours
    else:
        Dict_Bulles = clustering.compute_weights_week(Dict_Bulles)  # Calcule le poids qu'auront les bulles pour les 7 prochains jours
        days = 7
    max_cluster_size = 18  # FIXME: PQ 18

    
    logging.info("Formatage des paramètres terminé")

    total_simulation_time = 0
    for week in range(numberOfWeeks):
        print(f"Début de la simulation pour la semaine {week}.")
        logging.info(f"Début de la simulation pour la semaine {week + 1}.")
        # Si on relance la simulation en semaine, il faut connaître le nombre de jour restant à simuler pour cette semaine
        days = numberOfDays
        daystosunday = 7
        if week == 0:
            if date_debut.weekday() > 0 and date_debut.weekday() < 5:  # Si on relance en cours de semaine
                # Compte que les weekday, pas samedi et dimanche
                friday = date_debut + datetime.timedelta((4 - date_debut.weekday()) % 7)  # ATTENTION : compte le nombre de jour entre la date donnée et leprochain vdd A PARTIR DE AJD, donc si date dans le passé faire gaffe
                days = (friday - date_debut).days
                daystosunday = days + 2  # nombre de jours avant prochain dimanche
            if days > numberOfDays:
                days = numberOfDays  # si on est lundi mais qu'on a prévu que deux jours de simulations, on va simuler qmm que sur deux jours. si on est jeudi, que sur 1

        """
        Création des camions pour la semaine
        """

        total_capacity = 0
        Trucks = []
        id_truck = 0
        for day in range(days):
            for i in range(numberOfSmallTrucks):
                Trucks.append(truck(Depot_Nom, [TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG / 2,
                                                TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG / 2],
                                    id_truck, is26T=True))  # 2 fois le même calcul car ils font moitié ben pour le verre blanc et l'autre pour celui de couleur
                total_capacity += TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG
                id_truck += 1

        for day in range(days):
            for i in range(numberOfBigTrucks):
                Trucks.append(truck(Depot_Nom, [TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG / 2,
                                                TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG / 2], id_truck, is26T=False))
                total_capacity += TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG
                id_truck += 1

        #print("Nombre de jours de simulation : ", days)

        """
        Tant que les camions actuels ne permettent pas de couvrir le poids à récupérer on upgrade les camions.
        """

        milieusemaine = days // 2

        weights_to_take = [bullesRempliesFinSemaine.poids_week[milieusemaine] for b_id, bullesRempliesFinSemaine in Dict_Bulles.items() if bullesRempliesFinSemaine.poids_week[-1] > TAUX_REMPLISSAGE_BULLE * bullesRempliesFinSemaine.poids_utile]
        sum_weights_to_take = sum(weights_to_take)

        #print("la somme pour la semaine",sum_weights_to_take)



        if total_capacity < sum_weights_to_take:  # Si le poids total à aller récupérer est plus grand que la capacité des camions
            while total_capacity < sum_weights_to_take:
                if days < 2*(5 - date_debut.weekday()) and((not MODE_AUTO) or days<2*numberOfDays):
                   nb_small=0;
                   nb_big=0;
                   days += 1
                   while total_capacity < sum_weights_to_take and (nb_small<numberOfSmallTrucks or nb_big<numberOfBigTrucks): # on ajoute le nombre de camions max par jour si besoin
                        if numberOfBigTrucks > 0 and nb_big < numberOfBigTrucks:  # Si on travaille avec des 44 Tonnes
                            nb_big += 1
                            id_truck += 1
                            Trucks.append(truck(Depot_Nom, [TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG / 2,
                                                            TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG / 2],
                                                id_truck, is26T=False))
                            total_capacity += TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG

                            logging.info("Capacité des camions insuffisante : Un camion de 44 Tonnes est ajouté.")
                        if numberOfSmallTrucks > 0 and nb_small<numberOfSmallTrucks :  # Si on travaille avec des 26 Tonnes
                            nb_small+=1
                            id_truck += 1
                            Trucks.append(truck(Depot_Nom, [TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG / 2,
                                                        TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG / 2],
                                            id_truck, is26T=True))
                            total_capacity += TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG


                            logging.info("Capacité des camions insuffisante : Un camion de 26 Tonnes est ajouté.")

                else:
                    break

        else :  # Si le poids total à aller récupérer est plus petit que la capacité des camions
                continuer=True
                while sum_weights_to_take < total_capacity and continuer:
                    nb_small = numberOfSmallTrucks;
                    nb_big = numberOfBigTrucks;

                    while total_capacity > sum_weights_to_take and (nb_small > 0 or nb_big > 0):
                        if numberOfSmallTrucks > 0 and nb_small > 0 :
                            if total_capacity - TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG > sum_weights_to_take:
                                nb_small-=1
                                Trucks.pop(0)
                                total_capacity -= TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG

                                logging.info("Capacité des camions trop importante : Un camion de 26 Tonnes est supprimé.")
                            else:
                                continuer = False
                                break
                        if numberOfBigTrucks > 0 and nb_big > 0:
                            if total_capacity - TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG > sum_weights_to_take:
                                nb_big-=1
                                Trucks.pop(0)
                                total_capacity -= TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG

                                logging.info("Capacité des camions trop importante : Un camion de 44 Tonnes est supprimé.")
                            else:
                                continuer = False
                                break

                    if nb_small==0 and nb_big==0 :
                        days-=1
        """
        Clustering
        """

        logging.info(f"Demarage du clustering avec {len(Trucks)} camions.")
        Weekly_weight_coverage = clustering.compute_weekly_weight_coverage(Dict_Bulles, daystosunday)
        nbre_clusters = clustering.how_many_clusters(Trucks)  # CAS 26T: 1 camions = 1 cluster ; l'algo plus haut assigne le nombre de camion désiré par jour
        # donc retourne le nbre de cluster par semaine
        
        bulles, bulles_non_prises,urg, list_bulles_urgentes = clustering.select_bulles(Dict_Bulles, Weekly_weight_coverage, max_cluster_size, nbre_clusters, TAUX_REMPLISSAGE_BULLE,total_capacity,sum_weights_to_take,min(numberOfDays,5-date_debut.weekday()))

        nbr_bulles = len(bulles.index)

        time_tournee  = float('inf')
        bulles_to_keep = bulles
        
        clusters, centroids = clustering.clusters(nbre_clusters, bulles_to_keep, Dict_Bulles, list_bulles_urgentes)
        clusters = clustering.cluster_to_route(clusters, Time_Matrix, Depots)
        sorted_clusters = clustering.sort_clusters_dist_depot(Depots[0], clusters, centroids)
        Trucks, b = clustering.assign_clusters(sorted_clusters, Trucks, Depots, Time_Matrix)

        #plotMap(Trucks, Dict_Bulles, Depots, f"week{week}_{i}.html")
        # Clacul du temps des trajets
        times = []
        for t in Trucks:  # On calcule le temps de trajet de tous les camions
            times.append(t.time_road(Time_Matrix))
        time_tournee = max(
            times)  # On garde le maximum des temps de tournée pour voir si il respecte la contrainte de temps





        while time_tournee > (Max_time + 30*60):
            print(f"------------WARNING : time_tournee > Max_time----------------")
            if time_tournee > Max_time: #Actions mises en place pour fit la contrainte

                        if nbr_bulles >urg : # si encore des bulles non urgentes ( on peut alosr supprimer les non urgentes) :

                            nbr_bulles-=1
                            idx = bulles_to_keep.index.to_list()
                            bulles_to_keep = bulles_to_keep.drop(idx[-1])

                            #print("bulles supprimée")
                           
                           
                        else : #Sinon il faut rajouter un camions 
                            if day < 5 and days < numberOfDays:
                               
                                logging.info('Un 26 Tonne est ajouté à la semaine pour récolter les bulles supprimées')
                                days+=1
                                Trucks.append(truck(Depot_id, [TAUX_REMPLISSAGE_CAMION* CAMION_44T_CAPACITE_EN_KG/ 2,TAUX_REMPLISSAGE_CAMION *CAMION_44T_CAPACITE_EN_KG / 2], id_truck+1,is26T=True))
                                nbre_clusters = clustering.how_many_clusters(Trucks)
                            else:
                                # abandon d'essayer de fit la contrainte de temps
                                time_tournee = 1  # si on ne sait pas satisfaire la contrainte de temps on sors de la boucle
                                break

            clusters, centroids = clustering.clusters(nbre_clusters, bulles_to_keep, Dict_Bulles,list_bulles_urgentes)
            clusters = clustering.cluster_to_route(clusters, Time_Matrix, Depots)
            sorted_clusters = clustering.sort_clusters_dist_depot(Depots[0], clusters, centroids)
            Trucks, b = clustering.assign_clusters(sorted_clusters, Trucks, Depots,Time_Matrix)

            times = []


            for t in Trucks:  # On calcule le temps de trajet de tous les camions
                times.append(t.time_road(Time_Matrix))
            time_tournee = max(times) #On garde le maximum des temps de tournée pour voir si il respecte la contrainte de temps

        logging.info("Fin du clustering")


        


        """
        Affichage du résultat sur la carte
        """
        # plotMap(Trucks, Dict_Bulles, Depots, f"week{week}.html")
        """
        # Regroupement de trajets 
        # """
        Trucks, days = multiroute(Trucks,days, Max_time,Time_Matrix,numberOfSmallTrucks + numberOfBigTrucks)

        print("days_final",days)

        """
        Assignation de jours aux camions
        """
        Trucks, Dict_Bulles = day_assignment(Trucks, Dict_Bulles, days, TAUX_REMPLISSAGE_CAMION, week, date_debut)

        logging.info("Assignation des camions à différents jours")

        """
        Processus d'évaluation
        """

        logging.info("Début de l'évaluation des trajets")
        total_time = 0
        remplissage = []
        for t in Trucks:
            if not t.is26T:
                sum_trajet = 0
                trajet = 0
                for elem in t.route:
                    if elem.Id < 0:
                        if sum_trajet > TAUX_REMPLISSAGE_CAMION * CAMION_44T_CAPACITE_EN_KG:
                            logging.warning(
                                f"Le trajet {trajet} 44T du jour {t.day} déborde avec une charge de [{sum_trajet}]")
                        sum_trajet = 0
                        trajet += 1
                        continue
                    else:
                        sum_trajet += elem.poids


                total_time += t.time_road(Time_Matrix)
                if t.time_road(Time_Matrix) > Max_time:
                    logging.warning(f"Un camion de capacité {t.capacity} rempli à {t.remplissage} dépasse la contraintes de temps de {t.time_road(Time_Matrix)-Max_time}s")
                #Evaluation.evaluate(t.route, Time_Matrix, Max_time, t.capacity, Depot_id)
                remplissage.append(remplissage_moyen(t))
           
            else:

                sum_trajet=0
                trajet = 0
                for elem in t.route :
                    if elem.Id < 0:
                        if sum_trajet > TAUX_REMPLISSAGE_CAMION * CAMION_26T_CAPACITE_EN_KG:
                            logging.warning(
                                f"Le trajet {trajet} 26T du jour {t.day} déborde avec une charge de [{sum_trajet}]")
                        sum_trajet = 0
                        trajet += 1
                        continue
                    else:
                     sum_trajet += elem.poids

                total_time += t.time_road(Time_Matrix)
                #if t.time_road(Time_Matrix) > Max_time:
                    #logging.warning(f"Un camion de capacité {t.capacity} rempli à {t.remplissage} dépasse la contraintes de temps de {t.time_road(Time_Matrix) - Max_time}s")
                # Evaluation.evaluate(t.route, Time_Matrix, Max_time, t.capacity, Depot_id)
                remplissage.append(remplissage_moyen(t))
        total = 0
        for t in Trucks:
            total += t.remplissagec
            total += t.remplissageb
        logging.info(f'Poids récolté de la semaine : {total}')
        logging.info(
            f"Remplissage moyen des bulles vidées sur la semaine : {round(sum(remplissage) / len(remplissage) * 100, 2)}%")
        bulles_debordent = monitoring(Trucks, Dict_Bulles, bulles_debordent, TAUX_REMPLISSAGE_BULLE)
        logging.info(
            "Le temps de travail total sur la semaine est estimé à " + str(round(total_time / 3600, 2)) + " heures")
        total_simulation_time += total_time



        Solution.append(Trucks)
        # plotMap(Trucks, Dict_Bulles, Depots, f"week{week}.html")

        if numberOfWeeks > 1:
            Trucks_copy = copy.deepcopy(Trucks)
            Dict_Bulles_copy = copy.deepcopy(Dict_Bulles)
            Dict_Bulles_copy,date_debut = update_dict_weekly(Trucks_copy, Dict_Bulles_copy,date_debut)
            Dict_Bulles_copy = clustering.compute_weights_week(Dict_Bulles_copy)
            Dict_Bulles = Dict_Bulles_copy


    logging.info("La somme des temps estimés de tous les trajets sur l'ensemble de la simulation est " + str(
        round(total_simulation_time / 3600, 2)) + " heures")
    
    Solution = tri_solution(Solution)
        
    Solution = separation_route_en_plusieurs(Solution)

    return Solution, bulles_debordent


if __name__ == "__main__":
    with open('data/parametre.json', encoding='utf-8') as json_data:
        param = json.load(json_data)
    Sol, bullesdeb = main(param)
    print(f"\n\n")
    for idx, sol in enumerate(Sol):
        print(f"\n--------------------------------SEMAINE {idx+1}--------------------------------")
        print(f"{len(sol)} camions pour la semaine")
        for idx2, truck in enumerate(sol):
            isMulti = False
            if len(truck.route) > 1:
                isMulti = True
            print(f"CAMION {idx2 + 1} is26T = {truck.is26T} affecté au jour {truck.day + 1}, multiRoute = {isMulti}, {truck.remplissage/1000} tonnes ; temps = {round(truck.time/3600, 1)} Heures")
print('end')