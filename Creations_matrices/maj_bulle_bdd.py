# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 08:59:40 2022

@author: Younes
"""


import mysql.connector
import pandas as pd

mydb = mysql.connector.connect(
    host = 'db',
    user = 'vanheede',
    password = 'xXZq25d74zsn2-a',
    database ='vanheede'
    )
mycursor = mydb.cursor();

mycursor.execute('select num_bulle from bulles where id_depot = 1')
result = mycursor.fetchall()
bulle = []
for i in range(len(result)):
    bulle.append(result[i][0])
# print(bulle)
#%%
DataRamassage = pd.read_excel("maj_bulle.xlsx", usecols=[1, 5])
data = DataRamassage.values.tolist()  


#%%
table = []

print(data[1])
for i in range(len(bulle)):
    for j in range(len(data)):
        if bulle[i] in data[j][1]:
            tuples = (bulle[i],data[j][0])
            table.append(tuples)
            #print('yes  '+ bulle[i])
print()
table.sort(key= lambda tup: (tup[1],tup[0]))

dicts = {table[i][0]: table[i][1] for i in range(len(table))}
print(dicts)

for i in bulle:
    if i in dicts:
        print('ok')
    else:
        print(i)
keys = list(dicts.keys())
values = list(dicts.values())

for i in range(len(dicts)):
    
    mycursor.execute(f"UPDATE bulles SET date_vidange = '{values[i]}' WHERE num_bulle = '{keys[i]}'")
    print(i)
    mydb.commit()
