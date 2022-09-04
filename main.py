# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 17:45:57 2020

@author: lenovo
"""
from sparql import get_dataframe
from preprocessing import find_combinations,delete_null,sort_properties,correlation
import pandas as pd
import configparser
import os


CONFIG_FILE = "config.cfg"
if os.path.exists(os.path.join( os.getcwd(),CONFIG_FILE ) ):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE) 
    KG = config.get("main", "KG") 
    endpoint_url = config.get(KG, "endpoint_url") 
    class_name = config.get(KG, "class_name")
    delete_ratio = config.get(KG, "delete_ratio")
    num_keywords = config.get(KG, "num_keywords")
    class_properties_query = config.get(KG, "class_properties_query")
    values_query1 = config.get(KG, "values_query1")
    values_query2 = config.get(KG, "values_query2")
    
properties_label,properties,data_final = get_dataframe(endpoint_url,class_name,class_properties_query,values_query1,values_query2)
print("step 1 done!")
data_final,nan_list,properties = delete_null(data_final,properties,delete_ratio)
print("step 2 done!")
properties = sort_properties(properties,nan_list)
print("step 3 done!")
#corr_scores, properties = correlation(properties,num_keywords)
#print(corr_scores)
print("step 4 done!")
com_list = find_combinations(properties)
print("step 5 done!")
print("-------------------------------------------------")
result = [[],[]]
for col_1 in com_list:
    data_test = data_final[col_1]
    count = 0
    for i in data_test: 
        count = count + 1
        if(count == 1):
            flag = i
        if(count>1):
            data_test[flag] = data_test[flag].str.cat(data_test[i]) # Merge into string

    uniq =  data_test[flag].nunique()
    result[0].append(str(col_1)) 
    result[1].append(str(uniq)) 
result_df = pd.DataFrame(result)
result_df = result_df.T
columns = ["properties","uniq"]
result_df.columns=columns
result_df.to_csv(str(class_name) +"_result.csv")