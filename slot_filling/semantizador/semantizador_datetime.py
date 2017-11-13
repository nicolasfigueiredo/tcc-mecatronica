# -*- coding: utf-8 -*-
"""
Created on Sat Nov 11 12:39:22 2017

@author: erich
"""

import watson_developer_cloud
import entity_class as ec

def get_time_date(input_text,watson):
    date_entity = None
    time_entity = None

    response = watson.message(
        workspace_id='ed0df1dc-ab0a-474b-9612-02ea8d61bcfe',
        message_input={
            'text': input_text
        }
    )

    entities = response['entities']

    mapped_values = {}

    for entity in entities:
        if entity['entity'] == 'sys-date':
            mapped_values['date'] = entity['value']
#            locations['date'] = entity['location']
            entity_start = int(entity['location'][0])
            entity_end = int(entity['location'][1])
            date_entity = ec.Entity(input_text[entity_start:entity_end],entity_start,entity_end)
            
        elif entity['entity'] == 'sys-time':
            mapped_values['time'] = entity['value']
#            locations['time'] = entity['location']
            entity_start = int(entity['location'][0])
            entity_end = int(entity['location'][1])
            time_entity = ec.Entity(input_text[entity_start:entity_end],entity_start,entity_end)
    
    if not mapped_values:
        return None,None,None
    
    return date_entity,time_entity,mapped_values
#    if not locations:
#        return None, None

#    return entities_recognized, locations