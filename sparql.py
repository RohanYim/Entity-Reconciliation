# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:42:40 2020

@author: lenovo
"""
# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

# Find all attributes of this class
import pandas as pd
import numpy as np
import sys
import json
import os
import re
import configparser
from SPARQLWrapper import SPARQLWrapper, JSON

#def read_config():
#    with open("config.json") as json_file:
#        config = json.load(json_file)
#    return config
#
#def update_config(config):
#    with open("config.json", 'w') as json_file:
#        json.dump(config, json_file, indent=4)
#    return None

#def get_config():
#    CONFIG_FILE = "config.cfg"
#    if os.path.exists(os.path.join( os.getcwd(),CONFIG_FILE ) ):
#        config = configparser.ConfigParser()
#        config.read(CONFIG_FILE) 
#        KG = config.get("main", "KG") 
#        endpoint_url = config.get(KG, "endpoint_url") 
#        class_name = config.get(KG, "class_name")
#        delete_ratio = config.get(KG, "delete_ratio")
#        num_keywords = config.get(KG, "num_keywords")
#        class_properties_query = config.get(KG, "class_properties_query")
#        optional = config.get(KG, "optional")
#        values_query = config.get(KG, "values_query")
#        
#        return KG,endpoint_url,class_name,delete_ratio,num_keywords,class_properties_query,optional,values_query

def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def get_property(endpoint_url,class_name,class_properties_query):   
    print("getting properties...")
#    config = read_config()
#    globals().update(config)
#    endpoint_url = endpoint_url
    ## test class: Q11424(FILM)
    query = class_properties_query
#    query = """SELECT ?property ?propertyLabel {
#      VALUES (?class) {(wd:""" + class_name + """)}
#          ?class wdt:P1963 ?property
#      SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }   
#    } ORDER BY ASC(xsd:integer(strafter(str(?property), concat(str(wd:), "P"))))"""
    results = get_results(endpoint_url, query)
    properties = []
    properties_label = []
    for result in results["results"]["bindings"]:
        test_str = re.search(r"\W",result["property"]['value'].split('/')[-1])
        if test_str== None:
            properties.append(result["property"]['value'].split('/')[-1])   # remove meaningless part
        if "propertyLabel" in result.keys(): 
            properties_label.append(result["propertyLabel"]['value'])
    properties = sorted(set(properties),key=properties.index)
    properties_label = sorted(set(properties_label),key=properties_label.index)
    return properties_label,properties

def get_dataframe(endpoint_url,class_name,class_properties_query,values_query1,values_query2):
#    config = read_config()
#    globals().update(config)
    properties_label,properties = get_property(endpoint_url,class_name,class_properties_query)
    if os.path.exists(str(class_name) + ".csv"):
        print("reading csv files...")
        data_final = pd.read_csv(str(class_name) + ".csv")
        return properties_label,properties,data_final
    print("getting dataframe...")
    count = 0
    ## Process one attribute at a time and input it into the dataframe, then perform the operations of merging, sorting, and deduplication
    for i in properties:
#        optional = " OPTIONAL { ?item wdt:" + i + " ?a. }"
        query1 = values_query1
        query2 = values_query2
        query = str(query1) + i + str(query2)

        def get_results(endpoint_url, query):
            user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
            # TODO adjust user agent; see https://w.wiki/CX6
            sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            return sparql.query()
    
    
        results = get_results(endpoint_url, query)
        processed_results = json.load(results.response,strict=False)
        
        value = [[],[]]
        for row in processed_results['results']['bindings']:
            value[0].append(row["item"]['value'].split('/')[4])
            if "a" not in row.keys():
                value[1].append(["Null"]) # If an entity does not have this attribute, output NaN
            else:
                if endpoint_url.split("/")[0] in row["a"]['value']: 
                    value[1].append([row["a"]['value'].split('/')[-1]])
                else:
                    value[1].append([row["a"]['value']])
        data = pd.DataFrame(value)
        data = data.T
        # merge，sort，groupby
        data_temp = data.groupby(0)[1].apply(lambda x:"".join(sorted(list(set(np.concatenate(list(x))))))).reset_index()
        if count ==0:
            data_final = data[[0]].drop_duplicates()
            count += 1
        # Combine dataframes one column at a time after processing
        data_final = pd.merge(data_final,data_temp, on=0)
    ## Change column names
    columns = ["Entities"] + properties
    data_final.columns=columns
    data_final.to_csv(str(class_name) +".csv")
    return properties_label,properties,data_final
