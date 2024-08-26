# -*- coding: utf-8 -*-
"""
Created on Wed May 29 18:05:16 2024

@author: Ion
"""
import pandas as pd
import json
"""
df =  pd.read_excel('PBI DATA.xlsx',sheet_name = 'Sheet1')
df_PBI_DATA = df.to_dict()
df_2 = [{a:df_PBI_DATA[a[i]] for a in df_PBI_DATA.keys()} for i in range(4169)]

"""

f = open('data.csv' ,'r').read().splitlines()

f = [i.split(',') for i in f]
#keys = ['SHIFT_START' ,'SHIFT_NUMBER', 'SITE_ID' , 'WORK_CENTER' , 'DECPROD' , 'DECSCRAP' , 'PLCPROD' , 'PLCSCRAP' ,'WORK_ORDER'  ]
keys = ['SHIFT_START','SHIFT_NUMBER' , 'SITE_ID' , 'WORK_CENTER' , 'DECPROD' , 'DECSCRAP' , 'PLCPROD' , 'PLCSCRAP'  ]
differenze = {}
f = f[1:]
PBI_DATA = [{keys[i]: ff[i] for i in range(len(keys))} for ff in f]
PBI_DATA_pd  = pd.DataFrame( data = PBI_DATA, columns= [a for a in PBI_DATA[0].keys()])

#file_check = {'FRE':1661 , 'CHA' : 1105 , 'CHI' : 1161, 'MEN' : 1131}
file_check = {'PES':1162}
recap_of_recaps = []
excel_names = []

shifts = 3
for file in list(file_check.keys()):
    SHIFT_REPORT_PLANT = json.loads(open(f'{file}.txt' , 'r').read().splitlines()[0])
    PBI_DATA_this  = [i for i in PBI_DATA if i['SITE_ID'] == str(file_check[file])]
    frek = list(SHIFT_REPORT_PLANT.keys())
    plc = [i for i in frek if 'plc/time' in i]
    mes = [i for i in frek if 'mes/time' in i]
    SHIFT_REPORT_PLC = SHIFT_REPORT_PLANT[plc[0]]
    SHIFT_REPORT_MES = SHIFT_REPORT_PLANT[mes[0]]
    
    
    differenza = 0 
    general_check = []
    plc_or_mes = [SHIFT_REPORT_PLC,SHIFT_REPORT_MES ]
    for choose in range(len(plc_or_mes)) : 
        recap = []
        plc_or_mes_check = {0 : 'plc' , 1 : 'mes'}
        if choose == 0:
            plc_or_scrap = {'production_produced' :'PLCPROD' ,'scraped' : 'PLCSCRAP'  }
        else:
            plc_or_scrap = {'production_produced' :'DECPROD' ,'scraped' : 'DECSCRAP'  }
        
        for machine in plc_or_mes[choose] : 
            this = {}
            this_diff = 0
            this['Machine'] = machine
            this['site_id'] =  str(file_check[file])
            this['type'] = plc_or_mes_check[choose]
            try:
                
                SR_machine = plc_or_mes[choose][machine]
                PBI_DATA_machine = [i for i in PBI_DATA_this if i['WORK_CENTER'] == machine]
                for what in list(SR_machine.keys()):
                    for valore in range(shifts):
                        machine_PBI = [i for i in PBI_DATA_machine if int(i['SHIFT_NUMBER']) == valore+1][0][plc_or_scrap[what]]
                        machine_SR = SR_machine[what][valore]
                        if machine_PBI == '':
                            machine_PBI = 0
                        else:
                            machine_PBI = int(machine_PBI)
                        diff = int(machine_PBI) - machine_SR
                        differenza += diff
                        if machine_PBI != 0 : this_perc = diff/machine_PBI*100  
                        else: this_perc = 0
                        #print(f'Per la {machine} , turno {valore+1} , abbiamo PBI : {machine_PBI} , SR : {machine_SR} , diff = {diff}')
                        this[f'Shift {valore+1} {what}'] = diff
                        this[f'Shift {valore+1} % diff'] = this_perc
            except :
                print(f'issues on {machine}')
            recap.append(this)
        plc_or_mes_check = {0 : 'plc' , 1 : 'mes'}
        general_check.append({plc_or_mes_check[choose] : recap})
        excel_names.append(f'{file}_{plc_or_mes_check[choose]}')

    plc_recap_pd = pd.DataFrame( data = general_check[0]['plc'], columns= [a for a in general_check[0]['plc'][0].keys()])
    mes_recap_pd = pd.DataFrame( data = general_check[1]['mes'], columns= [a for a in general_check[1]['mes'][0].keys()])
    recap_of_recaps.append(general_check[0]['plc'])
    recap_of_recaps.append(general_check[1]['mes'])
test_pd = [pd.DataFrame(data = i, columns= [a for a in i[0].keys()]) for i in recap_of_recaps]


from datetime import datetime
today =  datetime.today().strftime('%Y-%m-%d')


concat = pd.concat(test_pd)
writer = pd.ExcelWriter(f'check_{today}_3.xlsx', engine='xlsxwriter')
concat.to_excel(writer,sheet_name = 'recap',index = False)
#for i in range(len(test_pd)): write multiples excel with one sheet name each dataframe
#    test_pd[i].to_excel(writer, sheet_name=excel_names[i],index = False)
writer.close()
