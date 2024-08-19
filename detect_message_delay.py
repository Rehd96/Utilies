# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 15:46:16 2024

@author: Ion
"""

from kafka import KafkaConsumer
import time
from datetime import datetime

import threading


pes= '10.7.130.14:31006,10.7.130.15:32421,10.7.130.16:31827'
prefix = '1162' 
total = []

# Configurazione del consumer Kafka per 4 topic
topics = [ f'{prefix}-prod-plc-total-good-count', f'{prefix}-prod-plc-cycle-time' ,f'{prefix}-prod-plc-machine-state', f'{prefix}-prod-plc-machine-speed']

consumer = KafkaConsumer(
    *topics,
    bootstrap_servers=pes,
    group_id='Reporting_Monitoring_check',
    auto_offset_reset='latest'
)

# Dizionario per tenere traccia dell'ultimo timestamp per ogni chiave
last_received = {}
keys_alarms = {}
go = 0
# Funzione per controllare il tempo trascorso e inviare allarmi
def check_for_alarms(go):
    cond = True
    while cond:
        current_time = time.time()
        for key, last_time in last_received.items():
            
            if current_time - last_time > 30:
                
                if key not in keys_alarms : 
                    print(f"{datetime.now()} Allarme: più di 30 secondi dall'ultima ricezione della chiave {key}")
                    keys_alarms[key] = 1
                else:
                    keys_alarms[key] +=1 
                    print("ignoring {key}")
        remove = []
        for key in keys_alarms:
            if keys_alarms[key] > 6:
                del keys_alarms[key]
        time.sleep(5)
        if go == 1:
            cond= False

# Thread per il controllo degli allarmi
alarm_thread = threading.Thread(target=check_for_alarms(go))
alarm_thread.daemon = True
alarm_thread.start()

# Consumo dei messaggi dai topic Kafka
for message in consumer:
    key = message.key.decode('utf-8') +'-' +  message.topic
    if key not in last_received:
        last_received[key] = [ time.time() , message.value['values']['value'] ] 
    else:
        value = message.value['values']['value']
        if value != last_received[key][1]:
            last_received[key] = [ time.time() , message.value['values']['value'] ] 
            print(f"changed value for {key} ")
        else:
            print(f"received again same message for {key}")
    total.append(message)