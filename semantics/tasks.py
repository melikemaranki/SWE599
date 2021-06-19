import requests, pytz, json
from geotext import GeoText
from rdflib import Graph, Literal, URIRef
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import DCTERMS, FOAF, RDF
import rdflib
import pandas as pd
from .confidential import my_api_key, host_address
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


def collect_data(q_text = 'covid', page_no = 1):
    parameters = {'q': q_text, 
           'page-size': 1,
           'page':page_no, 
           'show-fields': 'bodyText,headline,wordcount,shortUrl',
           'show-tags': 'contributor',
           'api-key': my_api_key }
    r = requests.get('http://content.guardianapis.com/search', params=parameters)
    return r

def build_graph(r):
    #https://www.w3.org/Submission/sioc-related/
    #When linking a sioc:Post to its creator, two options are offered:
    #The first one is to use a "sioc:Post sioc:has_creator sioc:User" statement.
    #The second one is to use a "sioc:Post foaf:maker foaf:Person" statement.

    # Define Namespaces
    g = Graph()
    SIOC = rdflib.Namespace("http://rdfs.org/sioc/ns#")
    DBO = rdflib.Namespace('http://dbpedia.org/ontology/')
    g.bind("foaf", FOAF)
    g.bind("sioc", SIOC)
    g.bind("dcterms", DCTERMS)
    g.bind("dbo", DBO)
    articles = r.json()['response']['results']


    for article in articles:
        article_text = article['fields']['bodyText']
        authors = article["tags"]
        article_section = Literal(article["sectionName"])
        article_publication_date = Literal(article["webPublicationDate"])
        article_title = Literal(article['fields']['headline'])
        article = URIRef(article['fields']['shortUrl'])

        g.add((article, RDF.type, SIOC.Post))
        g.add((article, SIOC.title, article_title))
        g.add((article, SIOC.topic, article_section))
        g.add((article, DCTERMS.created, article_publication_date))
        g.add((article, DCTERMS.publisher, Literal("the Guardian")))
        g.add((article, SIOC.content, Literal(article_text)))

        country_codes = GeoText(article_text).country_mentions
        country_names = []

        #Country names found in the bodyText will be added to the ontology
        for code in country_codes:
            #pytz doesn't recognize UK code.
            if(code == 	'UK'):
                code = 'GB'
            #https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes
            if(code == "XK"):
                country_name = "Kosovo"
            elif(code.strip() == "DO"):
                country_name ="Dominican Republic"
            else:
                try:
                    country_name = pytz.country_names[code]
                except:
                    country_name = "Other"
            country_names.append(country_name)
            g.add((article, DBO.country, Literal(country_name)))

        # Triples (Subject -> Predicate -> Object)
        for author in authors:
            authorName = author["webTitle"]
            authorUrl = author["webUrl"]
            author = URIRef(authorUrl) #shortUrl
            g.add((author, RDF.type, FOAF.Person))
            g.add((author, FOAF.name, Literal(authorName))) #friend of a friend ontology

            #For author both foaf:maker or sioc:has_creator can be used. SIOC one decided to be kept.
            g.add((article, SIOC.has_creator, author))

    return g.serialize(format="turtle").decode("utf-8")



def load_data():
    
    r = collect_data(page_no=34608)
    max_page_no = r.json()['response']['total']
    i = 34609
    while(i <= max_page_no):
        print(i, ". page from total: ", max_page_no, " is being loaded.", sep="")
        data = build_graph(r)
    
        prefixes = "prefix dbo: <http://dbpedia.org/ontology/>\
        prefix dcterms: <http://purl.org/dc/terms/> \
        prefix foaf: <http://xmlns.com/foaf/0.1/> \
        prefix sioc: <http://rdfs.org/sioc/ns#> \n"
        lines = append_lines(data.splitlines()[5:])
        
        
        response = requests.post(Update_endpoint, data={'update':prefixes +
        'INSERT  DATA{' + lines +'}'}) 
        r= collect_data(page_no=i)
        i += 1

def append_lines(lines):
        text = ""
        for line in lines:
            text += line
        return text

def query_data(query_text):
    response = requests.post(Query_endpoint,
    data={'query':query_text})
    vars = response.json()['head']['vars']
    results = response.json()['results']['bindings']
   
    d = defaultdict(list)
   
    for result in results:
        for key in vars:
            d[key].append(result[key]['value'])

    df = pd.DataFrame.from_dict(d)
    
    return df

def basic_query_data(query_text):
    query = """prefix dbo: <http://dbpedia.org/ontology/>
prefix dcterms: <http://purl.org/dc/terms/>
prefix foaf: <http://xmlns.com/foaf/0.1/>
prefix sioc: <http://rdfs.org/sioc/ns#>
    
SELECT ?article ?article_title ?article_text  WHERE { 
      ?article sioc:title ?article_title  .
      ?article sioc:topic ?article_section . 
      ?article sioc:content ?article_text . 
      FILTER regex(?article_text,""" +'"'+query_text+'"'+""", "i")
    } 
    LIMIT 5"""
    response = requests.post(Query_endpoint,
    data={'query':query})
    results = response.json()['results']['bindings']
   
    result_text = ""
    for result in results:
        title = result['article_title']['value']
        kws = keywords.keywords(result['article_text']['value'], words = 7)
        url = result['article']['value']
        abstract = summarize(result['article_text']['value'], words = 100)
    
        result_text += "title: " + title + "\n\nkeywords: " + " ".join(kws.splitlines()) + "\n\nurl: " + url + "\n\nabstract: " + abstract + "\n\n\n\n"
    return result_text
    

def clear_default_graph():
    #clearing default graph
    requests.post(Update_endpoint, data={'update':"CLEAR DEFAULT"})