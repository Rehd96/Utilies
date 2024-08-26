# -*- coding: utf-8 -*-
"""
Created on Wed May 29 18:05:16 2024

@author: Ion
"""
import pandas as pd
import json
debug = 0

def write_excel(test_pd,debug = 0 ):

    if debug != 0:
        from datetime import datetime
        today =  datetime.today().strftime('%Y-%m-%d_%H_%M')
        concat = pd.concat(test_pd)
        writer = pd.ExcelWriter(f'check_{today}.xlsx', engine='xlsxwriter')
        concat.to_excel(writer,sheet_name = 'recap',index = False)
        writer.close()
        

def check_this_machine(differenza,machine,checking_plc_or_mes ,shift_report_machine,  site_id , PBI_DATA_machine , Type , shifts , this_issues, debug =0 ):
    this = {}
    this_diff = 0
    this['Machine'] = machine
    this['site_id'] = site_id
    this['type'] = Type
    try:
        
        for what in list(shift_report_machine.keys()):
            for valore in range(shifts):
                machine_PBI = [i for i in PBI_DATA_machine  if int(i['SHIFT_NUMBER']) == valore+1][0][checking_plc_or_mes[what]]
                machine_SR = shift_report_machine[what][valore]
                if machine_PBI == '':
                    machine_PBI = 0
                else:
                    machine_PBI = int(machine_PBI)
                diff = machine_PBI - machine_SR
                differenza += diff
                if machine_PBI != 0 : this_perc = diff/machine_PBI*100  
                else: this_perc = 0
                #print(f'Per la {machine} , turno {valore+1} , abbiamo PBI : {machine_PBI} , SR : {machine_SR} , diff = {diff}')
                this[f'Shift {valore+1} {what}'] = diff
                #this[f'Shift {valore+1} {what} descr'] = f'{machine_PBI} - {str(machine_SR)}  = {diff} '
                this[f'Shift {valore+1} {what} % diff'] = str(this_perc)
    except :
        #print(f'issues on {machine} on {file}')
        this_issues.append(machine)
        this[f'Shift {valore+1} {what}'] = 'issue'
        #this[f'Shift {valore+1} descr'] = 'issue'
        this[f'Shift {valore+1} % diff'] = 'issue'
    return this , this_issues




f = open('data.csv' ,'r').read().splitlines()
f = [i.split(',') for i in f]
#keys = ['SHIFT_START' ,'SHIFT_NUMBER', 'SITE_ID' , 'WORK_CENTER' , 'DECPROD' , 'DECSCRAP' , 'PLCPROD' , 'PLCSCRAP' ,'WORK_ORDER'  ]
keys = ['SHIFT_START','SHIFT_NUMBER' , 'SITE_ID' , 'WORK_CENTER' , 'DECPROD' , 'DECSCRAP' , 'PLCPROD' , 'PLCSCRAP'  ]
differenze = {}
f = f[1:]
PBI_DATA = [{keys[i]: ff[i] for i in range(len(keys))} for ff in f]
PBI_DATA_pd  = pd.DataFrame( data = PBI_DATA, columns= [a for a in PBI_DATA[0].keys()])
PBI_DATA_plants = list(set([i['SITE_ID'] for i in PBI_DATA]))

MAP_PLANTS = {'FRE':1661 , 'CHA' : 1105 , 'CHI' : 1161, 'MEN' : 1131 , 'CHA': 1105 , 'PES': 1162 ,'LNB' : 1101}
file_check = {a: int(x) for x in PBI_DATA_plants  for a in MAP_PLANTS if MAP_PLANTS[a] == int(x)}
recap_of_recaps = []
issues = {}
shifts = 3 # how many shifts ? this will go from 1 to 3 indicating how many shits to check 

#for every plant 
for file in list(file_check.keys()):
    SHIFT_REPORT_RECAP_THIS_PLANT = json.loads(open(f'{file}.txt' , 'r').read().splitlines()[0])
    PBI_DATA_THIS_PLANT  = [i for i in PBI_DATA if i['SITE_ID'] == str(file_check[file])]
    frek = list(SHIFT_REPORT_RECAP_THIS_PLANT.keys())
    plc = [i for i in frek if 'plc/time' in i]
    mes = [i for i in frek if 'mes/time' in i]
    PLC_SHIFT_REPORT_RECAP_THIS_PLANT = SHIFT_REPORT_RECAP_THIS_PLANT[plc[0]]
    MES_SHIFT_REPORT_RECAP_THIS_PLANT = SHIFT_REPORT_RECAP_THIS_PLANT[mes[0]]
    differenza = 0 
    general_check = []
    SHIFT_REPORT_OF_PC_OR_MES = [PLC_SHIFT_REPORT_RECAP_THIS_PLANT,MES_SHIFT_REPORT_RECAP_THIS_PLANT ]
    
    this_issues = []
    for choose in range(len(SHIFT_REPORT_OF_PC_OR_MES)) :  #ciclo sia sui valori del plc che su quelli del mes
        recap = []
        plc_or_mes_check = {0 : 'plc' , 1 : 'mes'}
        if choose == 0:
            checking_plc_or_mes = {'production_produced' :'PLCPROD' ,'scraped' : 'PLCSCRAP'  }
        else:
            checking_plc_or_mes = {'production_produced' :'DECPROD' ,'scraped' : 'DECSCRAP'  }
        
        
        for machine in SHIFT_REPORT_OF_PC_OR_MES[choose] : 
            site_id = str(file_check[file])
            Type =  plc_or_mes_check[choose]
            shift_report_machine = SHIFT_REPORT_OF_PC_OR_MES[choose][machine]
            
            PBI_DATA_machine = [i for i in PBI_DATA_THIS_PLANT if i['WORK_CENTER'] == machine]
            
            this , this_issues = check_this_machine(differenza, machine , checking_plc_or_mes,shift_report_machine , site_id ,PBI_DATA_machine ,  Type ,shifts , this_issues,   debug)
            recap.append(this)
        
        general_check.append({plc_or_mes_check[choose] : recap})

    
    plc_recap_pd = pd.DataFrame( data = general_check[0]['plc'], columns= [a for a in general_check[0]['plc'][0].keys()])
    mes_recap_pd = pd.DataFrame( data = general_check[1]['mes'], columns= [a for a in general_check[1]['mes'][0].keys()])
    recap_of_recaps.append(general_check[0]['plc'])
    recap_of_recaps.append(general_check[1]['mes'])
    if this_issues != []:
        print(f'on {file} found {len(this_issues)} issues')
        issues[file_check[file]] = this_issues
test_pd = [pd.DataFrame(data = i, columns= [a for a in i[0].keys()]) for i in recap_of_recaps]




write_excel(test_pd,debug)



if debug ==1 :
    file = 'PES'
    choose = 0
    machine = 'IPN052'
    what = 'production_produced'
    valore = 2
    what = list(SR_machine.keys())[0]