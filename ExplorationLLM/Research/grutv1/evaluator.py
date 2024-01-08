
from typing import List
from itertools import zip_longest
from utils.confusion_matrix import ConfusionMatrix
from utils.enums import SRL_Input, SRL_Output
from utils.parsing_utils import from_srl_string_to_obj

class Evaluator:
    def __init__(self, type) -> None:
        self.type = type

    def get_confusion_matrix(self, texts: List[str], predictions: List[str], truths: List[str]):
        
        if self.type == "SRL":
            return self.get_confusion_matrix_srl(texts, predictions, truths)
        elif self.type == "FP + E2E":
            return self.get_confusion_matrix_fp_e2e(texts, predictions, truths)
    
    
    def get_confusion_matrix_fp_e2e(self, texts, predictions, truths):

        print("Calculating Confusion Matrix for " + str(len(texts)) + " elements. Type: " + self.type)
        fp_cm = self.get_confusion_matrix_frames_only(texts, predictions, truths)
        e2e_cm = ConfusionMatrix()

        e2e_pred_examples_list = []
        e2e_truth_examples_list = []
        for text, prediction, truth in zip(texts, predictions, truths):
            text = text.split(" " + SRL_Input.FEATURE_SEPARATOR.value + " ")[0]
            prediction_obj_list = from_srl_string_to_obj(prediction)
            truth_obj_list = from_srl_string_to_obj(truth)

            e2e_pred_examples = []
            e2e_truth_examples = []
            for pred_frame_obj, truth_frame_obj in zip_longest(prediction_obj_list, truth_obj_list, fillvalue={}):
                
                if 'frameElements' in pred_frame_obj:
                    for fe in pred_frame_obj['frameElements']:
                        for argument in fe['argument']:
                            e2e_pred_examples.append(pred_frame_obj['name'] + "_" + fe['name'] + "_" + argument.replace(SRL_Output.ARGUMENT_IN_TEXT_START.value, "").replace(SRL_Output.ARGUMENT_IN_TEXT_END.value, ""))
                else:
                    print(f"No frame elements PREDICTED for {text}")

                if 'frameElements' in truth_frame_obj:
                    for fe in truth_frame_obj['frameElements']:
                        for argument in fe['argument']:
                            e2e_truth_examples.append(truth_frame_obj['name'] + "_" + fe['name'] + "_" + argument.replace(SRL_Output.ARGUMENT_IN_TEXT_START.value, "").replace(SRL_Output.ARGUMENT_IN_TEXT_END.value, ""))
                else:
                    print(f"No frame elements TRUTH for {text}")
            
            e2e_pred_examples_list.append(e2e_pred_examples)
            e2e_truth_examples_list.append(e2e_truth_examples)

        e2e_cm = self.compute_e2e_cm(e2e_pred_examples_list, e2e_truth_examples_list)

        # TODO replace None with cm for e2e considering only the semantic head for the element
        return fp_cm, e2e_cm, ConfusionMatrix()


    def compute_e2e_cm(self, predictions, truths):
        cm = ConfusionMatrix()

        for predictions_list, truths_list in zip(predictions, truths):
            for truth in truths_list:
                if truth in predictions_list:
                    cm.tp +=1
                else:
                    cm.fn +=1

            for pred in predictions_list:
                if not (pred in truths_list):
                    cm.fp +=1
        return cm

    def get_confusion_matrix_frame(self, texts: List[str], predictions: List[str], truths: List[str]):
        print("Calculating Confusion Matrix for " + str(len(texts)) + " elements. Type: " + self.type)
        cm = ConfusionMatrix()

        for text, prediction, truth in zip(texts, predictions, truths):
            text_list = text.split(" # ")[0].split(" ")
            predictions_list, truths_list = self.get_lists_from_frame(prediction, truth)
            current_tot = 0

            for truth in truths_list:
                if truth in predictions_list:
                    cm.tp +=1
                    current_tot += 1
                else:
                    cm.fn +=1
                    current_tot += 1

            for pred in predictions_list:
                if not (pred in truths_list) and pred != "_":
                    cm.fp +=1
                    current_tot += 1
            
            cm.tn += max(len(text_list) - current_tot, 0)

        return cm

    def get_lists_from_frame(self, prediction: str, truth: str):
        predicted_frames = prediction.split(" " + SRL_Output.FRAME_SEPARATOR.value + " ")
        truth_frames = truth.split(" " + SRL_Output.FRAME_SEPARATOR.value + " ")

        predicted_frames_output = []
        truth_frames_output = []

        for predicted_frame, truth_frame in zip_longest(predicted_frames, truth_frames, fillvalue="_"):
            predicted_frames_output.append(predicted_frame)
            truth_frames_output.append(truth_frame)

        return predicted_frames_output, truth_frames_output


    def get_confusion_matrix_srl(self, texts: List[str], predictions: List[str], truths: List[str]):
        print("Calculating Confusion Matrix for " + str(len(texts)) + " elements. Type: " + self.type)
        cm_frame = ConfusionMatrix()
        cm_frame_elements_span = ConfusionMatrix()
        cm_frame_elements_head = ConfusionMatrix()

        preds_frames_list = []
        truth_frames_list = []   
        prediction_fes_span_list = []
        truth_fes_span_list = []
        prediction_fes_head_list = []
        truth_fes_head_list = []

        for text, prediction, truth in zip(texts, predictions, truths):
            prediction_list = from_srl_string_to_obj(prediction)
            truth_list = from_srl_string_to_obj(truth)
            prediction_frames = ""
            truth_frames = ""
            prediction_fes_span = []
            prediction_fes_head = []
            truth_fes_span = []
            truth_fes_head = []

            for pred, truth in zip_longest(prediction_list, truth_list, fillvalue={}):

                if pred:
                    if prediction_frames != "":
                        prediction_frames += " " + SRL_Output.FRAME_SEPARATOR.value + " " + pred['name']
                    else:
                        prediction_frames = pred['name']

                    for fe in pred['frameElements']:
                        if fe['in_text']:
    
                            # split text for semantic head evaluation
                            args = fe['argument'][0].split(" ")
                            for arg in args:
                                prediction_fes_head.append(fe['name'] + "_" + arg)
                            
                            # merge args back with _ for whole span evaluation
                            prediction_fes_span.append(fe['name'] + "_" + "_".join(args))
                        else:
                            
                            # add every arg alone for semantic head evaluation
                            for arg in fe['argument']:
                                prediction_fes_head.append(fe['name'] + "_" + arg)
                            
                            # merge args back with _ for whole span evaluation
                            prediction_fes_span.append(fe['name'] + "_" + "_".join(fe['argument']))
                if truth:
                    if truth_frames != "":
                        truth_frames += " " + SRL_Output.FRAME_SEPARATOR.value + " " + truth['name']
                    else:
                        truth_frames = truth['name']
                    
                    for fe in truth['frameElements']:
                        if fe['in_text']:

                            # split text for semantic head evaluation
                            args = fe['argument'][0].split(" ")
                            for arg in args:
                                truth_fes_head.append(fe['name'] + "_" + arg)
                            
                            # merge args back with _ for whole span evaluation
                            truth_fes_span.append(fe['name'] + "_" + "_".join(args))
                        else:
                            
                            # add every arg alone for semantic head evaluation
                            for arg in fe['argument']:
                                truth_fes_head.append(fe['name'] + "_" + arg)
                            
                            # merge args back with _ for whole span evaluation
                            truth_fes_span.append(fe['name'] + "_" + "_".join(fe['argument']))


            preds_frames_list.append(prediction_frames)
            truth_frames_list.append(truth_frames)
            prediction_fes_span_list.append(prediction_fes_span)
            truth_fes_span_list.append(truth_fes_span)
            prediction_fes_head_list.append(prediction_fes_head)
            truth_fes_head_list.append(truth_fes_head)

        cm_frame = self.get_confusion_matrix_frame(texts, preds_frames_list, truth_frames_list)
        cm_frame_elements_span = self.get_confusion_matrix_frame_elements_span(prediction_fes_span_list, truth_fes_span_list)
        cm_frame_elements_head = self.get_confusion_matrix_frame_elements_head(prediction_fes_head_list, truth_fes_head_list)
        
        # print(truth_frames_list)
        # print(preds_frames_list)
        # print(truth_fes_list)
        # print(prediction_fes_list)

        # for id, text, prediction, truth in zip(ids, texts, predictions, truths):
        #     #convert srl format to obj of frame and frame elements
        #     prediction_list = from_srl_string_to_obj(prediction)
        #     truth_list = from_srl_string_to_obj(truth)
        #     #convert srl format to list of "_" and list of tokens
        #     prediction_list_frame_elements = self.from_srl_to_frame_elements(text, prediction_list, dict_huric[str(id)])
        #     truth_list_frame_elements = self.from_srl_to_frame_elements(text, truth_list, dict_huric[str(id)])
            
        #     for elem_pred, elem_truth in zip(prediction_list_frame_elements, truth_list_frame_elements):
        #         if elem_truth == "_":
        #             if elem_truth == elem_pred:
        #                 cm_frame_elements.tn += 1
        #             else:
        #                 cm_frame_elements.fp += len(elem_pred)
        #         else:
        #             if elem_pred == "_":
        #                 cm_frame_elements.fn += len(elem_truth)
        #             else: #elem_truth and elem_pred != "_"
        #                 for e_t in elem_truth:
        #                     if e_t in elem_pred:
        #                         cm_frame_elements.tp += 1
        #                         elem_truth.remove(e_t)
        #                         elem_pred.remove(e_t)

        #                 if len(elem_truth) >= len(elem_pred):
        #                     cm_frame_elements.fn += len(elem_truth) - len(elem_pred)
        #                     cm_frame_elements.fp += len(elem_pred)
        #                 else:
        #                     cm_frame_elements.fp += len(elem_pred)

        return cm_frame, cm_frame_elements_span, cm_frame_elements_head

    # [['Goal_entity:v', 'Theme_entity:x', 'Goal_testo', 'Goal_asd']]
    # [['Goal_entity:v', 'Theme_entity:x', 'Goal_tesdfsto', 'Goal_assd']]
    def get_confusion_matrix_frame_elements_head(self, prediction_fes_list, truth_fes_list):
        cm = ConfusionMatrix()

        for pred_fes, truth_fes in zip_longest(prediction_fes_list, truth_fes_list, fillvalue=[]):
            checked_fes = {}

            for truth in truth_fes:
                fe = truth.split("_")[0]
                checked_fes.setdefault(fe, False)

                # 1 word with the correct argument is sufficient to be tp
                if truth in pred_fes and not checked_fes[fe]:
                    cm.tp += 1
                    checked_fes[fe] = True
            
            # if there are fes such that no words were contained in pred, add 1 fn for every fe
            for _, v in checked_fes.items():
                if not v:
                    cm.fn += 1
                    
            checked_fes = {}
            for pred in pred_fes:
                fe = pred.split("_")[0]
                checked_fes.setdefault(fe, False)
                if pred in truth_fes and not checked_fes[fe]:
                    checked_fes[fe] = True
            
            # if there are fes such that no words were contained in truth, add 1 fp for every fe
            for _, v in checked_fes.items():
                if not v:
                    cm.fp += 1  

        return cm

    def get_confusion_matrix_frame_elements_span(self, prediction_fes_list, truth_fes_list):
        cm = ConfusionMatrix()

        for pred_fes, truth_fes in zip_longest(prediction_fes_list, truth_fes_list, fillvalue=[]):

            for truth in truth_fes:
                if truth in pred_fes:
                    cm.tp +=1
                else:
                    cm.fn +=1
                    
            for pred in pred_fes:
                if pred not in truth_fes:
                    cm.fp +=1  
        return cm

    def from_srl_to_frame_elements(self, text, frame_list, dict_huric_example):
        text_list = text.split(" ")
        text_len = len(text_list)
        frame_elements = ["_"] * text_len

        for frame in frame_list:
            for frame_element in frame["frameElements"]:
                frame_element_pred = frame_element["name"]
                argument_pred = frame_element["argument"]
                in_text_pred = frame_element["in_text"]
                if in_text_pred:
                    #testo
                    tokens_argument_pred = argument_pred[0].split(" ") if argument_pred else []
                    for token_argument_pred in tokens_argument_pred:
                        if token_argument_pred in text_list:
                            token_index = text_list.index(token_argument_pred)
                            if frame_elements[token_index] == "_":
                                frame_elements[token_index] = []
                            if frame_element_pred not in frame_elements[token_index]:
                                frame_elements[token_index].append(frame_element_pred)
                else: 
                    #entità
                    for arg in argument_pred:
                        found_entity = False
                        for key, value in dict_huric_example.items():
                            if not found_entity:
                                if key != "sentence":
                                    if "frame_elements" in value.keys():
                                        frame_elements_huric = value["frame_elements"]
                                        for key, frame_element_huric in frame_elements_huric.items():
                                            name = frame_element_huric['name']
                                            if not frame_element_huric["in_text"]:
                                                values = frame_element_huric["values"]
                                                if len(values) > 0:
                                                    tokens = []
                                                    found = False
                                                    for v in values:
                                                        if not found:
                                                            objectName = v['objectName']
                                                            if arg == objectName: 
                                                                tokens.append(v['tokens'])
                                                                found = True
                                                                found_entity = True
                                                            
                                                    tokens = list(set([item for sublist in tokens for item in sublist]))

                                                for token in tokens:
                                                    if int(token) - 1 < len(frame_elements):
                                                        if frame_elements[int(token) - 1] == "_":
                                                            frame_elements[int(token) - 1] = []
                                                        if name not in frame_elements[int(token) - 1]:
                                                            frame_elements[int(token) - 1].append(frame_element_pred)

        return frame_elements


    # text = go to the kitchen and bring me the book
    # truth = MOTION(goal(kitchen)) & BRINGING(beneficiary(me), theme(the book)) => truth_list = [MOTION, BRINGING]
    # pred = MOTION(goal(kitchen)) & TAKING(theme(the book)) => pred_list = [MOTION, TAKING]
    def get_confusion_matrix_frames_only(self, texts, truths, preds):
        cm = ConfusionMatrix()

        for text, truth, pred in zip(texts, truths, preds):
            text_list = text.split(" " + SRL_Input.FEATURE_SEPARATOR.value + " ")[0].split(" ")
            # split predicative form in frames
            truth_list_raw = truth.split(SRL_Output.FRAME_SEPARATOR.value)
            pred_list_raw = pred.split(SRL_Output.FRAME_SEPARATOR.value)
            truth_list = []
            pred_list = []

            for truth_raw, pred_raw in zip(truth_list_raw, pred_list_raw):
                # get only frame name
                truth_list.append(truth_raw.split(SRL_Output.FRAME_CONTAINER_START.value)[0].replace(" ", ""))
                pred_list.append(pred_raw.split(SRL_Output.FRAME_CONTAINER_START.value)[0].replace(" ", ""))

            # compute confusion matrix here
            current_tot = 0
            for truth in truth_list:
                if truth in pred_list:
                    cm.tp +=1
                    current_tot += 1
                else:
                    cm.fn +=1
                    current_tot += 1

            for pred in pred_list:
                if not (pred in truth_list) and pred != "_":
                    cm.fp +=1
                    current_tot += 1
            
            cm.tn += max(len(text_list) - current_tot, 0)


        return cm