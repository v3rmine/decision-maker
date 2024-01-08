from itertools import zip_longest
import os
from utils.confusion_matrix import ConfusionMatrix

def getMatricesFileName(path):
    frames, frame_elements_span, frame_elements_head, e2e, fp_cm, ai_cm, ac_cm = [], [], [], [], [], [], []

    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".txt"):
                if file == "frame_elements_span_confusion_matrix.txt":
                    frame_elements_span.append(os.path.join(root, file))
                elif file == "frame_elements_head_confusion_matrix.txt":
                    frame_elements_head.append(os.path.join(root, file))
                elif file == "frame_confusion_matrix.txt":
                    frames.append(os.path.join(root, file))
                elif file == "e2e_confusion_matrix.txt":
                    e2e.append(os.path.join(root, file))
                elif file == "FP_cm.txt":
                    fp_cm.append(os.path.join(root, file))
                elif file == "AI_cm.txt":
                    ai_cm.append(os.path.join(root, file))
                elif file == "AC_cm.txt":
                    ac_cm.append(os.path.join(root, file))
                

    return frames, frame_elements_span, frame_elements_head, e2e, fp_cm, ai_cm, ac_cm

def readSingleMatricesAndUnifiedMatrix(path):
    frames_filenames, frame_elements_span_filenames, frame_elements_head_filenames, e2e_filenames, fp_filenames, ai_filenames, ac_filenames = getMatricesFileName(path)
    cm_frames = ConfusionMatrix()
    cm_frame_elements_span = ConfusionMatrix()
    cm_frame_elements_head = ConfusionMatrix()
    e2e_cm = ConfusionMatrix()
    fp_cm = ConfusionMatrix()
    ai_cm = ConfusionMatrix()
    ac_cm = ConfusionMatrix()

    for frames_filename, frame_elements_span_filename, frame_elements_head_filename, e2e_filename, fp_filename, ai_filename, ac_filename in zip_longest(frames_filenames, frame_elements_span_filenames, frame_elements_head_filenames, e2e_filenames, fp_filenames, ai_filenames, ac_filenames, fillvalue="_"):
        
        # read frame_confusion_matrix and add numbers to ConfusionMatrix
        if frames_filename != "_":
            with open(frames_filename) as file:
                frames_lines = [line.rstrip() for line in file]
            for line in frames_lines:
                if line.startswith("TP"):
                    cm_frames.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    cm_frames.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    cm_frames.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    cm_frames.fn += int(line.split(" ")[1])
            
        # read frame_elements_span_confusion_matrix and add numbers to ConfusionMatrix
        if frame_elements_span_filename != "_":
            with open(frame_elements_span_filename) as file:
                frame_elements_span_lines = [line.rstrip() for line in file]
            for line in frame_elements_span_lines:
                if line.startswith("TP"):
                    cm_frame_elements_span.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    cm_frame_elements_span.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    cm_frame_elements_span.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    cm_frame_elements_span.fn += int(line.split(" ")[1])
            
        # read frame_elements_head_confusion_matrix and add numbers to ConfusionMatrix
        if frame_elements_head_filename != "_":
            with open(frame_elements_head_filename) as file:
                frame_elements_head_lines = [line.rstrip() for line in file]
            for line in frame_elements_head_lines:
                if line.startswith("TP"):
                    cm_frame_elements_head.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    cm_frame_elements_head.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    cm_frame_elements_head.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    cm_frame_elements_head.fn += int(line.split(" ")[1])

        # read e2e_confusion_matrix and add numbers to ConfusionMatrix
        if e2e_filename != "_":
            with open(e2e_filename) as file:
                e2e_lines = [line.rstrip() for line in file]
            for line in e2e_lines:
                if line.startswith("TP"):
                    e2e_cm.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    e2e_cm.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    e2e_cm.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    e2e_cm.fn += int(line.split(" ")[1])

        # read fp_cm and add numbers to ConfusionMatrix
        if fp_filename != "_":
            with open(fp_filename) as file:
                fp_lines = [line.rstrip() for line in file]
            for line in fp_lines:
                if line.startswith("TP"):
                    fp_cm.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    fp_cm.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    fp_cm.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    fp_cm.fn += int(line.split(" ")[1])

        # read ai_cm and add numbers to ConfusionMatrix
        if ai_filename != "_":
            with open(ai_filename) as file:
                ai_lines = [line.rstrip() for line in file]
            for line in ai_lines:
                if line.startswith("TP"):
                    ai_cm.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    ai_cm.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    ai_cm.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    ai_cm.fn += int(line.split(" ")[1])

        # read ac_cm and add numbers to ConfusionMatrix
        if ac_filename != "_":
            with open(ac_filename) as file:
                ac_lines = [line.rstrip() for line in file]
            for line in ac_lines:
                if line.startswith("TP"):
                    ac_cm.tp += int(line.split(" ")[1])
                if line.startswith("TN"):
                    ac_cm.tn += int(line.split(" ")[1])
                if line.startswith("FP"):
                    ac_cm.fp += int(line.split(" ")[1])
                if line.startswith("FN"):
                    ac_cm.fn += int(line.split(" ")[1])

    if frames_filenames:
        cm_frames.save_to_file(path + "/frames_CM_unified.txt")
        print("Saved file " + str(path + '/frames_CM_unified.txt'))

    if frame_elements_span_filenames:
        cm_frame_elements_span.save_to_file(path + "/frame_elements_span_CM_unified.txt")
        print("Saved file " + str(path + '/frame_elements_span_CM_unified.txt'))

    if frame_elements_head_filenames:
        cm_frame_elements_head.save_to_file(path + "/frame_elements_head_CM_unified.txt")
        print("Saved file " + str(path + '/frame_elements_head_CM_unified.txt'))

    if e2e_filenames:
        e2e_cm.save_to_file(path + "/e2e_CM_unified.txt")
        print("Saved file " + str(path + '/e2e_CM_unified.txt'))
    
    if fp_filenames:
        fp_cm.save_to_file(path + "/FP_CM_unified.txt")
        print("Saved file " + str(path + '/FP_CM_unified.txt'))

    if ai_filenames:
        ai_cm.save_to_file(path + "/AI_CM_unified.txt")
        print("Saved file " + str(path + '/AI_CM_unified.txt'))

    if ac_filenames:
        ac_cm.save_to_file(path + "/AC_CM_unified.txt")
        print("Saved file " + str(path + '/AC_CM_unified.txt'))
    