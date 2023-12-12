import spacy

config = {
    "task": {
        "@llm_tasks": "spacy.NER.v3",
        "labels": ["OBJECT", "ACTION", "LOCATION"],
        "label_definitions": {
            "ACTION": "something done or performed"
        }
    }
}

def main():
    nlp = spacy.blank("en")
    llm_ner = nlp.add_pipe("llm_ner", config=config)
    nlp.initialize()

    doc = nlp("Grab a banana from the kitchen.")
    print([(ent.text, ent.label_) for ent in doc.ents])
