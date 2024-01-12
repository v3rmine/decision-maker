#!/usr/bin/env python3

from json import (dumps)
from operator import contains
from spacy import (load)
from spacy.tokens import (Token)

# HEAD_TOKENS = ["NN", "NNS", "NNP", "PRP"]
VERB_TOKENS = ["VB", "VBZ"]

def unique_extend(list_a, list_b) -> list:
    for e in list_b:
        if e not in list_a:
            list_a.append(e)
    return list_a
        

# def find_first_nn(t: Token) -> Token:
#     # Return first NN in recursive
#     if t.tag_ in HEAD_TOKENS:
#         return t
#     # Return first child with NN
#     for children in t.children:
#         result = find_first_nn(children)
#         if result.tag_ in HEAD_TOKENS:
#             return result
#     # Else return first token
#     return t

def recurse_heads(t: Token, head: Token):
    result = [t.i + 1]
    if t.has_head() and t != head:
        result.extend(recurse_heads(t.head, head))
    return result

def recurse_children(t: Token, ignored_token_tag: list[str] = []):
    result = []
    if len(ignored_token_tag) == 0 or t.tag_ not in ignored_token_tag:
        result = [t.i + 1]
        for child in t.children:
            result.extend(recurse_children(child, ignored_token_tag))
    return result

def main():
    result = {
        'prompt': input(),
        # Analyse the semantics of the prompt
        'tokens': [],
        # Analyse the dependencies between the tokens
        'dependencies': [],
        # Actions to take for this prompt (done manually for the moment)
        # Frame token (action) => linked (with a relation type) to tokens => linked to head token (target)
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
        })

        if token.tag_ in VERB_TOKENS:
            elements = []

            for tok in token.children:
                # TODO: Find sementic head using the frame type
                # semantic_head = find_first_nn(tok)
                # if semantic_head.tag_ in HEAD_TOKENS:
                # Store tokens from head -> current token 
                tokens_id = recurse_children(tok, ["MD"])
                if len(tokens_id) > 0:
                    tokens_id.sort()
                    elements.append({
                        # 'semantic_head_id': semantic_head.i + 1,
                        'tokens_id': tokens_id,
                    })

            result['semantics_frames'].append({
                'token_id': token.i + 1,
                'elements': elements
            })

    print(dumps(result, separators=(', ', ': '), indent=2))

if __name__ == '__main__':
    main()