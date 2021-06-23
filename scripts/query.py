import requests, pytz, json
from geotext import GeoText
from rdflib import Graph, Literal, URIRef
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import DCTERMS, FOAF, RDF
import rdflib
import pandas as pd
from semantics.confidential import my_api_key, host_address
from summa import keywords
from summa.summarizer import summarize
from collections import defaultdict

# ./fuseki-server --loc=/home/ubuntu/opt/fuseki/datasets --update /MyData
local = "http://localhost"
dataset_name = "MyData"


""" HTTP_endpoint = local +':3030/' + dataset_name + '/data'
Query_endpoint = local +':3030/'  + dataset_name + '/query' #or http://localhost:3030/MyDataset/sparql
Update_endpoint =  local +':3030/'  + dataset_name + '/update' """

HTTP_endpoint = host_address +':3030/' + dataset_name + '/data'
Query_endpoint = host_address +':3030/'  + dataset_name + '/query' #or http://localhost:3030/MyDataset/sparql
Update_endpoint =  host_address +':3030/'  + dataset_name + '/update'

def run(query_text = "germany"):
    query = """prefix dbo: <http://dbpedia.org/ontology/>
    prefix dcterms: <http://purl.org/dc/terms/>
    prefix foaf: <http://xmlns.com/foaf/0.1/>
    prefix sioc: <http://rdfs.org/sioc/ns#>
        
    SELECT ?article ?article_title ?article_text  WHERE { 
      ?article sioc:title ?article_title  .
      ?article sioc:topic ?article_section . 
      ?article sioc:content ?article_text . 
      FILTER regex(?article_title,""" +'"'+query_text+'"'+""", "i")
    } 
    LIMIT 5"""
    response = requests.post(Query_endpoint,
    data={'query':query})
    results = response.json()['results']['bindings']
   
    content = defaultdict(list)
    for result in results:
        content['title'].append(result['article_title']['value'])
        content['url'].append(result['article']['value'])
        content['kws'].append(keywords.keywords(result['article_text']['value'], words = 7))
        content['abstract'].append(summarize(result['article_text']['value'], words = 100))
      

      
    contents = pd.DataFrame.from_dict(content)
    for index, row in contents.iterrows():
      print(row['title'])
    print(contents)
    
        #result_text += "title: " + title + "\n\nkeywords: " + " ".join(kws.splitlines()) + "\n\nurl: " + url + "\n\nabstract: " + abstract + "\n\n\n\n"
    #print(result_text)
    #print(contents)
    return content