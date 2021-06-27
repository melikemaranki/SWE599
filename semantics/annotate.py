import tagme
from .confidential import tagme_token

tagme.GCUBE_TOKEN = tagme_token

def get_annotated_text(text):
    
    annotations = tagme.annotate(text)
    #score >0.3 are selected
    for ann in annotations.get_annotations(0.3):
        link_prep = '<a href=%s target="_blank">%s</a>' % (ann.uri(), ann.mention)
        text = text.replace(" "+ann.mention," "+link_prep)   #spaces are added to prevent replacing text inside urls
    return text