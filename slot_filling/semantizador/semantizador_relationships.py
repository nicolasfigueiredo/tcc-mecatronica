# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:31:41 2017

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

def get_list_of_relationships ():
    #Lista de relacoes tipo pais e filhos
    lista_relacoes_pf = ["esposa","esposo",
                         "esposas","esposos",
                         "pais","pai","mãe",
                         "filho","filha",
                         "filhos","filhas",
                         "irmão","irmã",
                         "irmãos","irmãs"]
    
    #lista de relacoes tipo avos e netos
    lista_relacoes_an = ["avô","avó",
                         "avô","avó",
                         "neto","neta",
                         "netos","netas"
                         "bisavô","bisavó",
                         "bisavôs","bisavós",
                         "bisneto","bisneta",
                         "bisnetos","binestas",
                         "trisavô","trisavó",
                         "trisavôs","trisavós",
                         "tataravô","tataravó",
                         "tataravôs","tataravós"]
    
    #Lista de relacoes tipo tios, sobrinhos e primos
    lista_relacoes_tsp = ["tio","tia",
                          "tios","tias",
                          "primo","prima",
                          "primos","primas",
                          "sobrinho","sobrinha",
                          "sobrinhos","sobrinhas"]
    
    #lista de relacoes tipo "in-law"
    lista_relacoes_il = ["sogro","sogra",
                         "sogros","sogras",
                         "cunhado","cunhada",
                         "cunhados","cunhadas",
                         "nora","genro",
                         "noras","genros"]
    #todas as relacoes
    list_of_relationships = lista_relacoes_pf + lista_relacoes_an + lista_relacoes_tsp + lista_relacoes_il
    
    return list_of_relationships

def get_relationships_on_sentence (parsed_sentence, list_of_relationships):
    lista_relacoes_on_sentence = []    

    for word in parsed_sentence:
        word_lowercase = word.lower()
        if word_lowercase in list_of_relationships:
            lista_relacoes_on_sentence.append(word_lowercase)
    
    return lista_relacoes_on_sentence

def get_relationship_entities (sentence):
    list_of_relationships = get_list_of_relationships()
    parsed_sentence = parse_sentence(sentence)
    relacoes_on_sentence = get_relationships_on_sentence(parsed_sentence,list_of_relationships)
    relacoes_radars = []
    if relacoes_on_sentence != []:
        for index,word in enumerate(parsed_sentence):
            if word in relacoes_on_sentence:
                word_index = index
                try:
                    pre1_word = parsed_sentence[word_index - 1]
                except:
                    pre1_word = ""
                try:
                    post1_word = parsed_sentence [word_index + 1]
                    post2_word = parsed_sentence [word_index + 2]
                except:
                    post1_word = ""
                    post2_word = ""
    #            word_radar = pre1_word + " " + word + " " + post1_word + " " + post2_word
                word_radar = [pre1_word,word,post1_word,post2_word]
                relacoes_radars.append(word_radar)
    
    relacoes_entidades = []
    for relacoes_radar in relacoes_radars:
        if "de" in relacoes_radar or "da" in relacoes_radar or "do" in relacoes_radar:
            relacoes_entidade = relacoes_radar[1] + " " + relacoes_radar[2] + " " + relacoes_radar[3]
        else:
            relacoes_entidade = relacoes_radar[0] + " " + relacoes_radar[1]
        relacoes_entity = ec.create_entity(relacoes_entidade,sentence)
        relacoes_entidades.append(relacoes_entity)
    return relacoes_entidades