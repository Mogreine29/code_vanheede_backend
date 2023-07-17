# -*- coding: utf-8 -*-
"""
Created on Thu Oct 20 16:18:34 2022

@author: antho
"""

import pandas as pd
from datetime import date
import datetime


df = pd.read_excel(r'optimisation/liste_triee_quevy.xlsx',sheet_name='PO01')
#print(df)


jour0 = date(2021, 8, 30)
jourfin = date(2021, 9, 13)
diff = jourfin - jour0
diff = diff.days
Poids = 700
JourMtn = date(2021, 9, 6)
diff2 = jourfin - JourMtn
diff2 = diff2.days
Estimation = Poids*diff2/diff
#print(Estimation)

t = "2021-08-30"
t = t.split("-")
m = date(int(t[0]),int(t[1]),int(t[2]))
#print(type(m))
#print(m)

#%%
dateref = date(2022,5,8)
for day in range(0, 7):
    date_semaine = dateref+datetime.timedelta(days=day)
    #print(date_semaine)