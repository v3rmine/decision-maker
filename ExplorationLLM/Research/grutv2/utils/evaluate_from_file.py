
from pathlib import Path
import spacy.language
import pandas as pd 
from evaluator import Evaluator
from utils.compute_postprocessing_grounding import get_sentence_id, get_truth_entities_from_huric, update_names
from utils.enums import SRL_Input, SRL_Output, Language



def get_entities_from_text(text):
    entities = []

    if SRL_Input.FEATURE_SEPARATOR.value in text:
        entities = text.split(SRL_Input.FEATURE_SEPARATOR.value)[1]
        if SRL_Input.FEATURE_ELEMENT_SEPARATOR.value in entities:
            entities = [x.rstrip().lstrip() for x in entities.split(SRL_Input.FEATURE_ELEMENT_SEPARATOR.value)]
        else:
            entities = [entities]
    
    return entities


def restructure_object(truth_obj):
    output_obj = []

    truth_obj = list(truth_obj.values())[0]

    for k,v in truth_obj.items():
        
        if k != "sentence":
            frame = {
                "name": v['name'],
                "frameElements": []
            }

            for _,v1 in v['frame_elements'].items():
                frame_element = {
                    'found': v1['found'],
                    'in_text': v1['in_text'],
                    'name': v1['name'],
                    'tokens': v1['tokens'],
                    'values': v1['values'],
                    'argument': [v1['objectName']] if v1['in_text'] else [x['objectName'] for x in v1['values']]
                    }
                frame['frameElements'].append(frame_element)

            output_obj.append(frame)
    
    return output_obj


def get_e_name_for_gsrl(e_name, e_type, entities):

    for truth_entity in entities:
        if " is an instance of class " in truth_entity:
            # take classes of entities and check if they're equal
            e_type = e_type.upper()
            entity_class_truth = str(truth_entity).split(" is an instance of class ")[1].lstrip().rstrip().upper()

            if e_type == entity_class_truth:
                # take entity name from prediction (it has to be the same)
                entity_name_pred = str(truth_entity).split(" also known as ")[0].lstrip().rstrip()
                e_name = entity_name_pred
                return e_name


def get_gsrl(srl_object, entities):
    srl = ""

    for frame in srl_object:
        frame_string = frame["name"] + SRL_Output.FRAME_CONTAINER_START.value
        for j, frame_element in enumerate(frame["frameElements"]):
            arguments = frame_element['argument'][0]

            if frame_element["in_text"]:
                frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + SRL_Output.ARGUMENT_IN_TEXT_START.value + arguments + SRL_Output.ARGUMENT_IN_TEXT_END.value + SRL_Output.ARGUMENT_CONTAINER_END.value
            elif frame_element['tokens']:
                frame_element["in_text"] = False
                indexes, e_name = [9999], ""
                for e in frame_element['values']:
                    if int(indexes[0]) > int(e['tokens'][0]):
                        indexes = e['tokens']
                        e_name = e['objectName']
                        e_type = e['type']

                # search for e_name in entities
                e_name = get_e_name_for_gsrl(e_name, e_type, entities)

                # add here ee_name
                frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + e_name + SRL_Output.ARGUMENT_CONTAINER_END.value

            else:
                # empty frame element
                frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + SRL_Output.ARGUMENT_CONTAINER_END.value

            if j == 0:
                # add first argument
                frame_string += frame_element_string
            else:
                # concatenate argument with separator
                frame_string += SRL_Output.ARGUMENT_SEPARATOR.value + " " + frame_element_string
            
        frame_string += SRL_Output.FRAME_CONTAINER_END.value

        if srl == "":
            # add first frame
            srl = frame_string
        else:
            # concatenate frame with separator
            srl += " " + SRL_Output.FRAME_SEPARATOR.value + " " + frame_string
    
    return srl


def compute_truth(input_text, entityRetrievalType, lan: Language, nlp: spacy.language.Language = ""):
    sentence = input_text.split(SRL_Input.FEATURE_SEPARATOR.value)[0].lstrip().rstrip()
    print(f"COMPUTING TRUTH \t {sentence}")
    truth_entities, truth_obj = get_truth_entities_from_huric(sentence, lan)

    # need to parse truth obj
    truth_obj = restructure_object(truth_obj)
    # print(truth_obj)
    # quit()
    
    # check pred_entities and take entities name from there if exists
    # it is necessary for the book (b1) to have the same name both in truth and pred
    pred_entities = get_entities_from_text(input_text)
    truth_entities = update_names(truth_entities, pred_entities)

    # if "robot can you find a pack of napkins" in text:
    # print("truth_entities\n", truth_entities)
    # print("pred_entities\n", pred_entities)
    
    # truth = get_grounded_srl(truth_obj, truth_entities, entityRetrievalType, nlp, False)
    truth = get_gsrl(truth_obj, truth_entities)
    
    return truth


def compute_truth_and_evaluate_from_file(lan: Language, path="", grounding_type="full", filename="results_unified_recomputed_from_Huric.xlsx", entityRetrievalType = "STR", nlp: spacy.language.Language = ""):
    df = pd.read_excel(path + "/results_unified.xlsx")

    new_df = pd.DataFrame({
        "id": df['id'].tolist(),
        "input_text": df['input_text'].tolist(),
        "truth": ["" for _ in range(len(df.index))],
        "prediction": df['prediction'].tolist(),
        "totally correct": df['totally correct'].tolist(),
        "all frames correct": df['all frames correct'].tolist(),
        "frames_list": df['frames_list'].tolist(),
    })

    if grounding_type == "full":
        # compute truth in fullgrounding mode here
        # append it tu new_df['truth']
        ids = [get_sentence_id(x.split(SRL_Input.FEATURE_SEPARATOR.value)[0]) for x in new_df['input_text']]
        new_df['id'] = ids

        truths = [compute_truth(input_text, entityRetrievalType=entityRetrievalType, lan=lan, nlp=nlp) for input_text in new_df['input_text']]
        new_df['truth'] = truths

    else:
        raise Exception(f"ERROR: grounding_type {grounding_type} not supported. Accepted values are ['full'].")


    Path(path + "/recomputed").mkdir(parents=True, exist_ok=True)
    new_df.to_excel(path + "/recomputed/" + filename)

    # finally compute confusion matrix
    e = Evaluator("SRL")
    cm_frame, cm_frame_elements_span, cm_frame_elements_head = e.get_confusion_matrix(new_df['input_text'].tolist(), new_df['prediction'].tolist(), new_df['truth'].tolist())

    cm_frame.save_to_file(path + "/recomputed/cm_frame.txt")
    cm_frame_elements_span.save_to_file(path + "/recomputed/cm_frame_elements_span.txt")
    cm_frame_elements_head.save_to_file(path + "/recomputed/cm_frame_elements_head.txt")

    print("****************************************************")
    print("SAVED " + path + "/recomputed")