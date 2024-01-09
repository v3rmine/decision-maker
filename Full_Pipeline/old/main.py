import spacy

from NLP import split_sentence_by_and, handle_doc
from parse_ontology import parseOntologyConfig

if __name__ == '__main__':

    # ===== ONTOLOGY =====

    ontology = parseOntologyConfig('ontology_v2.toml')
    entity_as_labels = [entity.upper() for entity in ontology.entities.keys()]

    ner_config = {
        'task': {
            '@llm_tasks': 'spacy.NER.v3',
            'labels': ['COLOR', 'AGE', 'WEIGHT'] + entity_as_labels,
            'label_definitions': {
                'ROBOT': 'You as a general purpose service robot, e.g. you',
                'HUMAN': 'A person, e.g. me, him, John, her, Anna.',
                'LOCATION': 'A room in a house, e.g. kitchen, living-room, bathroom',
                'OBJECT': 'Any object that can be found in a house, e.g. pencil, apple, drink, phone',
            }
        },
        'model': {
            '@llm_models': 'spacy.GPT-3-5.v2',
            'name': 'gpt-3.5-turbo',
            'config': {'temperature': 0.0}
        }
    }

    rel_config = {
        'task': {
            '@llm_tasks': 'spacy.REL.v1',
            'labels': ['FurnitureHasColor', 'HumanHasAge', 'ObjectHasWeight'],
        },
        'model': {
            '@llm_models': 'spacy.GPT-3-5.v2',
            'name': 'gpt-3.5-turbo',
            'config': {'temperature': 0.0}
        }
    }

    # ===== SPACY =====

    spacy.prefer_gpu()

    print('Loading model...')
    nlp = spacy.load('en_core_web_lg')  # en_core_web_lg
    print('Model loaded!')

    ner_llm = nlp.add_pipe('llm_ner', config=ner_config)
    rel_llm = nlp.add_pipe('llm_rel', config=rel_config)

    # Rule-based splitting, splits sentences on punctuation like . ! ?
    nlp.add_pipe('sentencizer')

    try:
        while True:
            print('------------------------')
            input_text = input('Enter a sentence: ')
            print()

            input_text = split_sentence_by_and(input_text, nlp)

            # Process text
            doc = nlp(input_text)

            handle_doc(doc, nlp)

    except KeyboardInterrupt:
        exit(0)
