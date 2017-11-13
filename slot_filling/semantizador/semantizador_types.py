# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:30:26 2017

@author: erich
"""

import entity_class as ec

def parse_sentence (sentence):
    cleaned_sentence = sentence.replace(",","")
    cleaned_sentence = cleaned_sentence.replace(".","")
    cleaned_sentence = cleaned_sentence.replace("?","")
    cleaned_sentence = cleaned_sentence.replace("!","")
    parsed_sentence = cleaned_sentence.split()
    return parsed_sentence

def get_list_of_types():
    #sinonimos de lugares para comer
    lista_types_comer = ["restaurante","comida",
                          "jantar","almoço",
                         "café","rango","comer"]
    #sinonimos de lugares para beber
    lista_types_beber = ["bar","boteco",
                         "breja","litrão",
                         "beber"]
    #sinonimos de lugares para dançar
    lista_types_dancar = ["balada","night",
                          "festa"]
    #sinonimos de lugares para fazer esporte
    lista_types_esporte = ["esporte","atividade física",
                          "fitness","jogo"]
    #sinonimos de lugares para casa
    lista_types_casa = ["casa","casa de amigo"]
    #sinonimos de lugares para reunião
    lista_types_reuniao = ["reunião","conversa"]
    #sinonimos de lugares para diversão
    lista_types_cinema = ["cinema"]#,"shopping",
                             #"parque","parque de diversões"]
    #todos os locais
    list_of_types = lista_types_comer + lista_types_beber + lista_types_dancar + lista_types_esporte + lista_types_casa + lista_types_reuniao + lista_types_cinema

    synonyms_dict = {"restaurante":lista_types_comer,
                     "bar":lista_types_beber,
                     "balada":lista_types_dancar,
                     "esporte":lista_types_esporte,
                     "casa":lista_types_casa,
                     "reunião":lista_types_reuniao,
                     "cinema":lista_types_cinema}
    
    return list_of_types,synonyms_dict

def get_types_on_sentence (sentence,parsed_sentence, list_of_types):
    import re
    lista_types_on_sentence = []    

    for word in parsed_sentence:
        word_lowercase = word.lower()
        if word_lowercase in list_of_types:
            word_entity = ec.create_entity(word,sentence)
            lista_types_on_sentence.append(word_entity)
    return lista_types_on_sentence

def get_types_entities (sentence):
    mapped_type_on_sentence = []
    list_of_types,synonyms_dict = get_list_of_types()
    parsed_sentence = parse_sentence(sentence)
    types_on_sentence = get_types_on_sentence(sentence,parsed_sentence,list_of_types)
    #Pegando apenas o primeiro "tipo compromisso" que aparecer na frase
    if types_on_sentence !=[]:
        type_on_sentence = types_on_sentence[0]
        for key in synonyms_dict.keys():
            if type_on_sentence.text in synonyms_dict[key]:
                type_on_sentence.text = key
                mapped_type_on_sentence.append(type_on_sentence)
                break
    return mapped_type_on_sentence