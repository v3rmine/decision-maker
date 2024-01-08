

from pathlib import Path
from typing import List
import pandas as pd
from evaluator import Evaluator
from huricParser import HuricParser
from utils.enums import Language, SRL_Input, SRL_Output
import spacy.language
from utils.files_utils import getAllFiles

from utils.parsing_utils import entity_in_sentence, from_srl_string_to_obj


def get_entity_name(entities, arguments, entityRetrievalType, lan: Language, nlp: spacy.language.Language = ""):
    entities_indexes = []
    
    # t8 also known as fridge or refrigerator is an instance of class FRIDGE
    # split_1 = ['t8', 'fridge or refrigerator is an instance of class FRIDGE']
    # entity_lrs = ['fridge', 'refrigerator']
    for entity_description in entities:
        entity_description = str(entity_description).lstrip().rstrip()
        try:
            split_1 = entity_description.split(" also known as ")
            if split_1 and isinstance(split_1, List) and len(split_1) > 1:
                # print(" also known as ")
                entity_lrs = split_1[1].split(" is an instance of class ")[0].split(" or ")
                # print('split(" is an instance of class ")[0].split(" or ")')
                for entity_lexical_reference in entity_lrs:
                    indexes = entity_in_sentence(entity_lexical_reference, arguments, lan, nlp, type=entityRetrievalType)
                    if indexes:
                        e_name = split_1[0]
                        # print('e_name')
                        entities_indexes.append([indexes, e_name])
        except IndexError:
            print("[ERROR][get_entity_name]: IndexError on split")
            print(entities)
            print(entity_description)
            print(arguments)
            quit()
    
    return entities_indexes


def get_grounded_srl(srl_object, entities, entityRetrievalType, lan: Language, nlp: spacy.language.Language = "", toPrint: bool = False):
    srl = ""

    for frame in srl_object:
        frame_string = frame["name"] + SRL_Output.FRAME_CONTAINER_START.value
        for j, frame_element in enumerate(frame["frameElements"]):
            arguments = frame_element['argument'][0]

            entities_indexes = get_entity_name(entities, arguments, entityRetrievalType, lan, nlp)

            if toPrint:
                print("entities_indexes")
                print(entities_indexes)
                print("************************************************************************")
                print("arguments")
                print(arguments)
                print("************************************************************************")

            if entities_indexes:
                frame_element["in_text"] = False
                indexes, e_name = [9999], ""
                for e in entities_indexes:
                    if int(indexes[0]) > int(e[0][0]):
                        indexes = e[0]
                        e_name = e[1]

                # add here ee_name
                frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + e_name + SRL_Output.ARGUMENT_CONTAINER_END.value
                
            elif frame_element["in_text"]:
                frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + SRL_Output.ARGUMENT_IN_TEXT_START.value + arguments + SRL_Output.ARGUMENT_IN_TEXT_END.value + SRL_Output.ARGUMENT_CONTAINER_END.value
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


def get_sentence_id(text, lan: Language):
    text = text.rstrip().lstrip()
    text_id = ""
    df = pd.read_csv("./data/huric_sentences_" + lan.value + ".csv")
    try:
        text_id = df.loc[df['sentence'] == text]['id'].values[0]
    except IndexError:
        print("[ERROR][get_sentence_id]: IndexError values[0]")
        print(text)
        print(df.loc[df['sentence'] == text])
        quit()
    return text_id


def get_truth_entities_from_huric(text, lan: Language):
    entities = []

    text_id = get_sentence_id(text, lan)
    if text_id != "":
        # loop through huric files
        files = getAllFiles("./data/huric/en")
        for file in files:
            if str(text_id) in file:
                hp = HuricParser(Language.ENGLISH)
                [_, sentence, _], srl = hp.parseHuricFile(file, "SRL", "SRL", True, False, "lmd", False, "full", "W2V", lan, "all")
                if SRL_Input.FEATURE_SEPARATOR.value in sentence:
                    entities = sentence.split(SRL_Input.FEATURE_SEPARATOR.value)
                    if SRL_Input.FEATURE_ELEMENT_SEPARATOR.value in sentence:
                        entities = entities[1].split(SRL_Input.FEATURE_ELEMENT_SEPARATOR.value)
                    else:
                        entities = [entities[1]]
                break

    return [x.lstrip().rstrip() for x in entities], srl


def update_names(truth_entities, pred_entities):
    final_entitites = []

    for truth_entity_description in truth_entities:
        new_entity_description = ""
        for pred_entity_description in pred_entities:
            if " is an instance of class " in pred_entity_description:
                # take classes of entities and check if they're equal
                entity_class_truth = str(truth_entity_description).split(" is an instance of class ")[1].lstrip().rstrip().upper()
                entity_class_pred = str(pred_entity_description).split(" is an instance of class ")[1].lstrip().rstrip().upper()
            
                if entity_class_truth == entity_class_pred:
                    # take entity name from prediction (it has to be the same)
                    entity_name_pred = str(pred_entity_description).split(" also known as ")[0].lstrip().rstrip()
                    # take entity descr from truth since it's the most right one
                    entity_descr_truth = str(pred_entity_description).split(" also known as ")[1].lstrip().rstrip()
                    # put them together and append to the final list
                    new_entity_description = entity_name_pred + " also known as " + entity_descr_truth
                    break
        if new_entity_description == "":
            # if not found, append the truth computed one
            new_entity_description = truth_entity_description
        final_entitites.append(new_entity_description)
    return final_entitites


