import spacy
from termcolor import colored

from constants import GOALS
from llm import generate_ner_config, generate_rel_config, generate_textcat_config
from memory import Memory
from parse_ontology import parseOntologyConfig

memory = Memory()

if __name__ == '__main__':
    """
    
        ONTOLOGY
    
    """

    memory.ontology = parseOntologyConfig('ontology_v2.toml')

    print()

    """
    
        SPACY CONFIG
    
    """

    spacy.prefer_gpu()

    print('Loading model...')
    nlp = spacy.load('en_core_web_lg')  # en_core_web_lg
    print('Model loaded!')

    # Named Entity Recognition
    ner_labels = memory.ontology.NER_labels
    ner_config = generate_ner_config(labels=ner_labels)
    ner_llm = nlp.add_pipe('llm_ner', config=ner_config)

    # Relation extraction
    rel_relations = memory.ontology.REL_relations
    rel_config = generate_rel_config(labels=rel_relations)
    rel_llm = nlp.add_pipe('llm_rel', config=rel_config)

    # Text Categorizer
    textcat_labels = [goal.name for goal in GOALS]
    textcat_config = generate_textcat_config(labels=textcat_labels)
    textcat_llm = nlp.add_pipe('llm_textcat', config=textcat_config)

    # Rule-based sentence splitting on punctuation e.g. . ! ?
    nlp.add_pipe('sentencizer')

    """
    
        MAIN LOOP
    
    """

    try:
        while True:
            print('------------------------')
            input_text = input('Enter a sentence: ')
            print()

            # Process text
            doc = nlp(input_text)

            # === ENTITIES ===

            print(colored('ENTITIES', attrs=['underline']))

            memory.entities = list(doc.ents)
            memory.print_entities()

            # === RELATIONS ===

            print(colored('RELATIONS', attrs=['underline']))

            candidate_relations = doc._.rel
            memory.select_relations(candidate_relations=candidate_relations)

            print()

            # === GOAL ===

            print(colored('GOALS', attrs=['underline']))

            candidate_goals = doc.cats
            memory.select_goals(candidate_goals=candidate_goals)

            # === NLP ===

            print(colored('\nWORDS', attrs=['underline']))

            for token in doc:
                print('\t', colored(token.text, attrs=['bold']), '\t|', token.dep_, token.pos_,
                      token.ent_type_ if token.ent_type_ != '' else '∅',
                      token.head.text, [child for child in token.children])

            # === FILL TASK MEMORY STACK AND TASK LIST ===

            print(colored('\nTASKS', attrs=['underline']))
            memory.fill_answers_and_memory_stack()

            print(colored('\nMEMORY STACK', attrs=['underline']))
            memory.print_memory_stack()

            print()

            # === EXECUTE TASK PIPELINE ===

            print(colored('TASK PIPELINE', attrs=['underline']))
            memory.execute_pipeline()

    except KeyboardInterrupt:
        exit(0)
