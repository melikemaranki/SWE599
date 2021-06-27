import tagme
from semantics.confidential import tagme_token

tagme.GCUBE_TOKEN = tagme_token

def run():
    text = "At the beginning of March, thousands of refugees gathered in the shadow of the Pazarkule border gate in Turkey after President Recep Tayyip Erdoğan said he would “open the gate” to Europe. They had no choice but to go, she says: “[Turkish forces] threatened us with weapons.” Rima says that there was minimal food provision and medical care in Malatya. “Thousands of people were flooded to the border as a political leverage or blackmailing material,” he says. “My friend is still suffering from injuries on his hand.” Ibrahim says he has spent about $1,700 (£1,380) and exhausted nearly all his finances on the attempt to cross the border into Europe."
    annotations = tagme.annotate(text)

    # Print annotations with a score higher than 0.1
    for ann in annotations.get_annotations(0.1):
        link_prep = "<a href=" + ann.uri() + ',target="_blank">' + ann.mention + "</a>"
        text = text.replace(ann.mention,link_prep)
   
    return text