def compute_postprocessing_grounding(lan: Language, results_unified_filepath: str = "./model/2022_07_19/bart_halfgrounding", entityRetrievalType: str = "STR", nlp: spacy.language.Language = ""):
    if "halfgrounding" not in results_unified_filepath and "halfgr" not in results_unified_filepath:
        print("WARNING: filepath does NOT contain 'halfgrounding'. This method is supposed to take results from 'halfgrounding' models!")
    # read results of hg
    df = pd.read_excel(results_unified_filepath + "/results_unified.xlsx")

    index = 0
    input_text, truths, predictions, totally_correct_list, all_frames_correct_list, truth_entities_list, pred_entities_list = [], [], [], [], [], [], []
    for text, truth, pred, totally_correct, all_frames_correct in zip(df['input_text'].tolist(), df['truth'].tolist(), df['prediction'].tolist(), df['totally correct'].tolist(), df['all frames correct'].tolist()):
        toLog = False
        if index != 0 and index % 100 == 0:
            print("********************", results_unified_filepath, "index", index, "********************")
        index += 1

        truth_obj = from_srl_string_to_obj(truth)
        pred_obj = from_srl_string_to_obj(pred)

        # if "robot can you find a pack of napkins" in text:
        #     print("truth_obj\n", truth_obj)
        #     print("pred_obj\n", pred_obj)
        #     toLog = True

        # correctness is the same
        totally_correct_list.append(totally_correct)
        all_frames_correct_list.append(all_frames_correct)
        
        try:
            # "testo testo # fn1"
            if SRL_Input.FEATURE_SEPARATOR.value in text:
                pred_entities = text.split(SRL_Input.FEATURE_SEPARATOR.value)
                if SRL_Input.FEATURE_ELEMENT_SEPARATOR.value in text:
                    pred_entities = pred_entities[1].split(SRL_Input.FEATURE_ELEMENT_SEPARATOR.value)
                else:
                    pred_entities = [pred_entities[1]]
            else:
                pred_entities = ["NOMAP"]

            pred_entities = [x.lstrip().rstrip() for x in pred_entities]
            pred_entities_list.append(pred_entities)
        except IndexError:
            print("[ERROR][compute_postprocessing_grounding]\tIndexError on split")
            print(text)
            quit()


        if pred_entities and pred_entities != ["NOMAP"]:
            # if pred_entities => compute here description to put in lists
            pred_description = get_grounded_srl(pred_obj, pred_entities, entityRetrievalType, lan, nlp, toLog)
            predictions.append(pred_description)
        else:
            # there are no entities to check
            # just add back pred
            predictions.append(pred)

        
        truth_entities, _ = get_truth_entities_from_huric(text.split(SRL_Input.FEATURE_SEPARATOR.value)[0].lstrip().rstrip(), lan)
        
        # if "robot can you find a pack of napkins" in text:
        #     print("truth_entities\n", truth_entities)
        #     print("pred_entities\n", pred_entities)
            

        # check pred_entities and take entities name from there if exists
        # it is necessary that entities names (e1) corresponds between truth and pred
        truth_entities = update_names(truth_entities, pred_entities)

        truth_entities_list.append(truth_entities)
        if truth_entities and truth_entities != ["NOMAP"]:
            truth_description = get_grounded_srl(truth_obj, truth_entities, "W2V", lan, nlp, toLog)
            truths.append(truth_description)
        else:
            # there are no entities to check
            # just add back truth
            truths.append(truth)

        # if "robot can you find a pack of napkins" in text:
        #     print("truth_entities AFTER updateding names\n", truth_entities)
        #     print("truth SRL after\n", truth_description)
        #     quit()
        
        
        # no need to modify text
        input_text.append(text)


    new_df = pd.DataFrame({
        "input_text": input_text, 
        "truths": df['truth'].tolist(),
        "grounded_truths": truths,
        "truth_entities": truth_entities_list,
        "predictions": df['prediction'].tolist(),
        "grounded_predictions": predictions,
        "pred_entities": pred_entities_list,
        "totally_correct": totally_correct_list, 
        "all_frames_correct": all_frames_correct_list
    })

    Path(results_unified_filepath + "/postgrounding").mkdir(parents=True, exist_ok=True)

    new_df.to_excel(results_unified_filepath + "/postgrounding/results_unified.xlsx")

    # finally compute confusion matrix
    e = Evaluator("SRL")
    cm_frame, cm_frame_elements_span, cm_frame_elements_head = e.get_confusion_matrix(input_text, predictions, truths)

    cm_frame.save_to_file(results_unified_filepath + "/postgrounding/cm_frame.txt")
    cm_frame_elements_span.save_to_file(results_unified_filepath + "/postgrounding/cm_frame_elements_span.txt")
    cm_frame_elements_head.save_to_file(results_unified_filepath + "/postgrounding/cm_frame_elements_head.txt")

    print("****************************************************")
    print("SAVED " + results_unified_filepath + "/postgrounding")