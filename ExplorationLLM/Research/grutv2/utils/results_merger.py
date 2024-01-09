
import pandas as pd
import os

from evaluator import Evaluator

def getResultsFileName(path):

    results = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == "results.xlsx":
                results.append(os.path.join(root, file))

    return results

def readResultsAndMerge(path):
    
    results_filenames = getResultsFileName(path)
    results_df = pd.DataFrame()

    for results_filename in results_filenames:
        # read results.xlsx and concatenate in single file
        results_df = results_df.append(pd.read_excel(results_filename), ignore_index=True) 

    # save unified file
    results_df.to_excel(path + '/results_unified.xlsx')
    print("Saved file " + str(path + '/results_unified.xlsx'))



def mergeAmbigousSentences(model_name, model_path):
    ambigousSentecesFilePath = "./model/"+ model_path + "/ambigous_sentences.xlsx"
    df = pd.read_excel(ambigousSentecesFilePath)
    ambigous_sentences = df['NOMAP input_text'].tolist()

    print("COMPUTING BART AMBIGOUS SENTENCES")
    # get bart_nomap results
    bart_nomap_file_path = "./model/"+ model_path + "/" + model_name + "_nomap/results_unified.xlsx"
    bart_nomap_df = pd.read_excel(bart_nomap_file_path)
    bart_nomap_inputs = bart_nomap_df['input_text'].tolist()
    bart_nomap_truth = bart_nomap_df['truth'].tolist()
    bart_nomap_prediction = bart_nomap_df['prediction'].tolist()

    # get bart_mtm results
    bart_mtm_file_path = "./model/"+ model_path + "/" + model_name + "_en_mtm_lmd/results_unified.xlsx"
    bart_mtm_df = pd.read_excel(bart_mtm_file_path)
    bart_mtm_inputs = bart_mtm_df['input_text'].tolist()
    bart_mtm_truth = bart_mtm_df['truth'].tolist()
    bart_mtm_prediction = bart_mtm_df['prediction'].tolist()

    nomap_input_text = []
    nomap_prediction = []
    nomap_truth = []
    mtm_input_text = []
    mtm_prediction = []
    mtm_truth = []
    for ambigous_sentence in ambigous_sentences:
        for index, nomap_input in enumerate(bart_nomap_inputs):
            if ambigous_sentence in nomap_input:
                nomap_input_text.append(nomap_input)
                nomap_prediction.append(bart_nomap_prediction[index])
                nomap_truth.append(bart_nomap_truth[index])
                
        for index, mtm_input in enumerate(bart_mtm_inputs):
            if ambigous_sentence in mtm_input:
                mtm_input_text.append(mtm_input)
                mtm_prediction.append(bart_mtm_prediction[index])
                mtm_truth.append(bart_mtm_truth[index])

    final_bart_df = pd.DataFrame({
        "NOMAP input_text": nomap_input_text,
        "NOMAP prediction": nomap_prediction,
        "NOMAP truth": nomap_truth,
        "MAP input_text": mtm_input_text,
        "MAP prediction": mtm_prediction,
        "MAP truth": mtm_truth,
    })

    final_bart_df.to_excel("./model/"+ model_path + "/" + model_name + "_ambigous_results.xlsx")

    print("COMPUTING NOMAP FRAMES CM")
    # compute here f1 on frames for nomap
    evaluator = Evaluator("SRL")
    nomap_cm = evaluator.get_confusion_matrix_frames_only(nomap_input_text, nomap_truth, nomap_prediction)
    # save it on model_name + "_nomap_ambigous_sentences_frames_cm.txt"
    nomap_cm.save_to_file('./model/'+ model_path + '/' + model_name + '_nomap_ambigous_sentences_frames_cm.txt')
    
    print("COMPUTING MTM FRAMES CM")
    # compute here f1 on frames for mtm
    evaluator = Evaluator("SRL")
    mtm_cm = evaluator.get_confusion_matrix_frames_only(mtm_input_text, mtm_truth, mtm_prediction)
    # save it on model_name + "_mtm_ambigous_sentences_frames_cm.txt"
    mtm_cm.save_to_file('./model/'+ model_path + '/' + model_name + '_mtm_ambigous_sentences_frames_cm.txt')

