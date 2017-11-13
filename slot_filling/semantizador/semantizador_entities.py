# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:34:48 2017

@author: erich
"""
#Importing dependencies
import re
from cogroo_interface import Cogroo
import watson_developer_cloud
import json

#Importing own functions

import entity_class as ec
import semantizador_noun_chunks as snc
import semantizador_types as st
import semantizador_relationships as sr
import semantizador_datetime as sd
import semantic_map as sm

CLIENT_ACCESS_TOKEN = '9480dca442fa4b079e8382d5712b075c'
API_KEY = "AIzaSyAKGEidnvkggJ-k8PiI5-PUP9DDDgwyw5w"

#Abre seção do cogroo
cogroo = Cogroo.Instance()

#Abre sessão do Watson
watson = watson_developer_cloud.ConversationV1(
    username='46485294-3d4b-4068-9f2e-dea4797cf2ac',
    password='lbTkhbwTbSXm',
    version='2017-05-26'
)

def get_all_entities(input_text):
    #--------------------------------------------------
    #------------------POS extraction------------------
    #--------------------------------------------------
    
    noun_chunks_list = snc.get_noun_chunks(input_text, cogroo)
      
    #---------------------------------------------
    #------------------Heuristics-----------------
    #---------------------------------------------

    date_entity,time_entity,mapped_datetime = sd.get_time_date(input_text,watson)    
    types_list = st.get_types_entities(input_text)
    relationships_list = sr.get_relationship_entities(input_text)
    semantic_map = sm.get_semantic_map(input_text)

    #-------------------------------------------
    #------------------Filters------------------
    #-------------------------------------------
    
    #Creating list of date and time
    datetime_list = []
    if date_entity != None:
        datetime_list.append(date_entity)
    if time_entity != None:
        datetime_list.append(time_entity)
        
    #Filter 1: Remove all the relationship and datetime entities - identified through rules
    reasoned_list = relationships_list + datetime_list

    filter1_list = [] #Contains everything that is not relationship entities
    
    for noun_chunk in noun_chunks_list:
        overlap_flag = False
        for entity in reasoned_list:
            if ec.exists_overlap(noun_chunk,entity):
                overlap_flag = True
        if overlap_flag == False:
            filter1_list.append(noun_chunk)
    

    
    #Filter 2: Remove all the places entities - identified through semantic map
    filter2_1_list = [] #Places entities
    filter2_2_list = [] #Participant entities
    filter2_3_list = [] #Others
    
    for entity in filter1_list:
        entity_type = sm.reason_semantic(entity,semantic_map)     
        if entity_type == "place":
            filter2_1_list.append(entity)
        elif entity_type == "participant":
            filter2_2_list.append(entity)
        else:
            filter2_3_list.append(entity)
    
#    print("---- Noun_chunks ----")
#    for noun_chunk in noun_chunks_list:
#        print(noun_chunk.text,end = ",")
#    print("")
#            
#    print("---- Filter 1.0 ----")    
#    for entity in filter1_list:
#        print(entity.text)    
#    
#    print("---- Filter 2.1 ----")    
#    for entity in filter2_1_list:
#        print(entity.text)
#        
#    print("---- Filter 2.2 ----")    
#    for entity in filter2_2_list:
#        print(entity.text)
#        
#    print("---- Filter 2.3 ----")    
#    for entity in filter2_3_list:
#        print(entity.text)
            
    #-------------------------------------------
    #------------------Results------------------
    #-------------------------------------------
    
    #Moving all the filtered entities to the right lists 
    places_list = filter2_1_list
    non_relationships_list = filter2_2_list
    try:
        date = mapped_datetime["date"]
    except:
        date = None
    try:
        time = mapped_datetime["time"]
    except:
        time = None
    
    #Printing the results
    print("-"*20)
    
    print("Essas são as entidades data: ",end = "")
    if date != None:
        print(date_entity.text + " mapeada para " + date)
    else:
        print("")
        
    print("Essas são as entidades tempo: ",end = "")
    if time != None:
        print(time_entity.text + " mapeada para " + time)
    else:
        print("")
    
    print("Essas são as entidades participante: ",end = "")
    for entity in non_relationships_list:
        print(entity.text,end = ", ")
    print("")
    
    print("Essas são as entidades participante por relacionamento: ",end = "")
    for entity in relationships_list:
        print(entity.text,end = ", ")
    print("")
    
    print("Essas são as entidades local: ",end = "")
    for entity in places_list:
        print(entity.text,end = ", ")
    print("")
    
    print("Essas são as entidades tipo-compromisso: ",end = "")
    for entity in types_list:
        print(entity.text,end = ", ")
        
    return non_relationships_list,places_list,relationships_list,types_list,date,time
#
#user_input = ""
#while True and user_input != "stop":
#    user_input = input("Escreva a frase: ")
#    b = get_all_entities(user_input)

