# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:33:06 2017

@author: erich
"""

import entity_class as ec

from cogroo_interface import Cogroo
#cogroo = Cogroo.Instance()

def get_noun_chunks(input_text,cogroo):
    noun_chunks_list = []
    pos_tagged_text = cogroo.analyze(input_text).sentences[0]
#    print(pos_tagged_text.chunks)
    for chunk in pos_tagged_text.chunks:
#        print("-"*20)
        chunk_text = input_text[chunk.start:chunk.end]
        chunk_start = chunk.start
        chunk_end = chunk.end
#        print (chunk_text)
#        print(str(chunk_start) + "-" + str(chunk_end))
        if chunk.tag == "NP":
            for token in chunk.tokens:
                token_text = input_text[token.start:token.end]
#                print("Token: " + str(token.pos))
                #Limpando conjuncoes
#                print(token.pos)
                if token.pos == "conj-c":
        #             print("Removendo..." + str(token_text))
                    if chunk.end == token.end:
                        chunk_text = chunk_text[:token.start - chunk_start - 1]
                        chunk_end = token.start - 1
                    else:
                        chunks = chunk_text.split(" e ")
                        chunk_text = chunks[0]
                        chunk_text2 = chunks[1]
                        noun_chunk2 = ec.Entity(text = chunk_text2, start = token.end + 2, end = chunk_end)
                        noun_chunks_list.append(noun_chunk2)
                        chunk_end = token.start - 1
                #Limpando artigos
                elif token.pos == "art":
                    if chunk.start == token.start:
                        chunk_text = chunk_text[token.end - chunk_start + 1:]
                        chunk_start = token.end + 1
#            print("Esse é o chunk: " + str(chunk_text))
            noun_chunk = ec.Entity(text = chunk_text, start = chunk_start, end = chunk_end)
            noun_chunks_list.append(noun_chunk)
#            for item in noun_chunks_list:
#                print (item.text + ", ", end = "")
      
#    print("---- Unglutinated noun_chunks")
#    for chunk in noun_chunks_list:
#        print(chunk.text)
        
    #-----------------------------------------------
    #------------------Aglutinador------------------
    #-----------------------------------------------
    
    #Preparing the pile, aglut_preps and the list to store aglutinated chunks
    noun_chunks_pile = list(noun_chunks_list)
    new_noun_chunks_list = []
    aglut_preps = ["de","do","da"]
            
    while len(noun_chunks_pile) !=0 :
#        print("Size of pile: " +str(len(noun_chunks_pile)))
        joined_chunk = ""
#        print("This is the current chunk: " + noun_chunks_pile[0].text)
        
        #If there is only one item, it is not possible to aglutinate
        if len(noun_chunks_pile) == 1:
            new_noun_chunks_list.append(noun_chunks_pile[0])
            noun_chunks_pile.remove(noun_chunks_pile[0])
        
        #If there are more than one, try to aglutinated
        else:
            current_chunk = noun_chunks_pile[0]
            next_chunk = noun_chunks_pile[1]
#            print("This is the current chunk: " + current_chunk.text)
#            print("This is the next chunk: " + next_chunk.text)
#            print("Condição 1: "+ str( next_chunk.start - current_chunk.end))
#            print("Condição 2: "+ str( input_text[current_chunk.end +1 : next_chunk.start - 1]))
#            
            #Aglutinator 1: Aglutinate consecutive noun_chunks
            if next_chunk.start - current_chunk.end == 1:
                del noun_chunks_pile[1]
                del noun_chunks_pile[0]
                joined_chunk_text = current_chunk.text + " " + next_chunk.text
                joined_chunk = ec.Entity(text = joined_chunk_text, start = current_chunk.start, end = next_chunk.end)
#                joined_chunk = ec.create_entity(joined_chunk_text,input_text)
                noun_chunks_pile.insert(0,joined_chunk)
            
            #Aglutinator 2: Aglutinate if there is a prep "de","da" or "do"
            elif next_chunk.start - current_chunk.end == 4 and input_text[current_chunk.end +1 : next_chunk.start - 1] in aglut_preps:
                aglut_prep = input_text[current_chunk.end +1 : next_chunk.start - 1]
                del noun_chunks_pile[1]
                del noun_chunks_pile[0]
                joined_chunk_text = current_chunk.text + " " + aglut_prep + " " + next_chunk.text
                joined_chunk = ec.Entity(text = joined_chunk_text, start = current_chunk.start, end = next_chunk.end)
#                joined_chunk = ec.create_entity(joined_chunk_text,input_text)
                noun_chunks_pile.insert(0,joined_chunk)
            #If it wasn't aglutinated, remove from the pile and append to aglutinated list
            else:
#                print("This is the chunk added: " + current_chunk.text)
                del noun_chunks_pile[0]
                new_noun_chunks_list.append(current_chunk)   
#        print("This is the new_noun_chunks_list:")
#        for chunk in new_noun_chunks_list:
#            print(chunk.text)
    return new_noun_chunks_list