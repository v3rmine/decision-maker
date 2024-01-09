import re
from typing import List, Sequence

from spacy import Language
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span
from spacy_llm.tasks.rel import RelationItem

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
goals = [
    ('grab', 'OBJECT'),
    ('grab', 'OBJECT', 'LOCATION'),
    ('grab', 'OBJECT', 'HUMAN'),
    ('grab', 'OBJECT', 'LOCATION', 'HUMAN'),
    ('put', 'OBJECT', 'LOCATION'),
    ('go', 'LOCATION'),
    ('detect', 'OBJECT'),
    ('detect', 'HUMAN'),
    # ('say', 'dobj'),
    # ('display', 'dobj'),
    # ('play', 'dobj'),
]

"""
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
"""
excluded_words = []


def entity_to_text(entity: Span) -> str:
    text = ''
    for sub_entity in entity.subtree:
        if sub_entity.text_with_ws not in excluded_words:
            text += sub_entity.text_with_ws

    return text


def handle_sentence(sentence: Span, entities: Sequence[Span], relations: List[RelationItem], nlp: Language):
    root = None

    # For every relation between entities
    for relation in relations:
        # If the relation points to itself it means that an adjective what omitted in entity labelling
        if relation.dep == relation.dest:
            # Goes through every word of the destination entity
            for word in entities[relation.dest]:
                # If a word in this entity is an adjective
                if word.pos_ == 'ADJ':
                    # Extract the second part of the relation
                    relation_regex = re.match(r'^\w+Has(\w+)$', relation.relation)
                    dep_entity_label = relation_regex.groups()[0].upper()
                    # Affect the new entity
                    sentence[word.i].ent_type_ = dep_entity_label

                    # new_entity_text = entities[relation.dest].text.replace(word.text_with_ws, '')

                    excluded_words.append(word.text_with_ws)
                    break

    print('\tWORDS')
    for token in sentence:
        print('\t', token.text, token.dep_, token.pos_, token.ent_type_ if token.ent_type_ != '' else '∅',
              token.head.text, [child for child in token.children])

        if token.dep_ == 'ROOT':
            root = token

    # ========
    print('\n\tPOSSIBILITIES')

    token_txt = root.lemma_
    for entity in entities:
        token_txt += f" {entity_to_text(entity)}"

    token_nlp = nlp(token_txt)
    print('\t', root, [(entity_to_text(entity), entity.label_) for entity in entities], '>', token_txt)

    best_result = [0, None]

    for goal in goals:
        possibility_txt = ' '.join(goal)

        filled = 0

        for arg in goal[1:]:
            for entity in entities:
                if arg == entity.label_:
                    possibility_txt = possibility_txt.replace(arg, entity_to_text(entity))
                    filled += 1

        if filled != len(goal) - 1:
            score = 0.00
        else:
            possibility_nlp = nlp(possibility_txt)
            score = round(possibility_nlp.similarity(token_nlp), 3)

        print('\t\t', score, '|', possibility_txt, '=', token_txt)

        if score >= best_result[0]:
            best_result = [score, goal]

    # ========
    print('\n\tBEST RESULT')
    if best_result[0] < 0.45:
        print('\t> No solution found')
    else:
        print('\t>', best_result[0], ' '.join(best_result[1]))


def handle_doc(doc: Doc, nlp: Language):
    for index, sentence in enumerate(doc.sents):
        print('- Sentence', index + 1, ':', sentence.text)
        handle_sentence(sentence, doc.ents, doc._.rel, nlp)
        print()


def split_sentence_by_and(text: str, nlp: Language) -> str:
    parts = text.split()

    for word_index in range(1, len(parts) - 1):
        if parts[word_index] in ['and', 'or', 'then']:
            possible_verb = nlp(parts[word_index + 1])

            if possible_verb[0].pos_ == 'VERB':
                parts[word_index - 1] += '.'
                del parts[word_index]

    final_text = ' '.join(parts)
    return final_text
