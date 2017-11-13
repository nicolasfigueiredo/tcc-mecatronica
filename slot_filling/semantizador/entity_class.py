# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 11:51:48 2017

@author: erich
"""

class Entity:
    def __init__(self, text, start,end):
        self.text = text
        self.start = start
        self.end = end
        
def create_entity(entity_text,sentence):
    import re
    entity_search = re.search(entity_text,sentence)
    entity_object = Entity(entity_text,entity_search.start(),entity_search.end()-1)
    return entity_object

#def create_prep_entity(prep_text,sentence):
#    import re
#    entity_list = []
#    search_iterator = re.finditer(prep_text,sentence)
#    
#    for search in search_iterator:
#        entity_object = Entity(prep_text,search.start(),search.end())
#        entity_list.append(entity_object)        
#        
#    return entity_list
        
def exists_overlap(entity1,entity2):
    if entity1.start >= entity2.start and entity1.start <= entity2.end:
        return True
    elif entity1.end >= entity2.start and entity1.end <= entity2.end:
        return True
    elif entity2.start >= entity1.start and entity2.start <= entity1.end:
        return True
    elif entity2.end >= entity1.start and entity2.end <= entity1.end:
        return True
    else: return False