# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 11:16:46 2024

@author: rodri
"""

import pandas as pd

df=pd.read_csv(r"C:\Users\rodri\Downloads\2023.csv",decimal=",",sep=";")
stations=list(df[df.columns[2]])
set_res = set(stations) 
stations = (list(set_res))

lista=[]
for i in stations:
   lista.append(df[df[df.columns[2]]==i])


with pd.ExcelWriter(r"C:\Users\rodri\Desktop\2023\01012023-31122023_Turbidez.xlsx") as writer:
    i=0
    for i in range(len(stations)):
        lista[i].to_excel(writer, sheet_name=stations[i])




   