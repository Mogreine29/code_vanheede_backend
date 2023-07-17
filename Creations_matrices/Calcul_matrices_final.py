# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 13:34:43 2022

@author: Micha
"""
import pandas as pd
import requests

sudhainaut_coord = pd.read_excel("Quevy_site.xlsx", usecols=[7, 8])
walloniepicarde_coord = pd.read_excel("Dottignies_site.xlsx", usecols=[7, 8])

coord_sudhainaut_sites = sudhainaut_coord.values.tolist()
coord_walloniepicarde_sites = walloniepicarde_coord.values.tolist()


url = 'http://localhost:8080/ors/v2/matrix/driving-hgv' #ors-app
print(coord_sudhainaut_sites)
def CreationMatrices(coords,csvtemps,csvdistances) :
    myobj = {"locations": coords, "metrics":["distance","duration"]}
    x = requests.post(url, json = myobj)
    x = x.json()
    durees = x["durations"]
    distances = x["distances"]
    print(f'distance: {distances}')
    print(f'distance: {durees}')

    csv_temps = pd.DataFrame(durees)
    csv_temps.to_csv(f"{csvtemps}.csv",index = False, header = False)
    csv_distances = pd.DataFrame(distances)
    csv_distances.to_csv(f"{csvdistances}.csv",index = False, header = False)


CreationMatrices(coord_sudhainaut_sites,"csvSudHainautTemps","csvSudHainautDistances")
CreationMatrices(coord_walloniepicarde_sites,"csvWalloniePicardeTemps","csvWalloniePicardeDistances")