# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 17:12:46 2020

@author: lenovo
"""
from itertools import combinations
from correlation import correlation_scores


def delete_null(data_final,properties,delete_ratio):
    print("finding null properties...")
#    config = read_config()
#    globals().update(config)
    delete_ratio = float(delete_ratio)
    nan_list = []
    del_list = []
    total = len(data_final)
    flag = 0
    for i in data_final:
        if flag == 0:
            flag = flag + 1
            continue;
        count = list(data_final[i]).count("Null")
        ratio = count/total
        nan_list.append(ratio)
        if ratio > delete_ratio:
            del_list.append(i)
    data_final = data_final.drop(del_list, 1)
    for i in del_list:
        properties.remove(i)
    return data_final,nan_list,properties

def sort_properties(properties,nan_list):
    print("soritng properties...")
    properties = [x for _,x in sorted(zip(nan_list,properties))]
    return properties

def find_combinations(properties):
    print("finding all the combinations...")
    com_list= []
    for i in range(len(properties)): 
#        combos = combinations(properties, i+1)
#        for combo in combos:
#            text_file.write(str(combo) + "\n")
        x = list(combinations(properties, i+1))
        for j in range(len(x)):
            x[j] = list(x[j])
            com_list.append(x[j])
    return com_list

def correlation(properties,num_keywords):
    print("finding corrlated properties...")
    del_list = []
    corr_scores = correlation_scores(properties,num_keywords)
    for i in range(len(corr_scores)):
        max_score = corr_scores[i][i]
        for j in range(len(corr_scores[i])):
            if j == i:
                break;
            if abs(corr_scores[i][j]-max_score) > 1:
                del_list.append(j)
    del_list = sorted(list(set(del_list)))
    a_index = [i for i in range(len(properties))]
    a_index = set(a_index)
    b_index = set(del_list)
    index = list(a_index-b_index)
    properties = [properties[i] for i in index]
    return corr_scores,properties
    

