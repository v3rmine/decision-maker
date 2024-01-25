#!/usr/bin/env -S poetry run python3
import spacy
from termcolor import colored

from constants import BASE_GOALS
from llm import generate_ner_config, generate_rel_config, generate_textcat_config
from memory import Memory
from parse_ontology import parseOntologyConfig
import argparse
import stt

if __name__ == '__main__':
    """
    
        ONTOLOGY
    
    """

    # Parse the ontology file
    ontology = parseOntologyConfig('ontology_v2.toml')

    # Contains all the data needed to process the NLP (NER, REL and TEXTCAT) results
    memory = Memory(ontology)

    print()

    """
    
        SPACY CONFIG
    
    """

    spacy.prefer_gpu()

    print('Loading model...')
    nlp = spacy.load('en_core_web_lg')  # en_core_web_lg
    print('Model loaded!')

    # === NER: Named Entity Recognition ===
    # Retrieve NER labels from the ontology
    ner_labels = memory.ontology.NER_labels
    # Generate the NER configuration dict
    ner_config = generate_ner_config(labels=ner_labels)
    # Add the NER to the NLP pipeline
    ner_llm = nlp.add_pipe('llm_ner', config=ner_config)

    # === REL: Relation Extraction ===
    # Retrieve REL labels from the ontology
    rel_relations = memory.ontology.REL_relations
    # Generate the REL configuration dict
    rel_config = generate_rel_config(labels=rel_relations)
    # Add the REL to the NLP pipeline
    rel_llm = nlp.add_pipe('llm_rel', config=rel_config)

    # === TEXTCAT: Text Categorizer ===
    # Retrieve TEXTCAT labels from the goals
    textcat_labels = [goal.name for goal in BASE_GOALS]
    # Generate the TEXTCAT configuration dict
    textcat_config = generate_textcat_config(labels=textcat_labels)
    # Add the TEXTCAT to the NLP pipeline
    textcat_llm = nlp.add_pipe('llm_textcat', config=textcat_config)

    # Rule-based sentence splitting on punctuation e.g. . ! ?
    nlp.add_pipe('sentencizer')

    """
    
        MAIN LOOP
    
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--record", help="Get the input with mic", action='store_true')
    args = parser.parse_args()

    try:
        # while True:
            print('================================================')
            if args.record:
                input_text = stt.rec()
                print(input_text)
            else:
                input_text = input('Enter a sentence: ')
            print()

            # Process the text with NLP
            doc = nlp(input_text)

            # === ENTITIES ===

            print(colored('ENTITIES', attrs=['underline']))

            # Retrieve entities from the NLP
            memory.entities = list(doc.ents)
            memory.print_entities()

            # === RELATIONS ===

            print(colored('RELATIONS', attrs=['underline']))

            # Retrieve entity relations from the NLP
            candidate_relations = list(doc._.rel)

            # Add to memory the relations that are validated
            memory.select_relations(candidate_relations=candidate_relations)

            print()

            # === GOAL ===

            print(colored('GOALS', attrs=['underline']))

            # Retrieve textcats from the NLP
            candidate_goals = doc.cats

            # Add to memory the goals that are validated
            memory.select_goals(candidate_goals=candidate_goals)

            # === NLP ===

            print(colored('\nWORDS', attrs=['underline']))

            for token in doc:
                # Print various information about the sentence
                print('\t', colored(token.text, attrs=['bold']), '\t|', token.dep_, token.pos_, token.ent_type_ if token.ent_type_ != '' else '∅', token.head.text, [child for child in token.children])

            # === FILL TASK MEMORY STACK AND TASK LIST ===

            print(colored('\nTASKS', attrs=['underline']))
            memory.fill_answers_and_memory_stack()

            print(colored('\nMEMORY STACK', attrs=['underline']))
            memory.print_memory_stack()

            print()

            # === EXECUTE TASK PIPELINE ===

            print(colored('TASK PIPELINE', attrs=['underline']))
            memory.execute_pipeline()

            # Reset the memory
            memory.reset()

    except KeyboardInterrupt:
        exit(0)
