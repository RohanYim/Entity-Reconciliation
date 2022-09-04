# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 17:31:59 2020

@author: lenovo
"""

# Output the result to a dataframe


import pandas as pd
import re
import json
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import numpy as np
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer   
from sklearn.feature_extraction.text import TfidfTransformer 
import math
from six import iteritems
from six.moves import xrange


def correlation_scores(properties,num_keywords):
#    config = read_config()
#    globals().update(config)
    # BM25 parameters.
    PARAM_K1 = 1.5
    PARAM_B = 0.75
    EPSILON = 0.25
    
    
    class BM25(object):
    
        def __init__(self, corpus):
            self.corpus_size = len(corpus)
            self.avgdl = sum(map(lambda x: float(len(x)), corpus)) / self.corpus_size
            self.corpus = corpus
            self.f = []
            self.df = {}
            self.idf = {}
            self.initialize()
    
        def initialize(self):
            for document in self.corpus:
                frequencies = {}
                for word in document:
                    if word not in frequencies:
                        frequencies[word] = 0
                    frequencies[word] += 1
                self.f.append(frequencies)
    
                for word, freq in iteritems(frequencies):
                    if word not in self.df:
                        self.df[word] = 0
                    self.df[word] += 1
    
            for word, freq in iteritems(self.df):
                self.idf[word] = math.log(self.corpus_size) - math.log(freq + 1)
    
        def get_score(self, document, index, average_idf):
            score = 0
            for word in document:
                if word not in self.f[index]:
                    continue
                idf = self.idf[word] if self.idf[word] >= 0 else EPSILON * average_idf
                score += (idf * self.f[index][word] * (PARAM_K1 + 1)
                          / (self.f[index][word] + PARAM_K1 * (1 - PARAM_B + PARAM_B * self.corpus_size / self.avgdl)))
            return score
    
        def get_scores(self, document, average_idf):
            scores = []
            for index in xrange(self.corpus_size):
                score = self.get_score(document, index, average_idf)
                scores.append(score)
            return scores
    
    
    def get_bm25_weights(corpus):
        bm25 = BM25(corpus)
        average_idf = sum(map(lambda k: float(bm25.idf[k]), bm25.idf.keys())) / len(bm25.idf.keys())
    
        weights = []
        for doc in corpus:
            scores = bm25.get_scores(doc, average_idf)
            weights.append(scores)
    
        return weights
    
    endpoint_url = "https://query.wikidata.org/sparql"
    
    optional = str()
    count = 0
    all_list = []
    ## Process one attribute at a time and input it into the dataframe, then perform the operations of merging, sorting, and deduplication
    for i in properties:
        optional = " ?item wdt:" + i + " ?a. "
        query = """select ?item ?a{
            ?item wdt:P31 wd:Q571.""" + optional + """}"""
    
        def get_results(endpoint_url, query):
            user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
            # TODO adjust user agent; see https://w.wiki/CX6
            sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            return sparql.query()
    
    
        results = get_results(endpoint_url, query)
        processed_results = json.load(results.response)
        
        value = [[],[]]
        for row in processed_results['results']['bindings']:
            value[0].append(row["item"]['value'].split('/')[4])
            if "http://www.wikidata.org/entity/" in row["a"]['value']: 
                value[1].append([row["a"]['value'].split('/')[4]])
            else:
                value[1].append([row["a"]['value']])
        data = pd.DataFrame(value)
        data = data.T
        # merge，sort，groupby
        data_temp = data.groupby(0)[1].apply(lambda x:" ".join(sorted(list(set(np.concatenate(list(x))))))).reset_index()
        df = data_temp.astype(str)
        df_list = df[1].tolist()
        df_string = " ".join(df_list)
        all_list.append(df_string)
    
    for i in range(len(all_list)):  
        all_list[i] = re.sub(r'[^A-Za-z0-9 ]+', '', all_list[i])
        all_list[i] = all_list[i].strip()
    
     
    list_A = all_list
    vectorizer=CountVectorizer()
    transformer=TfidfTransformer()  
    tfidf=transformer.fit_transform(vectorizer.fit_transform(list_A))  
    word=vectorizer.get_feature_names()  
    weight=tfidf.toarray() 
    key_word = []
    num_keywords = int(num_keywords)
    for i in range(len(weight)):
        Xy = [(xi, yi) for xi, yi in zip(weight[i], word) ]
        sorted_Xy = sorted(Xy,reverse=True)
        sorted_X = [xi for xi,_ in sorted_Xy]
        sorted_y = [yi for _,yi in sorted_Xy]
        count = 0
        for x in sorted_X:
            if x > 0:
                count = count + 1
            else:
                break
        if count > num_keywords:
            key_word.append(sorted_y[0:num_keywords])
        else:
            key_word.append(sorted_y[0:count])  
            
    filtered_keywords = []
    for i in range(len(key_word)):
        filtered_keywords.append([word for word in key_word[i] if word not in stopwords.words('english')])
    
    for i in range(len(all_list)):
        all_list[i] = all_list[i].lower()
        all_list[i] = all_list[i].split(" ")
        
    filtered_words = []
    for i in range(len(all_list)):
        filtered_words.append([word for word in all_list[i] if word not in stopwords.words('english')])
    corr_scores = []
    for i in range(len(filtered_words)):
        bm25Model = BM25(filtered_words)
        average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())
        query_str = filtered_keywords[i]
        bm25Model.initialize()
        corr_scores.append(bm25Model.get_scores(query_str,average_idf))
    return corr_scores