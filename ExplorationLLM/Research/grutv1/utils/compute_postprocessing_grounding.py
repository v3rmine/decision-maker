

import pandas as pd
from evaluator import Evaluator
from utils.enums import SRL_Output

from utils.parsing_utils import entity_in_sentence, from_srl_string_to_obj


def get_entity_name(entities, arguments):
    entities_indexes = []
    
    for entity_description in entities:
        split_1 = entity_description.split(" also known as ")
        entity_lrs = split_1[1].split(" is an instance of class ")[0].split(" or ")
        for entity_lexical_reference in entity_lrs:
            indexes = entity_in_sentence(entity_lexical_reference, arguments)
            if indexes:
                e_name = split_1[0]
                entities_indexes.append([indexes, e_name])
    
    return entities_indexes


def get_grounded_srl(srl_object, entities):
    srl = ""

    for frame in srl_object:
        frame_string = frame["name"] + SRL_Output.FRAME_CONTAINER_START.value
        for j, frame_element in enumerate(frame["frameElements"]):
            arguments = frame_element['argument'][0]

            entities_indexes = get_entity_name(entities, arguments)
            # print("entities_indexes")
            # print(entities_indexes)
            # print("************************************************************************")
            # print("arguments")
            # print(arguments)
            # print("************************************************************************")

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


def compute_postprocessing_grounding():

    # read results of hg
    df = pd.read_excel("./model/2022_07_19/bart_halfgrounding/results_unified.xlsx")

    input_text, truths, predictions, totally_correct_list, all_frames_correct_list = [], [], [], [], []
    for text, truth, pred, totally_correct, all_frames_correct in zip(df['input_text'].tolist(), df['truth'].tolist(), df['prediction'].tolist(), df['totally correct'].tolist(), df['all frames correct'].tolist()):
        truth_obj = from_srl_string_to_obj(truth)
        pred_obj = from_srl_string_to_obj(pred)
        entities = text.split(" # ")[1].split(" & ")

        # correctness still remains the same
        totally_correct_list.append(totally_correct)
        all_frames_correct_list.append(all_frames_correct)

        if entities != ["NOMAP"]:
            # if entities => compute here description to put in lists
            truth_description = get_grounded_srl(truth_obj, entities)
            truths.append(truth_description)
            pred_description = get_grounded_srl(pred_obj, entities)
            predictions.append(pred_description)

            # no need to modify text
            input_text.append(text)
        else:
            # there are no entities to check
            # just add back text/truth/pred
            input_text.append(text)
            truths.append(truth)
            predictions.append(pred)

    new_df = pd.DataFrame({
        "input_text": input_text, 
        "truths": df['truth'].tolist(),
        "grounded_truths": truths,
        "predictions": df['prediction'].tolist(),
        "grounded_predictions": predictions,
        "totally_correct": totally_correct_list, 
        "all_frames_correct": all_frames_correct_list
    })
    new_df.to_excel("./model/2022_07_19/bart_halfgrounding_grounded_baseline/results_unified.xlsx")
    # finally compute confusion matrix
    e = Evaluator("SRL")
    cm_frame, cm_frame_elements_span, cm_frame_elements_head = e.get_confusion_matrix(input_text, predictions, truths)
    # hopefully is lower than fg/fg_lutypes
    cm_frame.save_to_file("./model/2022_07_19/bart_halfgrounding_grounded_baseline/cm_frame.txt")
    cm_frame_elements_span.save_to_file("./model/2022_07_19/bart_halfgrounding_grounded_baseline/cm_frame_elements_span.txt")
    cm_frame_elements_head.save_to_file("./model/2022_07_19/bart_halfgrounding_grounded_baseline/cm_frame_elements_head.txt")