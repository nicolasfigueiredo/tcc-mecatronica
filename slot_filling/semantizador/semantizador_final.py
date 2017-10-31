# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:34:48 2017

@author: erich
"""
import re
from cogroo_interface import Cogroo

cogroo = Cogroo.Instance()

import semantizador_noun_chunks as snc
import semantizador_places as sp
import semantizador_relationships as sr

def get_all_entities(input_text):
    noun_chunks_list = snc.get_noun_chunks(input_text, cogroo)
    places_list = sp.get_places_entities(input_text)
    relationships_list = sr.get_relationship_entities(input_text)
    
    split_relationship_list = []
    for item in relationships_list:
        split_relationship_list = split_relationship_list + item.split()
    
    non_relationship_list = []
    for noun_chunk in noun_chunks_list:
        if noun_chunk not in places_list and noun_chunk not in relationships_list and noun_chunk not in split_relationship_list:
            noun_chunk = noun_chunk.replace(" e","")
            non_relationship_list.append(noun_chunk)
    return non_relationship_list,places_list,relationships_list
        
#input_text = "Quero ir para um bar com Roberta e meus pais"
#non_relationship_list,places_list,relationships_list = get_all_entities (input_text)
#print(non_relationship_list)
#print(places_list)
#print(relationships_list)

