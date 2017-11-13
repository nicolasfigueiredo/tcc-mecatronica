# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 17:52:47 2017

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

def get_bi_grams(sentence):
    bi_grams_list = [] 
    parsed_sentence = parse_sentence(sentence)
    for index in range(len(parsed_sentence[:-1])):
        bi_grams_list.append(parsed_sentence[index] + " " + parsed_sentence[index + 1])
    return bi_grams_list

def get_relevant_preps():
    place_preps = ["no","nos","na","nas","em",
                   "para","pra","pro",
                   "a um", "ao"] #evitei colocar 'a' aqui para não criar problemas de conflito com artigos e etc.
    
    participant_preps = ["com","junto de"]
    
    time_preps = ["à","às"]
    
    return place_preps,participant_preps,time_preps


def locate_relevant_preps (sentence):
    place_preps_on_sentence = []
    participant_preps_on_sentence = []
    time_preps_on_sentence = []

    #Breaking down the sentence in bi grams and words
    parsed_sentence = parse_sentence(sentence)
    bi_grams_list = get_bi_grams(sentence)
    
    #Getting all the relevant preps
    place_preps, participant_preps,time_preps = get_relevant_preps()
    
    for word in parsed_sentence:
        word_entity = ec.create_entity(word,sentence)
        if word in place_preps:
            place_preps_on_sentence.append(word_entity)
        elif word in participant_preps:
            participant_preps_on_sentence.append(word_entity)
        elif word in time_preps:
            time_preps_on_sentence.append(word_entity)
    
    for bi_gram in bi_grams_list:
        try:
            bi_gram_entity = ec.create_entity(bi_gram,sentence)
        except:
            True
        if bi_gram in place_preps:
            place_preps_on_sentence.append(bi_gram_entity)
        elif bi_gram in participant_preps:
            participant_preps_on_sentence.append(bi_gram_entity)
        elif bi_gram in time_preps:
            time_preps_on_sentence.append(bi_gram_entity)
    
    return place_preps_on_sentence,participant_preps_on_sentence,time_preps_on_sentence

def get_semantic_map(sentence):
    import operator
    sentence = sentence.lower()
    place_preps,participant_preps,time_preps = locate_relevant_preps(sentence)
    relevant_preps = place_preps + participant_preps + time_preps

    #Sorting the relevant_preps according to the "start" attribute
    sorted_relevant_preps = sorted(relevant_preps, key=operator.attrgetter('start'))

    #Creating a semantic map
    semantic_map = "-"*len(sentence)
#     semantic_map = sentence

    for index,relevant_prep in enumerate(sorted_relevant_preps):
        map_m = ""
        map_l = ""
        map_r = ""
        #If it is not the last prep
        if  relevant_prep != sorted_relevant_preps[-1]:
            next_prep = sorted_relevant_preps[index + 1]
            #If semantic_map indicates place, "l", from "local"
            if relevant_prep in place_preps:
                map_prep = (relevant_prep.end - relevant_prep.start)*"L"
                map_m = (next_prep.start - relevant_prep.end)*"l"
                map_l = semantic_map[:relevant_prep.start] + map_prep
                map_r = semantic_map[next_prep.start:]
                new_semantic_map = map_l + map_m + map_r 
                semantic_map = new_semantic_map
            elif relevant_prep in participant_preps:
            #If semantic_map indicates place, "c", from "companhia"
                map_prep = (relevant_prep.end - relevant_prep.start)*"C"
                map_m = (next_prep.start - relevant_prep.end)*"c"
                map_l = semantic_map[:relevant_prep.start] + map_prep 
                map_r = semantic_map[next_prep.start:]
                new_semantic_map = map_l + map_m + map_r 
                semantic_map = new_semantic_map
            elif relevant_prep in time_preps:
            #If semantic_map indicates place, "t", from "tempo"
                map_prep = (relevant_prep.end - relevant_prep.start)*"T"
                map_m = (next_prep.start - relevant_prep.end)*"t"
                map_l = semantic_map[:relevant_prep.start] + map_prep 
                map_r = semantic_map[next_prep.start:]
                new_semantic_map = map_l + map_m + map_r 
                semantic_map = new_semantic_map
                
        else:
            sentence_end = len(sentence)
            if relevant_prep in place_preps:
                map_prep = (relevant_prep.end - relevant_prep.start)*"L"
                map_m = (sentence_end - relevant_prep.end)*"l"
                map_l = semantic_map[:relevant_prep.start] + map_prep 
                new_semantic_map = map_l + map_m 
                semantic_map = new_semantic_map
            elif relevant_prep in participant_preps:
                map_prep = (relevant_prep.end - relevant_prep.start)*"C"
                map_m = (sentence_end - relevant_prep.end)*"c"
                map_l = semantic_map[:relevant_prep.start] + map_prep 
                new_semantic_map = map_l + map_m
                semantic_map = new_semantic_map
            elif relevant_prep in time_preps:
                map_prep = (relevant_prep.end - relevant_prep.start)*"T"
                map_m = (sentence_end - relevant_prep.end)*"t"
                map_l = semantic_map[:relevant_prep.start] + map_prep 
                new_semantic_map = map_l + map_m
                semantic_map = new_semantic_map
    return semantic_map

def reason_semantic (entity,semantic_map):
    semantic_region = semantic_map[entity.start:entity.end]
    if "l" in semantic_region:
        entity_type = "place"
    elif "c" in semantic_region:
        entity_type = "participant"
    else:
        entity_type = "unknown"
        
    return entity_type