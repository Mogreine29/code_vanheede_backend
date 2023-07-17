# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 10:20:58 2022

@author: Younes
"""

import mysql.connector
import requests
from global_var import ON_SERVER

if ON_SERVER:
  mydb = mysql.connector.connect(host = 'db',user = 'vanheede',password ='xXZq25d74zsn2-a',database = 'vanheede')

else:
  mydb = mysql.connector.connect(host = 'db',user = 'vanheede',password ='xXZq25d74zsn2-a', database = 'vanheede')

def maj(site):
    
    mycursor = mydb.cursor();
    mycursor.execute("select id_site,longitude,latitude from site where id_depot = 1") #0 10 11
    result_quevy = mycursor.fetchall();
    
    if ON_SERVER:
      url = 'http://ors-app:8080/ors/v2/matrix/driving-hgv' #ors-app si on est dans le serveur sinon c'est localhost
    else:
      url = 'http://ors-app:8080/ors/v2/matrix/driving-hgv' #ors-app si on est dans le serveur sinon c'est localhost
    
    cords=[]
    for i in result_quevy:
        cord = [i[1],i[2]]
        cords.append(cord)
    
    
    myobj = {"locations": cords, "metrics":["distance","duration"]}
    x = requests.post(url, json = myobj)
    x = x.json()
        
    durees = x["durations"]
    distances = x["distances"]
    
    for i in range(len(durees)):
    
        mycursor.execute(f"UPDATE site SET time_vector = '{durees[i]}',distance_vector	= '{distances[i]}' WHERE id_site = {result_quevy[i][0]}")
        mydb.commit()
    
    mycursor.execute("select id_site,longitude,latitude from site where id_depot = 2")
    result_dottignies = mycursor.fetchall();
    if ON_SERVER:
      url = 'http://ors-app:8080/ors/v2/matrix/driving-hgv' #ors-app si on est dans le serveur sinon c'est localhost
    else:
      url = 'http://ors-app:8080/ors/v2/matrix/driving-hgv' #ors-app si on est dans le serveur sinon c'est localhost
    
    cords=[]
    for i in result_dottignies:
        cord = [i[1],i[2]]
        cords.append(cord)
    
    myobj = {"locations": cords, "metrics":["distance","duration"]}
    x = requests.post(url, json = myobj)
    x = x.json()
        
    durees = x["durations"]
    distances = x["distances"]
    
    for i in range(len(durees)):
    
        mycursor.execute(f"UPDATE site SET time_vector = '{durees[i]}',distance_vector	= '{distances[i]}' WHERE id_site = {result_dottignies[i][0]}")
        mydb.commit()
    
    
    mycursor.execute('select id_site,longitude,latitude from site where id_depot = 1')
    result_quevy = mycursor.fetchall()
    mycursor.execute('select longitude,latitude from depot where id_depot = 1')
    depot_quevy = mycursor.fetchall()

    cords_quevy = [depot_quevy[0][0],depot_quevy[0][1]]

    cords = [] 
    for i in result_quevy:
        cord = [i[1],i[2]]
        cords.append(cord)

    cords.insert(0,cords_quevy)
    myobj = {"locations": cords, "metrics":["distance","duration"],"sources":[0]}
    x = requests.post(url, json = myobj)
    x = x.json()
    durees = x["durations"]
    distances = x["distances"]

    for i in range(len(durees)):
        
        mycursor.execute(f"UPDATE depot SET time_vector = '{durees[0]}',distance_vector	= '{distances[0]}' WHERE id_depot = 1")
        mydb.commit()
        
    mycursor.execute('select id_site,longitude,latitude from site where id_depot = 2')
    result_dottignies = mycursor.fetchall()
    mycursor.execute('select longitude,latitude from depot where id_depot = 2')
    depot_dottignies = mycursor.fetchall()

    cords_dottignies = [depot_dottignies[0][0],depot_dottignies[0][1]]

    cords = [] 
    for i in result_dottignies:
        cord = [i[1],i[2]]
        cords.append(cord)

    cords.insert(0,cords_dottignies)
    myobj = {"locations": cords, "metrics":["distance","duration"],"sources":[0]}
    x = requests.post(url, json = myobj)
    x = x.json()
    durees = x["durations"]
    distances = x["distances"]

    for i in range(len(durees)):
        
        mycursor.execute(f"UPDATE depot SET time_vector = '{durees[0]}',distance_vector	= '{distances[0]}' WHERE id_depot = 2")
        mydb.commit()
        
    mycursor.execute('select id_site,longitude,latitude from site')
    result_mineral = mycursor.fetchall()
    mycursor.execute('select longitude,latitude from depot where id_depot = 3')
    depot_mineral = mycursor.fetchall()

    cords_mineral = [depot_mineral[0][0],depot_mineral[0][1]]

    cords = [] 
    for i in result_mineral:
        cord = [i[1],i[2]]
        cords.append(cord)

    cords.insert(0,cords_mineral)
    myobj = {"locations": cords, "metrics":["distance","duration"],"sources":[0]}
    x = requests.post(url, json = myobj)
    x = x.json()
    durees = x["durations"]
    distances = x["distances"]

    for i in range(len(durees)):
        
        mycursor.execute(f"UPDATE depot SET time_vector = '{durees[0]}',distance_vector	= '{distances[0]}' WHERE id_depot = 3")
        mydb.commit()
      
      
    mycursor.execute('select id_site,longitude,latitude from site')
    result_renaix = mycursor.fetchall()
    mycursor.execute('select longitude,latitude from depot where id_depot = 4')
    depot_renaix = mycursor.fetchall()

    cords_renaix = [depot_renaix[0][0],depot_renaix[0][1]]

    cords = [] 
    for i in result_renaix:
        cord = [i[1],i[2]]
        cords.append(cord)

    cords.insert(0,cords_renaix)
    myobj = {"locations": cords, "metrics":["distance","duration"],"sources":[0]}
    x = requests.post(url, json = myobj)
    x = x.json()
    durees = x["durations"]
    distances = x["distances"]

    for i in range(len(durees)):
        
        mycursor.execute(f"UPDATE depot SET time_vector = '{durees[0]}',distance_vector	= '{distances[0]}' WHERE id_depot = 4")
        mydb.commit()
