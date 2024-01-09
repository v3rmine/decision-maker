
from pprint import pprint

import pandas as pd
from simpletransformers.seq2seq import Seq2SeqModel, Seq2SeqArgs
from simpletransformers.t5 import T5Model, T5Args
from kfold import KFold
import os
import errno
from evaluator import Evaluator
import torch
from huricParser import HuricParser
import csv
from typing import List
import xlsxwriter
from datetime import datetime

from utils.confusion_matrix_merger import readSingleMatricesAndUnifiedMatrix
from utils.enums import Language, SRL_Output
from utils.errorAnalyser import ErrorAnalyzer
from utils.parsing_utils import computeLUDescriptionsIfDontExist, getMaxLength, isPredictionCorrect
from utils.results_merger import readResultsAndMerge

class Trainer:
    def __init__(self, lan: Language, model = 'bart', model_variant = 'base', task = "SRL", learning_rate = 1e-4, batch_size = 4, output_dir = 'outputs', best_model_dir = 'outputs/best_model', n_gpu = 0, num_train_epochs = 10, warmup_ratio = 0.1, patience = 3, use_cuda = False, target_type = "frame", early_stopping = True, num_beans=None, return_sequences=1):
        self.lan = lan
        self.model = model
        self.model_variant = model_variant
        self.model_name = ""
        self.task = task

        if model == "mt5" or model == "t5":
            self.model_args = T5Args()
            self.model_args.fp16 = False
            self.model_args.optimizer = "AdamW" #"AdamW" #"Adafactor"
            self.model_args.scheduler = "linear_schedule_with_warmup" #"linear_schedule_with_warmup" #"constant_schedule" #"constant_schedule_with_warmup" #
            self.model_args.learning_rate = learning_rate
            self.model_args.eval_batch_size = batch_size
            self.model_args.train_batch_size = batch_size
            if model == "t5":
                self.model_name = 't5-' + model_variant
            else:
                self.model_name = 'google/mt5-' + model_variant
            self.model_args.gradient_accumulation_steps = 2
            self.model_args.early_stopping_patience = patience
            self.model_args.early_stopping_delta = 1e-4 #0.005
        elif model == "bart":
            self.model_args = Seq2SeqArgs()
            self.model_args.fp16 = False
            self.model_args.optimizer = "AdamW" #"Adafactor"
            self.model_args.scheduler = "linear_schedule_with_warmup" #"constant_schedule" #"constant_schedule_with_warmup" #
            self.model_args.learning_rate = learning_rate
            self.model_args.eval_batch_size = batch_size
            self.model_args.train_batch_size = batch_size
            self.model_name = 'facebook/bart-' + model_variant
            self.model_args.gradient_accumulation_steps = 2
            self.model_args.early_stopping_patience = patience
            self.model_args.early_stopping_delta = 1e-4 #0.001
        # self.model_args.do_sample = True
        self.model_args.evaluate_during_training = True
        self.model_args.evaluate_during_training_steps = 100 #2500
        self.model_args.evaluate_during_training_verbose = True
        self.model_args.max_length = 255 #default value - changed in loading dataset
        self.model_args.max_seq_length = 255 #default value - changed in loading dataset
        self.model_args.num_beams = num_beans
        self.model_args.num_return_sequences = return_sequences
        self.model_args.num_train_epochs = num_train_epochs
        self.model_args.overwrite_output_dir = True
        self.model_args.reprocess_input_data = True
        self.model_args.save_eval_checkpoints = False
        self.model_args.save_model_every_epoch = False
        self.model_args.save_steps = -1
        # self.model_args.top_k = 0
        # self.model_args.top_k = 50
        # self.model_args.top_p = 0.95
        self.model_args.use_multiprocessing = False
        self.model_args.output_dir = output_dir
        self.model_args.best_model_dir = best_model_dir
        self.model_args.n_gpu = n_gpu
        self.model_args.warmup_ratio = warmup_ratio
        self.model_args.use_early_stopping = True
        self.model_args.early_stopping_consider_epochs = early_stopping
        self.model_args.early_stopping_metric = "eval_loss"
        self.model_args.early_stopping_metric_minimize = True
        self.use_cuda = use_cuda
        self.target_type = target_type

        print("**********************************")
        print("MODEL OPTIONS")
        pprint(self.__dict__)
        print("**********************************")


    def train_saving_all_folds_models(self, num_folds, quick_train = False, addMap = False, map_type = "no", addLUType = False, grounding="no"):
        evaluator = Evaluator(self.target_type)
        now = datetime.now() # current date and time
        date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        model_folder_name = 'model'

        kfold_folder_name = self.model + '_' + self.lan.value + "_" + map_type + "_" + grounding + "grounding"
        if addLUType:
            kfold_folder_name += "_addedLUType"
        kfold_folder_name += "_" + date_time
        kfold_base_dir = model_folder_name + '/' + kfold_folder_name + '/'
        hp = HuricParser(self.lan)

        # precompute lus description
        computeLUDescriptionsIfDontExist("./data/sentences_lus_descriptions", self.lan)

        # check if csv file exists, else generate it with huricParser
        if not os.path.exists("./data/huric_sentences_" + self.lan.value + ".csv"):
            print("Generating huric sentences file ..")
            hp.writeHuricSentences("./data/huric/", "./data/huric_sentences_" + self.lan.value + ".csv")
        
        df = pd.read_csv("./data/huric_sentences_" + self.lan.value + ".csv")
            
        
        # if quick_train is True, take 100 examples and quick train
        if quick_train:
            df = df.sample(frac=1.0).head(100)

        # max_sequence_length = calculateMaxColumnLength(self.model_name, datasetFile)
        # print("[max_sequence_length]" + str(max_sequence_length))
        # self.model_args.max_seq_length = max_sequence_length
        self.model_args.max_seq_length = 128

        # max_generation_length = calculateMaxColumnLength(self.model_name, datasetFile, column="target_text")
        # print("[max_generation_length]" + str(max_generation_length))
        # self.model_args.max_length = max_generation_length
        self.model_args.max_length = 128

        # default = 1.0 => no penalty
        # set to 
        #   < 1.0 to encourage model to generate shorter sequences
        #   > 1.0 to encourage model to generate longer sequences
        # self.model_args.length_penalty = 1.0

        cuda_available = torch.cuda.is_available() and self.use_cuda
        print('GPU available: ' + str(cuda_available))

        kfold = KFold(num_folds, True)
        fold_n = 0

        for test_df, eval_df, train_df in kfold.split(df):
            fold_n += 1
            print('CURRENT FOLD: ' + str(fold_n) + "/" + str(num_folds))
            kfold_dir = kfold_base_dir + str(fold_n)
            model_dir = kfold_dir + '/' + model_folder_name
            self.model_args.best_model_dir = model_dir
            train_file_path = kfold_dir + '/train.csv'
            eval_file_path = kfold_dir + '/eval.csv'
            test_file_path = kfold_dir + '/test.csv'
            confusion_matrix_name_file = 'confusion_matrix.txt'
            results_file = 'results'
            loss_file = 'loss'

            # if kfold_dir doesn't exist, create it
            # we have to save later a lot of files in there
            if not os.path.exists(kfold_dir):
                try:
                    os.makedirs(kfold_dir)
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            
            # for filename
            if addLUType:
                lutype = "_addedLUType"
            else:
                lutype = ""

            filename_to_load = "./data/huric_dataset/" + self.lan.value + "_" + map_type + "_" + grounding + "grounding" + lutype + ".csv"
            if not os.path.exists("./data/huric_dataset/"):
                try:
                    os.makedirs("./data/huric_dataset/")
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            hp.parseAndWrite("./data/huric/", self.task, filename_to_load, self.target_type, addMap, map_type, addLUType, grounding)
            allData = pd.read_csv(filename_to_load)

            # if multitask_model:
            #     for i in allData.index:
            #         thisInputText = allData["input_text"][i]
            #         allData["input_text"][i] = "NOMAP: " + thisInputText if " # NOMAP" in thisInputText else "MAP: " + thisInputText

            # compute here max len
            self.model_args.max_length = getMaxLength(allData['input_text'].tolist())
            self.model_args.max_seq_length = self.model_args.max_length 
            print(f"MAX LEN IS {self.model_args.max_length }")

            # need to take ids for saving predictions later to file
            train_df_ids = train_df['id'].tolist()
            test_df_ids = test_df['id'].tolist()
            eval_df_ids = eval_df['id'].tolist()
                
            train_input_text = []
            train_target_text = []
            for id, input_text, target_text in zip(allData['id'].tolist(), allData['input_text'].tolist(), allData['target_text'].tolist()):
                id_string = str(id).replace("999", "") # if multitask_model else str(id)
                if int(id_string) in train_df_ids:
                    train_input_text.append(input_text)
                    train_target_text.append(target_text)

            train_df = pd.DataFrame({
                'input_text': train_input_text, 
                'target_text': train_target_text
            })


            eval_input_text = []
            eval_target_text = []
            for id, input_text, target_text in zip(allData['id'].tolist(), allData['input_text'].tolist(), allData['target_text'].tolist()):
                id_string = str(id).replace("999", "") # if multitask_model else str(id)
                if int(id_string) in eval_df_ids:
                    eval_input_text.append(input_text)
                    eval_target_text.append(target_text)

            eval_df = pd.DataFrame({
                'input_text': eval_input_text, 
                'target_text': eval_target_text
            })
            

            test_input_text = []
            test_target_text = []
            for id, input_text, target_text in zip(allData['id'].tolist(), allData['input_text'].tolist(), allData['target_text'].tolist()):
                if id in test_df_ids:
                    test_input_text.append(input_text)
                    test_target_text.append(target_text)

            test_df = pd.DataFrame({
                'input_text': test_input_text, 
                'target_text': test_target_text
            })
            
            train_df.to_csv(train_file_path)
            test_df.to_csv(test_file_path)
            eval_df.to_csv(eval_file_path)

            if self.model in ["mt5", "t5"] and self.model_variant in ["small", "base", "large", "xl", "xxl"]:
                model = T5Model(
                    model_type=self.model,
                    model_name=self.model_name,
                    args=self.model_args,
                    use_cuda=cuda_available
                )
                # add prefix to test and train
                test_df['prefix'] = [self.task] * len(test_df['input_text'].tolist())
                eval_df['prefix'] = [self.task] * len(eval_df['input_text'].tolist())
                train_df['prefix'] = [self.task] * len(train_df['input_text'].tolist())

            elif self.model in ["bart"]:
                model = Seq2SeqModel(
                    encoder_decoder_type="bart",
                    encoder_decoder_name=self.model_name,
                    args=self.model_args,
                    use_cuda=cuda_available
                )

            print("_______________STARTING TO TRAIN_______________")
            model_train_out = model.train_model(train_df, eval_data=eval_df)
            self.save_loss_values_xlsx_file(kfold_dir + '/' + loss_file, model_train_out[1]['eval_loss'], model_train_out[1]['train_loss'])

            truth = test_df["target_text"].tolist()
            texts = test_df["input_text"].tolist()
            preds = model.predict(texts)

            # for SRL calculate 2 confusion matrix
            if self.target_type == "SRL":
                confusion_matrix_frame, confusion_matrix_frame_elements_span, confusion_matrix_frame_elements_head = evaluator.get_confusion_matrix(texts, preds, truth)
                confusion_matrix_frame.save_to_file(kfold_dir + '/' + 'frame_' + confusion_matrix_name_file)
                confusion_matrix_frame_elements_span.save_to_file(kfold_dir + '/' + 'frame_elements_span_' + confusion_matrix_name_file)
                confusion_matrix_frame_elements_head.save_to_file(kfold_dir + '/' + 'frame_elements_head_' + confusion_matrix_name_file)

            elif self.target_type == "FP + E2E":
                fp_cm, e2e_cm, _ = evaluator.get_confusion_matrix(texts, preds, truth)
                fp_cm.save_to_file(kfold_dir + '/' + 'frame_' + confusion_matrix_name_file)
                e2e_cm.save_to_file(kfold_dir + '/' + 'e2e_' + confusion_matrix_name_file)

            else:
                confusion_matrix, _, _ = evaluator.get_confusion_matrix(texts, preds, truth)
                confusion_matrix.save_to_file(kfold_dir + '/' + confusion_matrix_name_file)

            # get frames list text by text
            frames_lists = []
            for t in truth:
                splitted = t.split(" " + SRL_Output.FRAME_SEPARATOR.value + " ")
                tmp = []
                for split in splitted:
                    tmp.append(split.split("(")[0])

                frames_lists.append(tmp)

            self.save_predict_result_xlsx_file(kfold_dir + '/' + results_file, test_df_ids, texts, preds, truth, frames_lists)
            self.save_predict_result_csv_file(kfold_dir + '/' + results_file, test_df_ids, texts, preds, truth, frames_lists)

            # if quick_train is True, skip all other folds, if any
            if quick_train:
                break

        
        now = datetime.now() # current date and time
        date_time = now.strftime("%Y_%m_%d_%H_%M_%S")

        pred_type = self.target_type if self.task != "SRL" else self.task
        source = kfold_base_dir
        destination = model_folder_name + '/' + kfold_folder_name + '_' + pred_type + '_' + date_time
        # rename current kfold folder name
        os.rename(source, destination)

        readSingleMatricesAndUnifiedMatrix(destination)
        readResultsAndMerge(destination)
        ea = ErrorAnalyzer(destination)
        ea.analyze()

    
    def save_predict_result_xlsx_file(self, file, ids: List[str], texts: List[str], predictions: List[str], truths: List[str], frames_lists):
        
        file = file + '.xlsx'

        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, 'id')
        worksheet.write(0, 1, 'input_text')
        worksheet.write(0, 2, 'truth')
        worksheet.write(0, 3, 'prediction')
        worksheet.write(0, 4, 'totally correct')
        worksheet.write(0, 5, 'all frames correct')
        worksheet.write(0, 6, 'frames_list')
        row = 1

        for id, text, truth, pred, frames_list in zip(ids, texts, truths, predictions, frames_lists):
            isTotallyCorrect, allFramesCorrect = isPredictionCorrect(text, truth, pred)

            worksheet.write(row, 0, id)
            worksheet.write(row, 1, text)
            worksheet.write(row, 2, truth)
            worksheet.write(row, 3, pred)
            worksheet.write(row, 4, isTotallyCorrect)
            worksheet.write(row, 5, allFramesCorrect)
            worksheet.write(row, 6, ','.join(frames_list))
            row += 1
 
        workbook.close()
    
    def save_predict_result_csv_file(self, file, ids: List[str], texts: List[str], predictions: List[str], truths: List[str], frames_lists ):

        file = file + '.csv'
        header = ['id', 'input_text', 'truth', 'prediction', 'totally correct', 'all frames correct', 'frames_list']
        rows = []

        for id, text, truth, pred, frames_list in zip(ids, texts, truths, predictions, frames_lists):
            isTotallyCorrect, allFramesCorrect = isPredictionCorrect(text, truth, pred)
            rows.append([id, text, truth, pred, isTotallyCorrect, allFramesCorrect, ','.join(frames_list)])

        with open(file, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

    def save_loss_values_xlsx_file(self, file, eval_loss: List[str], train_loss: List[str]):
        
        file = file + '.xlsx'

        workbook = xlsxwriter.Workbook(file)
        worksheet = workbook.add_worksheet()

        worksheet.write(0, 0, 'eval_loss')
        worksheet.write(0, 1, 'train_loss')
        row = 1

        for eval, train in zip(eval_loss, train_loss):
            worksheet.write(row, 0, eval)
            worksheet.write(row, 1, train)
            row += 1
 
        workbook.close()
        



        
