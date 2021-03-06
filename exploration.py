#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 11:35:34 2018

@author: dennis
"""

import pandas as pd
import numpy as np
import math
import os
import json
    
# parameters and data
filename = "Chr20GWAStraits.tsv"
infofile = "Chr20GeneData.tsv"
gofile = "Chr20GOslimData.tsv"

output = "edges.json"
geneoutput = "geneinfo.json"
reducedoutput = "Chr20Reduced.tsv"
sep = "\t"

# manually defined dictionary of classification mappings
class_dict = {"asthma":"physical",
              "arthritis":"physical",
              "diabetes":"physical",
              "narcolepsy":"physical",
              "cancer":"physical",
              "leukemia":"physical",
              
              "depression": "mental",
              "anger": "mental",
              "schizophrenia": "mental",
              "bipolar": "mental",
              "attention": "mental",
              "loneliness": "mental",
              
              "head": "head",
              "face": "head",
              "facial": "head",
              "brain": "head",
              "intelligence": "head",
              "well-being": "head",
              "memory": "head",
              "hair": "head",
              
              "heart": "heart",
              
              "blood": "blood",
              "artery": "blood",
              
              "lung": "lung",
              "pulmonary": "lung",
              
              "breast": "breast",
              
              "waist": "waist",
              "obesity": "waist",
              "bmi": "waist",
              "body mass": "waist",
              
              "liver": "liver",
              "kidney": "liver",
              
              "height": "height",
              
              }

def output_json(mapping,score):
    """ Creates a JSON outut file"""
    
    # combine to list, so we can put it to JSON
    temp_list = []
    for el in mapping:
        # line layout: source (Gene), target (bodypart), score
        temp_list.append([el[0], el[1], str(score[el])])
        
    json_string = '{ "links":['
    for el in temp_list:
        json_string += '{"source":"'+el[0]+'","target":"'+el[1]+'","value":"'+el[2]+'"},'
    json_string = json_string[:-1] + ']}'
    
    with open(output, "w") as f:
        f.write(json_string)

if __name__ == "__main__":
    os.chdir(".")
    
    # Manually read in file. Split at specified separator, clean any line breaks, and force lowercase
    trait_list = []
    with open(filename, "r") as f:
        data = f.readlines()
        for line in data:
            temp = line.split(sep)
            temp[1] = temp[1].lower().strip("\n")
            trait_list.append(temp)

    # skip header
    trait_list = trait_list[1:]
    
    # create empty sets and dictionaries
    # We're using sets, since it automatically cancels the problem of duplicate edges.
    mapping = set()
    score = {}
    
    # go over all the examples we have and find whether keywords appear
    for key in class_dict.keys():
        for j, el in enumerate(trait_list):
            if key in el[1]:
                tup = (el[0], class_dict[key])
                
                # add an intensity score, which is linearly increased
                if (tup in mapping):
                    score[tup] += 1
                else:
                    score[tup] = 1
                mapping.add(tup)
                
    # create output file
    output_json(mapping, score)
    
    
    # utilize pandas dataframes for second part, where we prepare the Gene information.
    info = pd.read_csv(infofile, sep=sep)
    go = pd.read_csv(gofile, sep=sep)
    # avoid conflict for later join
#    go.rename(index=str, columns={"ID":"go_ID", "name":"go_name", "namespace":"go_namespace", "def":"go_def", "counts": "go_counts"})
    
#    info.join(go, on="GO_C", rsuffix="_go_c")

    # create list of genes that appear:
    genes = set()
    for el in mapping:
        genes.add(el[0])
        
    # create manual truth vector for values that are in array
    boolean = [False] * info.shape[0]
    for i in range(info.shape[0]):
        if (info.iloc[i,0] in genes):
            boolean[i] = True
            
    info = info[boolean]
    
    # write as file
    # JSON for the JS part
    info.to_json(geneoutput, orient="index")
    # tsv for the horizontal svg
    info.to_csv(reducedoutput, sep=sep, index=False)
    
    
