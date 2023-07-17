"""
Auteur : Timothy Baeckelant étudiant en ingénieur civil grosse tchol diplomé avec distinction 15.6
de moyenne en BAC3 informatique et gestion, ses amis le trouvent rigolo

Afin de simplifier considérablement le temps de calcul, nous allons
émettre deux hypothèses simplificatrices :

D'une part, les vitesses de remplissages et les temps de trajet entre
chaque bulle suivent une loi de distribution normale à long terme
(théorème central limite).

D'autre part, nous allons considérer que toutes les variables aléatoires
(i.e. chaque temps de trajet et chaque vitesse de remplissage) sont
indépendantes. Cette hypothèse est bien entendue non conforme à la réalité,
quoique meilleure approximation lorsque l'on travaille par site.

Ces hypothèses nous permettront d'une part d'approximer le total en une loi
normale et d'autre part de calculer aisément les paramètres de cette distribution.




INPUT : Route constituée des bulles en tant qu'objet Bulle, liste des écarts-types
de la vitesse de remplissage, limite de temps, limite de capacité, la matrice des temps, le dépot
(l'id du dépot pour le moment)

OUTPUT : Probabilité de réussite du trajet

!!! Code pas encore testé car la version actuelle du main ne run pas donc flemme !!!
"""

import math
from scipy import stats


def multitrip(liste):
    for element in liste:
        if isinstance(element, list) == True:
            return True
    return False


# Il faut run cette fonction pour chaque truck

def evaluate(route, matTime, timeLimit, capacity, idDepot):
    totalTime = 0
    totalpc = 0
    totalpb = 0
    totalVarC = 0
    totalVarB = 0
    totalVarTime = 0

    if multitrip(route) == False:
        traj = [i.Id for i in route]
        tstart = [(traj[i], traj[i + 1]) for i in range(len(traj) - 1)]
        for bulle in route:
            totalpc += bulle.poidsc
            totalpb += bulle.poidsb
            totalVarC += bulle.varc
            totalVarB += bulle.varb
        for (i, j) in tstart:
            totalTime += 1.5 * matTime[i - 1][j - 1]
            totalVarTime += (0.2 * matTime[i - 1][j - 1]) ** 2
        totalTime += 5 * len(traj)
        totalTime += 45
        totalTime += matTime[idDepot - 1][route[0].Id]
        totalVarTime += (0.2 * matTime[idDepot - 1][route[0].Id]) ** 2
        totalTime += matTime[route[-1].Id][idDepot - 1]
        totalVarTime += (0.2 * matTime[route[-1].Id][idDepot - 1]) ** 2

    else:
        for bulle in route[1][:-1]:
            totalpc += bulle.poidsc
            totalpb += bulle.poidsb
            totalVarC += bulle.varc
            totalVarB += bulle.varb
        for bulle in route[2][1:-1]:
            totalpc += bulle.poidsc
            totalpb += bulle.poidsb
            totalVarC += bulle.varc
            totalVarB += bulle.varb
        traj1 = [i.Id for i in route[1]]
        traj2 = [i.Id for i in route[2]]
        tstart1 = [(traj1[i], traj1[i + 1]) for i in range(len(traj1) - 1)]
        tstart2 = [(traj2[i], traj2[i + 1]) for i in range(len(traj2) - 1)]
        for (i, j) in tstart1:
            totalTime += 1.5 * matTime[i - 1][j - 1]
            totalVarTime += (0.2 * matTime[i - 1][j - 1]) ** 2
        for (i, j) in tstart2:
            totalTime += 1.5 * matTime[i - 1][j - 1]
            totalVarTime += (0.2 * matTime[i - 1][j - 1]) ** 2
        totalTime += 5 * len(traj1)
        totalTime += 5 * len(traj2)
        totalTime += 45
        totalTime += matTime[idDepot - 1][route[1][0].Id]
        totalVarTime += (0.2 * matTime[idDepot - 1][route[1][0].Id]) ** 2
        totalTime += matTime[route[1][-1].Id][idDepot - 1]
        totalVarTime += (0.2 * matTime[route[1][-1].Id][idDepot - 1]) ** 2

    probapc = stats.norm.cdf(capacity[1], loc=totalpc, scale=math.sqrt(totalVarC))
    probapb = stats.norm.cdf(capacity[0], loc=totalpb, scale=math.sqrt(totalVarB))
    probaTime = stats.norm.cdf(timeLimit, loc=totalTime, scale=math.sqrt(totalVarTime))

    #print('\n Proba de valider la contrainte de temps : ' + str(probaTime))
    #print('Proba de valider la contrainte de poids blanc : ' + str(probapb))
    #print('Proba de valider la contrainte de poids coloré : ' + str(probapc))            