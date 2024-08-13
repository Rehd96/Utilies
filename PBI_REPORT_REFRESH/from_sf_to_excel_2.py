# -*- coding: utf-8 -*-
"""
Created on Fri Oct 13 16:46:53 2023

@author: Ion
"""

# -*- coding: utf-8 -*-




import json
from datetime import datetime  
import pytz
import pandas as pd

amount_of_time = 15
cf = json.load(open('configu.json','r'))
local_tz = pytz.timezone(cf['local_tz'])
utc = pytz.timezone('UTC')
euro = cf['euro']
ww = cf['ww']
ww2 = cf['ww2']


def get_lista_plant(f):
    dizionari = {}
    for i in f:
        diz = {}
        diz['plant'] = int(i[2])
        diz['success'] = int(i[3])
        diz['from'] =  datetime.strptime( i[5] , forma)
        diz['to'] =    datetime.strptime( i[6] , forma)
        diz['start'] = datetime.strptime( i[7] , forma)
        diz['end'] =   datetime.strptime( i[8] , forma)
        diz['diff'] = diz['start'] - diz['to'] 
        diz['diff'] = int(diz['diff'].seconds)//60
        dizionari[diz['plant']] =  diz 
    return dizionari


def select_world_zone(lista_plants):
    which_plants = 'null'
    key_0  = list(lista_plants.keys())[0]
    if key_0 in euro:
        which_plants = euro
    else:
        if short == 1:
            which_plants = ww
        else:
            which_plants = ww2
    return which_plants

missing = input("press y if we have PBI refreshes, n if don't")
cond = input("press a button to start, e for extra time delay")
try:
    while cond != '0':
        amount_of_time = 20
        if cond == 'e' :
            amount_of_time = 1500
        forma = '%d/%m/%Y, %H:%M:%S'
        f = open(cf['refresh_file'],'r').read().splitlines()
        f = [i.split('\t') for i in f]
        refreshes = [[i[2],i[3]] for i in f if i[4] == 'Completata']
        refreshes = [[datetime.strptime(i[0], forma), datetime.strptime(i[1], forma)] for i in refreshes]
        refreshes = refreshes[::-1]
        ##AT THIS POINT I HAVE THE PBI REFRESHSES, IN UTC+1 OR LOCAL TIME
        
        
        forma = '%Y-%m-%d %H:%M:%S.%f'
        short = cf['short'] #if short = 0 consider all plants, otherwise only the reduced version
        f = open(cf['refresh_to_export'],'r').read().splitlines()
        f = [i.split('\t') for i in f]
        ##HERE I HAVE THE SF JOBS, IN UTC
        
        lista_plants = get_lista_plant(f)
        lista_per_pd = [lista_plants[key] for key in lista_plants.keys()]
        lista_pd = pd.DataFrame(data = lista_per_pd,columns= [i for i in lista_per_pd[0].keys()])
        world_zone = select_world_zone(lista_plants)
        
        returning = [{'plants':i} for i in world_zone ]
        calculation_end = [[lista_plants[i]['plant'],lista_plants[i]['end']] for i in  list(lista_plants.keys()) ]
        refreshes = [[i[0].astimezone(pytz.timezone('UTC')).strftime('%d/%m/%Y, %H:%M:%S'),i[1].astimezone(pytz.timezone('UTC')).strftime('%d/%m/%Y, %H:%M:%S')] for i in refreshes]
        refreshes = [[datetime.strptime(i[0], '%d/%m/%Y, %H:%M:%S'), datetime.strptime(i[1], '%d/%m/%Y, %H:%M:%S')] for i in refreshes]    
        #Asia/Baku
        for i in range(len(returning)):
            if returning[i]['plants'] in lista_plants:
                plant = lista_plants[returning[i]['plants']]
                returning[i]['time'] = plant['end']
                if plant['diff'] > amount_of_time and plant['plant'] not in [2222]:
                    returning[i]['time'] = 'the calc took place ' + str(plant['diff']) + ' minutes after shift end!' 
                    returning[i]['refresh'] =' error'
                if plant['from'] == plant['to']:
                    returning[i]['time'] = 'start = end!'
                    returning[i]['refresh'] =' error'
                if plant['success'] == 0:
                    returning[i]['time'] = 'Success = FALSE!'
                    returning[i]['refresh'] =' error'
                if type(returning[i]['time']) != str:
                    for ref in range(len(refreshes)-1):
                        if plant['end'] > refreshes[ref][0] and plant['end'] <= refreshes[ref+1][0]:
                            returning[i]['refresh'] = refreshes[ref+1][1]
            else:
                returning[i]['time'] = 'no time'
                returning[i]['refresh'] = 'no refresh'
        
        if world_zone != euro :
            returning =  [[i['plants'],i['time'].astimezone(pytz.timezone('Europe/Berlin')),i['refresh'].astimezone(pytz.timezone('Europe/Berlin'))] if type(i['time']) != str else [i['plants'],i['time'],i['refresh']] for i in returning ]
        if world_zone == euro : #from OCT to MARCh, daylight saving time = 'Asia/Famagusta' /      UTC+2 : Asia/Baku
            returning = [[i['plants'],i['time'].astimezone(pytz.timezone('Asia/Baku')),i['refresh'].astimezone(pytz.timezone('Asia/Baku'))] if type(i['time']) != str else [i['plants'],i['time'],i['refresh']] for i in returning ]
        ret = ''
        
        righe = []
        with open(cf['refresh_to_export'],'w') as g:
            for i in returning:
                riga = ''
                if type(i[1]) != str: 
                    if '00:' in str(i[2]):
                        ttt = str(i[2]).replace('00:', '24:')
                        riga = str(i[1])[-14:-6] + '\t' + ttt[-14:-6]
                        righe.append(riga)
                    else:
                        riga = str(i[1])[-14:-6] + '\t' + str(i[2])[-14:-6]
                else:
                    riga = str(i[1]) + '\t' + str(i[2])
                if missing == 'n':
                    riga = str(i[1])[-14:-6] + '\t' + '\t'
                if 'no refresh' not in riga:
                    g.write(riga)
                g.write('\n')
            for i in returning:
                riga = [str(a)+'\t' for a in i]
                
                g.write(str(riga))
                g.write('\n')
        cond = input("press any case to redo, 0 to esc")
        
except:
    import fromSFtoexcel
    print("there was no refresh avaialbe, doing other script")
    fromSFtoexcel.do_it()
       