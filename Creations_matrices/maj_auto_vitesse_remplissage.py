# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 14:15:54 2022

@author: Micha
"""
import mysql.connector
import ast
import datetime
import time
from global_var import ON_SERVER

if ON_SERVER:
  mydb = mysql.connector.connect(host = 'db',user = 'vanheede',password ='xXZq25d74zsn2-a',database = 'vanheede')
else:
  mydb = mysql.connector.connect(host = 'db',user = 'vanheede',password ='xXZq25d74zsn2-a',database = 'vanheede')

def nbre_jours(year,month):
    if month in [4, 6, 9, 11]:
        return(30)
    elif month in [1, 3, 5, 7, 8, 10, 12]:
        return(31)
    else:
        if year % 400 == 0 or (year % 4 == 0 and year % 100 != 0):
            return(29)
        else:
            return(28)
def diff_month(d1, d2):
    return (d1.year - d2.year) * 12 + d1.month - d2.month
        
def maj_automatisation(bulles):
    #Testtttt---------------
    cnx = mysql.connector.connect(host = 'db',user = 'vanheede',password ='xXZq25d74zsn2-a',database = 'vanheede')

    mycursor = cnx.cursor()

    #mycursor = mydb.cursor()
    mycursor.execute("SELECT num_bulle, date_vidange,vitesse_remplissage_blanc,vitesse_remplissage_colore,vecteur_remplissage_poids_blanc, vecteur_remplissage_poids_colore from bulles")
    liste_bulles = []
    for x in mycursor:
        liste_bulles.append(x)
        
    test = bulles #test = [(datetime.datetime(2023,2,16).date(),"rotulo", 1569, 1223)] => Test de base pour voir le format des données
        
    for w in range(len(liste_bulles)):
        liste_bulles[w] = list(liste_bulles[w])     
        liste_bulles[w][2] = ast.literal_eval(liste_bulles[w][2])
        liste_bulles[w][3] = ast.literal_eval(liste_bulles[w][3])                  #Transformation de la liste de tuples en liste de listes
        liste_bulles[w][4] = ast.literal_eval(liste_bulles[w][4])     #Transformation du string liste en liste
        liste_bulles[w][5] = ast.literal_eval(liste_bulles[w][5])
    #CAS Général : Ajout poids dans vecteur des poids
    """
    Ici, nous allons juste append un poids dans le vecteur_remplissage_poids à chaque fois qu'on vide une bulle.
    Attention, à chaque fois qu'on arrive au mois suivant, la vitesse de remplissage de toutes les bulles de la base de données
    doit être calculée et le vecteur de remplissage des poids supprimé. Nous devons en plus mettre à jour les dates de vidange.
    """

    for j in test:

        temp = 0
        pos = "salut"
        for i in liste_bulles:
            if j[1] == i[0]:
                pos = temp
                break
            temp+=1
        if pos == "salut":
            print("impossible car le nom de la bulle entrée est différent que ceux existants dans la base de donnée")
            break
        if j[0] != liste_bulles[pos][1]:
            if time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[0] != time.strptime(str(j[0]),"%Y-%m-%d")[0] or time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] != time.strptime(str(j[0]),"%Y-%m-%d")[1]:
                nbr_jours = nbre_jours(time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[0], time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1])    #Calcul le nombre de jours du mois de la dernière vidange dans la BD
                fin_mois = nbr_jours - time.strptime(str(i[1]),"%Y-%m-%d")[2] #Calcul le nombre de jours entre la fin du mois et la dernière date de vidange dans la BD pour la bulle
                diff_jours = (j[0]-liste_bulles[pos][1]).days   #Calcul le nombre de jours entre la première vidange du mois suivant et la dernière date de vidange de l'ancien mois
                premier_poids_mois_2_blanc = j[2]
                premier_poids_mois_2_colore = j[3]
                poids_mois_1_blanc = (premier_poids_mois_2_blanc/diff_jours)*fin_mois
                poids_mois_1_colore = (premier_poids_mois_2_colore/diff_jours)*fin_mois
                poids_mois_2_blanc = premier_poids_mois_2_blanc - poids_mois_1_blanc
                poids_mois_2_colore = premier_poids_mois_2_colore - poids_mois_1_colore
                if j[2] == -999 or j[3] == -999:
                    print("")
                else:
                    liste_bulles[pos][4].append(poids_mois_1_blanc)
                    liste_bulles[pos][5].append(poids_mois_1_colore)
                tempo_blanc = 0
                tempo_colore = 0
                #CAS 1 : Bulles déjà existantes
                """
                Vecteur de 12 (correspondant aux mois) dans la table bulle qui se mettent à jour à chaque début de mois suivant(pour verre blanc et coloré).
                Vecteur s'incrémentant à chaque nouvelle vidange (pour chaque bulle).
                Le vecteur_remplissage_poids est remis à 0 au début du mois suivant.
                """
                if len(liste_bulles[pos][4]) > 0:
                    for z in liste_bulles[pos][4]:
                        tempo_blanc += z
                    moyenne_blanc = tempo_blanc /nbr_jours
                else :
                    moyenne_blanc = 0.0
                if diff_month(j[0], liste_bulles[pos][1]) == 1:
                    liste_bulles[pos][2][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1] = moyenne_blanc
                    liste_bulles[pos][4] = []
                else :
                    liste_bulles[pos][2][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1] = moyenne_blanc
                    for i in range(diff_month(j[0], liste_bulles[pos][1])-1): 
                        liste_bulles[pos][2][(time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] +i)%12] = 0.0
                    liste_bulles[pos][4] = []
                if len(liste_bulles[pos][5]) > 0:
                    for z in liste_bulles[pos][5]:
                        tempo_colore += z
                    moyenne_colore = tempo_colore /nbr_jours
                else :
                    moyenne_colore = 0.0
                if diff_month(j[0], liste_bulles[pos][1]) == 1:
                    liste_bulles[pos][3][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1] = moyenne_colore
                    liste_bulles[pos][5] = []
                else :
                    liste_bulles[pos][3][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1] = moyenne_colore
                    for i in range(diff_month(j[0], liste_bulles[pos][1])-1): 
                        liste_bulles[pos][3][(time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] +i)%12] = 0.0
                    liste_bulles[pos][5] = []
                liste_bulles[pos][3][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1] = moyenne_colore
                liste_bulles[pos][5] = []

                #CAS 1 : Bulles dont nous ne disposons pas de données sur une année

                for p in liste_bulles[pos][2]:
                    if p == 100.0001 or p == 200.0001:
                        liste_bulles[pos][2][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1]] = liste_bulles[pos][2][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1]
                for p in liste_bulles[pos][3]:
                    if p == 100.0001 or p == 200.0001:
                        liste_bulles[pos][3][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1]] = liste_bulles[pos][3][time.strptime(str(liste_bulles[pos][1]),"%Y-%m-%d")[1] - 1]

                if j[2] == -999 or j[3] == -999:
                    liste_bulles[pos][1] = j[0]
                else:
                    liste_bulles[pos][4].append(poids_mois_2_blanc/diff_month(j[0], liste_bulles[pos][1]))
                    liste_bulles[pos][5].append(poids_mois_2_colore/diff_month(j[0], liste_bulles[pos][1]))
                    liste_bulles[pos][1] = j[0]


            else:
                if j[2] == -999 or j[3] == -999:
                    liste_bulles[pos][1] = j[0]
                else:
                    liste_bulles[pos][4].append(j[2])
                    liste_bulles[pos][5].append(j[3])
                    liste_bulles[pos][1] = j[0]
        else :
            break

    for i in liste_bulles:
        sql = "UPDATE bulles SET date_vidange = %s, vitesse_remplissage_blanc = %s,vitesse_remplissage_colore = %s, vecteur_remplissage_poids_blanc = %s, vecteur_remplissage_poids_colore = %s WHERE num_bulle = %s"
        val = (i[1], f'{i[2]}',f'{i[3]}',f'{i[4]}',f'{i[5]}',f'{i[0]}')
        mycursor.execute(sql, val)
        cnx.commit()
