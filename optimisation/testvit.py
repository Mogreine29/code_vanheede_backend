# -*- coding: utf-8 -*-
"""
Created on Sun Nov  6 11:06:16 2022

@author: alexi
"""
import pandas as pd
import datetime 
Vrai_id_bulle="VH8095"
dateref=datetime.datetime(2021, 5, 17)
Vitesse_Excell = pd.read_excel(r'C:\Users\alexi\Documents\ProjetOpti\vanheede\Vanheede_VF\backend\optimisation\Vitesse.xlsx',sheet_name = Vrai_id_bulle,header=None)
Vitesse_Excel = Vitesse_Excell.values.tolist()
V_C=Vitesse_Excel[dateref.month][2]
V_B=Vitesse_Excel[dateref.month][1]
#print(V_B,V_C)