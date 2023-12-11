from typing import List

import spacy
from numerizer import numerize
from spacy import Language
from spacy.tokens import Token
from spacy.tokens.doc import Doc
from spacy.tokens.span import Span

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
    ('grab', 'dobj'),
    ('grab', 'dobj', 'pobj'),
    ('grab', 'dobj', 'pobj', 'dative'),
    ('grab', 'dobj', 'dative'),
    ('put', 'dobj', 'pobj'),
    ('go', 'pobj'),
    ('detect', 'dobj'),
    ('detect', 'dative'),
    ('say', 'dobj'),
    ('display', 'dobj'),
    ('play', 'dobj'),
]


def check_children(token: Token) -> List:
    children = []
    for child in token.children:
        if child.dep_ in order:
            data = [child.text, child.dep_, 1]

            for sub_child in child.children:
                if sub_child.dep_ == 'nummod' and sub_child.like_num:
                    data[2] = numerize(sub_child.text)

            children.append(data)

        children += check_children(child)

    return children


def handle_sentence(sentence: Span):
    root = None

    print('\tWORDS')
    for token in sentence:
        print('\t', token.text, token.dep_, token.pos_, token.ent_type_ if token.ent_type_ != '' else '∅', token.head.text, [child for child in token.children])

        if token.dep_ == 'ROOT':
            root = token

    # ========
    print('\n\tPOSSIBILITIES')

    dependencies = check_children(root)
    dependencies = sorted(dependencies, key=lambda child: order.index(child[1]))

    token_txt = root.text
    for dependency in dependencies:
        token_txt += f" {dependency[0]}"

    token_nlp = nlp(token_txt)
    print('\t', root, dependencies, '>', token_txt)

    best_result = [0, None]

    for possibility in possibilities:
        possibility_txt = ' '.join(possibility)

        filled = 0

        for arg in possibility[1:]:
            for dep in dependencies:
                if arg == dep[1]:
                    possibility_txt = possibility_txt.replace(arg, dep[0])
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


@Language.component('split_and_or')
def set_custom_boundaries(doc: Doc):
    for token in doc[:-1]:
        if token.text == 'and' or token.text == 'or':
            doc[token.i + 1].is_sent_start = True
    return doc


if __name__ == '__main__':
    spacy.prefer_gpu()

    print('Loading model...')
    nlp = spacy.load('en_core_web_lg')  # en_core_web_lg
    print('Model loaded!')

    # Rule-based splitting, splits sentences on punctuation like . ! ?
    nlp.add_pipe('sentencizer')
    nlp.add_pipe('split_and_or', before='parser')

    try:
        while True:
            print('------------------------')
            text = input('Enter a sentence: ')
            print()

            # Process text
            doc = nlp(text)

            handle_doc(doc)

    except KeyboardInterrupt:
        exit(0)