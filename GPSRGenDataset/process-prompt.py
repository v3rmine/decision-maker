#!/usr/bin/env python3

from json import (dumps)
from spacy import (load)
from spacy.tokens import (Token)

def main():
    result = {
        'prompt': input(),
        # Analyse the semantics of the prompt
        'tokens': [],
        # Analyse the dependencies between the tokens
        'dependencies': [],
        # Actions to take for this prompt (done manually for the moment)
        # Frame token (action) => linked (with a relation type) to tokens => linked to head (target)  
        'semantics_frames': [],
        # TODO: Fill the entities with the ontology / robot memory
        'entities': [],
        # TODO: Assign a token to an entity 
        'lexical_groundings': [],
    }

    nlp = load('en_core_web_sm')
    doc = nlp(result['prompt'])

    for token in doc:
        result['tokens'].append({
            'id': token.i + 1,
            'lemma': token.lemma_,
            'pos': token.tag_,
            'surface': token.text,
        })

        dep_type = str(token.dep_).lower()
        result['dependencies'].append({
            'from': 0 if dep_type == "root" else token.head.i + 1,
            'to': token.i + 1,
            'type': dep_type,
            'text': token.text
        })

        if token.tag_ == "VB":
            elements = []
            def recurse_childrens(c: Token):
                result = [c.i + 1]
                for children in c.children:
                    result.extend(recurse_childrens(children))
                return result

            for tok in token.children:
                tokens_id = recurse_childrens(tok)
                tokens_id.sort()
                elements.append({
                    'tokens_id': tokens_id,
                })

            result['lexical_groundings'].append({
                'token_id': token.i + 1,
                'elements': elements
            })

    print()
    print(dumps(result, separators=(', ', ': '), indent=2))

if __name__ == '__main__':
    main()