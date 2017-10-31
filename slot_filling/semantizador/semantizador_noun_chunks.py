# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 09:33:06 2017

@author: erich
"""

def get_noun_chunks(input_text,cogroo):
    noun_chunks_list = []
    pos_tagged_text = cogroo.analyze(input_text).sentences[0]
    for chunk in pos_tagged_text.chunks:
#        print("-"*20)
        chunk_text = input_text[chunk.start:chunk.end]
        if chunk.tag == "NP":
            for token in chunk.tokens:
                token_text = input_text[token.start:token.end]
#                print("Token: " + str(token.pos))
                #Limpando conjuncoes
                if token.pos == "conj-c":
        #             print("Removendo..." + str(token_text))
                    chunk_text = chunk_text.replace(" " + token_text,"")
                #Limpando artigos
                elif token.pos == "art":
                    chunk_text = chunk_text.replace(token_text + " ","")
#            print("Esse é o chunk: " + str(chunk_text))
            noun_chunks_list.append(chunk_text)
    return noun_chunks_list