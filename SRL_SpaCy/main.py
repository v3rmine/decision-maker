from typing import List

import spacy
from numerizer import numerize
from spacy.tokens import Token
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy_llm.util import assemble

"""
POS_LIST = ["ADJ", "ADP", "ADV", "AUX", "CONJ", "CCONJ", "DET", "INTJ", "NOUN", "NUM", "PART", "PRON", "PROPN", "PUNCT", "SCONJ", "SYM", "VERB", "X", "SPACE"]
DEP_LIST = ["acl", "acomp", "advcl", "advmod", "agent", "amod", "appos", "attr", "aux", "auxpass", "case", "cc", "ccomp", "compound", "conj", "cop", "csubj", "csubjpass", "dative", "dep", "det", "dobj", "expl", "intj", "mark", "meta", "neg", "nn", "npmod", "nsubj", "nsubjpass", "oprd", "obj", "obl", "pcomp", "pobj", "poss", "preconj", "prep", "prt", "punct",  "quantmod", "relcl", "root", "xcomp"]
NER_LIST = ["PERSON", "NORP", "FAC", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE", "DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL"]

POS TAGS
--------
ADJ: adjective
ADP: adposition
ADV: adverb
AUX: auxiliary
CCONJ: coordinating conjunction
DET: determiner
INTJ: interjection
NOUN: noun
NUM: numeral
PART: particle
PRON: pronoun
PROPN: proper noun
PUNCT: punctuation
SCONJ: subordinating conjunction
SYM: symbol
VERB: verb
X: other


DEP
--------
dobj: direct object
pobj: object of preposition
det: determiner
prep: prepositional modifier
cc: coordinating conjunction
advmod: adverbial modifier
"""

order = ['dobj', 'pobj', 'dative']
possibilities = [
    ('grab', 'OBJECT'),
    ('grab', 'OBJECT', 'LOCATION'),
    ('grab', 'OBJECT', 'HUMAN'),
    ('grab', 'OBJECT', 'LOCATION', 'HUMAN'),
    ('put', 'OBJECT', 'LOCATION'),
    ('go', 'LOCATION'),
    ('detect', 'OBJECT'),
    ('detect', 'HUMAN'),
    #('say', 'dobj'),
    #('display', 'dobj'),
    #('play', 'dobj'),
]


def check_children(token: Token) -> List:
    children = []

    print(token)
    for child in token.children:
        if child.ent_type_ in ["ROBOT", "HUMAN", "LOCATION", "OBJECT"]:
            print(child.text, child.ent_type_)
            data = [child.lemma_, child.dep_, 1]

            for sub_child in child.children:
                if sub_child.dep_ == 'nummod' and sub_child.like_num:
                    data[2] = numerize(sub_child.text)

            children.append(data)

        children += check_children(child)

    return children


def handle_sentence(sentence: Span):
    root = None

    ner = NER_nlp(sentence.text_with_ws)
    entities = ner.ents

    print('\tWORDS')
    for token in sentence:
        print('\t', token.text, token.dep_, token.pos_, token.ent_type_ if token.ent_type_ != '' else '∅', token.head.text, [child for child in token.children])

        if token.dep_ == 'ROOT':
            root = token

    # ========
    print('\n\tPOSSIBILITIES')

    token_txt = root.lemma_
    for entity in entities:
        token_txt += f" {entity.text}"

    token_nlp = nlp(token_txt)
    print('\t', root, [(entity.text, entity.label_) for entity in entities], '>', token_txt)

    best_result = [0, None]

    for possibility in possibilities:
        possibility_txt = ' '.join(possibility)

        filled = 0

        for arg in possibility[1:]:
            for entity in entities:
                if arg == entity.label_:
                    possibility_txt = possibility_txt.replace(arg, entity.text)
                    filled += 1

        if filled != len(possibility) - 1:
            score = 0.00
        else:
            possibility_nlp = nlp(possibility_txt)
            score = round(possibility_nlp.similarity(token_nlp), 3)

        print('\t\t', score, '|', possibility_txt, '=', token_txt)

        if score >= best_result[0]:
            best_result = [score, possibility]

        """
        verb_nlp = nlp(possibility[0])
        possibility_nlp = nlp(' '.join(possibility))

        verb_score = round(verb_nlp.similarity(root), 3)
        possibility_score = round(possibility_nlp.similarity(token_nlp), 3)
        avg_score = round((verb_score + possibility_score) / 2, 3)
        
        print('\t\t·', avg_score, '|', verb_nlp, verb_score, '|', possibility_nlp, possibility_score)

        if avg_score >= best_result[0]:
            best_result = [avg_score, possibility]
        """

    # ========
    print('\n\tBEST RESULT')
    if best_result[0] < 0.45:
        print('\t> No solution found')
    else:
        print('\t>', best_result[0], ' '.join(best_result[1]))


def handle_doc(doc: Doc):
    for index, sentence in enumerate(doc.sents):
        print('- Sentence', index + 1, ':', sentence.text)
        handle_sentence(sentence)
        print()


def split_sentence_by_and(text: str) -> str:
    parts = text.split()

    for word_index in range(1, len(parts)-1):
        if parts[word_index] in ['and', 'or', 'then']:
            possible_verb = nlp(parts[word_index + 1])

            if possible_verb[0].pos_ == 'VERB':
                parts[word_index-1] += '.'
                del parts[word_index]

    final_text = ' '.join(parts)
    return final_text


if __name__ == '__main__':
    spacy.prefer_gpu()
    """
    'label_definitions': {
        'ROBOT': 'You as a general purpose service robot, e.g. you',
        'HUMAN': 'A person, e.g. me, him, John, her, Anna.',
        'LOCATION': 'A room in a house, e.g. kitchen, living-room, bathroom',
        'OBJECT': 'Any object that can be found in a house, e.g. pencil, apple, drink, phone',
    }
    """

    llm_config = {
        'task': {
            '@llm_tasks': 'spacy.NER.v3',
            'labels': ['ROBOT', 'HUMAN', 'LOCATION', 'OBJECT'],
        },
        'model': {
            '@llm_models': 'spacy.GPT-3-5.v1',
            'name': 'gpt-3.5-turbo'
        }
    }

    print('Loading model...')
    nlp = spacy.load('en_core_web_lg')  # en_core_web_lg
    NER_nlp = spacy.blank('en')
    NER_llm = NER_nlp.add_pipe("llm_ner", config=llm_config)
    NER_nlp.initialize()
    print('Model loaded!')

    print(NER_nlp.components)
    # Rule-based splitting, splits sentences on punctuation like . ! ?
    nlp.add_pipe('sentencizer')

    try:
        while True:
            print('------------------------')
            input_text = input('Enter a sentence: ')
            print()

            input_text = split_sentence_by_and(input_text)

            # Process text
            doc = nlp(input_text)

            handle_doc(doc)

    except KeyboardInterrupt:
        exit(0)
