# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:30:26 2017

@author: erich
"""

def parse_sentence (sentence):
    cleaned_sentence = sentence.replace(",","")
    cleaned_sentence = cleaned_sentence.replace(".","")
    cleaned_sentence = cleaned_sentence.replace("?","")
    cleaned_sentence = cleaned_sentence.replace("!","")
    parsed_sentence = cleaned_sentence.split()
    return parsed_sentence

def get_list_of_places():
    #sinonimos de lugares para comer
    lista_places_comer = ["restaurante","comida",
                          "jantar","almoço",
                         "café","rango","comer"]
    #sinonimos de lugares para beber
    lista_places_beber = ["bar","boteco",
                         "breja","litrão",
                         "beber"]
    #sinonimos de lugares para dançar
    lista_places_dancar = ["balada","night",
                          "festa"]
    #sinonimos de lugares para fazer esporte
    lista_places_esporte = ["esporte","atividade física",
                          "fitness","jogo"]
    #sinonimos de lugares para casa
    lista_places_casa = ["casa","casa de amigo"]
    #sinonimos de lugares para reunião
    lista_places_reuniao = ["reunião","conversa"]
    #sinonimos de lugares para diversão
    lista_places_diversao = ["cinema","shopping",
                             "parque","parque de diversões"]
    #todos os locais
    list_of_places = lista_places_comer + lista_places_beber + lista_places_dancar + lista_places_esporte + lista_places_casa + lista_places_reuniao + lista_places_diversao
    
    return list_of_places

def get_places_on_sentence (parsed_sentence, list_of_places):
    lista_places_on_sentence = []    

    for word in parsed_sentence:
        word_lowercase = word.lower()
        if word_lowercase in list_of_places:
            lista_places_on_sentence.append(word_lowercase)
    
    return lista_places_on_sentence

def get_places_entities (sentence):
    list_of_places = get_list_of_places()
    parsed_sentence = parse_sentence(sentence)
    places_on_sentence = get_places_on_sentence(parsed_sentence,list_of_places)
    return places_on_sentence