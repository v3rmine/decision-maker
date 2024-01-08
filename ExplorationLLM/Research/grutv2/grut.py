from datetime import datetime

start_time = datetime.now()
printable_start_time = start_time.strftime("%H:%M:%S")
print(f"START {printable_start_time}")
##############################################################

from trainer import Trainer
from predictor import Predictor
from utils.enums import Language
import argparse
import logging
from huricParser import HuricParser

###############################################################
# IMPORTANT IMPORTS and OPTIONS
import torch.multiprocessing
torch.multiprocessing.set_sharing_strategy('file_system')

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
###############################################################
# LOGGING STUFF
logging.basicConfig(level=logging.INFO)
transformers_logger = logging.getLogger("transformers")
transformers_logger.setLevel(logging.WARNING)
###############################################################

# Instantiate the parser
parser = argparse.ArgumentParser(description='GrUT Models')

# Required positional argument
parser.add_argument('mode', type=str,
                    help='The modality: train or predict')

def defineTrainArguments(n_fold, use_cuda, epochs, targetType, modelName, modelVariant, batchSize, learning_rate, early_stopping, quick_train, addMap, addLUType, mapType, grounding, lexicalReferences, thresholdW2V, thresholdLDIST, additional_training_data_path):
    global parser

    # Optional argument
    parser.add_argument('-nf','--n_fold', type=int,
                        help='numbers of fold. Default "' + str(n_fold) + '". Define only in train mode.')

    # Optional argument
    parser.add_argument('-uc','--use_cuda', type=bool,
                        help='use GPU. Default "' + str(use_cuda) + '". Define only in train mode.')    
                        
    # Optional argument
    parser.add_argument('-lr','--learning_rate', type=float,
                        help='learning_rate parameter for training. Default "' + str(learning_rate) + '". Define only in train mode.')
                        
    # Optional argument
    parser.add_argument('-ep','--epochs', type=int,
                        help='number of epochs to train. Default "' + str(epochs) + '". Define only in train mode.')
    
    # Optional argument
    parser.add_argument('-tt','--target_type', type=str,
                        help='Type of target. Default "' + targetType + '". Define only in train mode. Possible values: frame | frame+pos | frame+token')

    # Optional argument
    parser.add_argument('-mn','--model_name', type=str,
                        help='model name. Choices: ["bart", "mbart", "t5", "mt5"], Default "' + str(modelName) + '". Define only in train mode.') 
    
    # Optional argument
    parser.add_argument('-mv','--model_variant', type=str,
                        help='model variant. Default "' + str(modelVariant) + '". Define only in train mode.') 

    # Optional argument
    parser.add_argument('-bs','--batch_size', type=int,
                        help='batch size. Default "' + str(batchSize) + '". Define only in train mode.') 

    # Optional argument
    parser.add_argument('-es','--early_stopping', type=bool,
                        help='early stopping considering epoch. Default "' + str(early_stopping) + '". Define only in train mode.') 

    # Optional argument
    parser.add_argument('-map','--mapType', type=str,
                        help='type of map to use. Default "' + mapType + '" . Define only in train mode.') 
                        
    # Optional argument
    parser.add_argument('-qt','--quick_train', type=bool,
                        help='whether or not to quick train and then test the model. It will take 100 random examples from dataset. Default "' + str(quick_train) + '". Define only in train mode.') 
    
    # Optional argument
    parser.add_argument('-am','--addMap', type=bool,
                        help='whether or not to add info about map to the input. Default "' + str(addMap) + '". Define only in train mode.') 
    
    # Optional argument
    parser.add_argument('-alut','--addLUType', type=bool,
                        help='whether or not to add info about lexical units to the input. Default "' + str(addLUType) + '". Define only in train mode.') 

    # Optional argument
    parser.add_argument('-gr','--grounding', type=str,
                        help='type of grounding to perform. Acceptable values are "full", "half", "post", "no". Default "' + str(grounding) + '". Define only in train mode.') 
    
    # Optional argument
    parser.add_argument('-lexr','--lexicalReferences', type=str,
                        help='type of lexical references of entity usage. Acceptable values are "all" for using all lrs or "random" for using 1 random lr. Default "' + str(lexicalReferences) + '". Define only in train mode.') 

    # Optional argument
    parser.add_argument('-tw2v','--thresholdW2V', type=float,
                        help='threshold for W2V retrieval. Acceptable values are floats between 0 and 1. Default "' + str(thresholdW2V) + '". Define only in train mode.') 
    
    # Optional argument
    parser.add_argument('-tLDIST','--thresholdLDIST', type=float,
                        help='threshold for Levenshtein Distance retrieval. Acceptable values are floats between 0 and 1. Default "' + str(thresholdLDIST) + '". Define only in train mode.') 
    
    # Optional argument
    parser.add_argument('-atdp','--additional_training_data_path', type=str,
                        help='Path to additional training data. The model will not be evaluated on this data, but it will only use it for training. Default "None". Define only in train mode.') 
       


def definePredictArguments(model_dir, text, huric_file_path):
    global parser

    # Optional argument
    parser.add_argument('-m', '--model_dir', type=str,
                        help='path to model_dir. Default "' + model_dir + '". Define only in predict mode.')

    # Optional argument
    parser.add_argument('-i','--input', type=str,
                        help='input text. Default "' + text + '". Define only in predict mode.')
                        
    # Optional argument
    parser.add_argument('-hrc','--huric_file_path', type=str,
                        help='path to huric file. Default "' + str(huric_file_path) + '". Define only in predict mode.')


def defineGlobalArguments(task, num_beams, return_sequences, language, entityRetrievalType):
    global parser

    # Optional argument
    parser.add_argument('-t','--task', type=str,
                        help='task type, one of \{FP, BD, AC, SRL\}. Default "' + task + '". Define both in train and predict mode.')
    # Optional argument
    parser.add_argument('-nb','--num_beams', type=int,
                        help='number of beams. Default "' + str(num_beams) + '". Define both in train and predict mode.')
                        
    # Optional argument
    parser.add_argument('-rs','--return_sequences', type=int,
                        help='number of sequences to return for each prediction. Default "' + str(return_sequences) + '". Define both in train and predict mode.')

    # Optional argument
    parser.add_argument('-lan','--language', type=str,
                        help='dataset language to use. Default "' + language.value + '". Define both in train and predict mode.')

    # Optional argument
    parser.add_argument('-ert','--entityRetrievalType', type=str,
                        help='type of entity retrieval. Acceptable values are "STR" for string match or "LDIST" for Levenshtein Distance or "W2V" for word2vec. Default "' + str(entityRetrievalType) + '". Define only in train mode.') 



def main():

    # both modes
    num_beams = None
    return_sequences = 1
    task = 'SRL'
    language = Language.ENGLISH
    entityRetrievalType = "STR"

    defineGlobalArguments(task, num_beams, return_sequences, language, entityRetrievalType)

    # train mode
    n_fold = 2
    use_cuda = False
    epochs = 1
    learning_rate = 1e-4
    target_type = 'SRL'
    modelName = "bart"
    modelVariant = "small"
    batch_size = 4
    early_stopping = True
    quick_train = False
    addMap = False
    addLUType = False
    mapType = "nomap"
    grounding = "no"
    lexicalReferences = "all"
    thresholdW2V = 0.5
    thresholdLDIST = 0.8
    additional_training_data_path = ""
    
    defineTrainArguments(n_fold, use_cuda, epochs, target_type, modelName, modelVariant, batch_size, learning_rate, early_stopping, quick_train, addMap, addLUType, mapType, grounding, lexicalReferences, thresholdW2V, thresholdLDIST, additional_training_data_path)

    #predict mode
    model_dir = '/model'
    text = "take the book near the cat on the sofa"
    # huric_file_path = "/data/huric/en/S4R/2748.hrc"
    huric_file_path = None

    definePredictArguments(model_dir, text, huric_file_path)

    # get arguments from command line
    args = parser.parse_args()
    
    # both modes
    if args.num_beams != None:
        num_beams = args.num_beams
    if args.return_sequences != None:
        return_sequences = args.return_sequences
    if args.task != None:
        task = args.task
    if args.language != None:
        # default is en
        # set only if different
        if args.language == "it" or args.language == "italian":
            language = Language.ITALIAN

    # train only options
    if args.mode == 'train':
        print('Starting train mode...')
        if args.n_fold != None:
            n_fold = args.n_fold
        if args.use_cuda != None:
            use_cuda = args.use_cuda
        if args.epochs != None:
            epochs = args.epochs
        if args.target_type != None:
            target_type = args.target_type
        if args.model_name != None:
            modelName = args.model_name
        if args.model_variant != None:
            modelVariant = args.model_variant
        if args.batch_size != None:
            batch_size = args.batch_size
        if args.early_stopping != None:
            early_stopping = args.early_stopping
        if args.quick_train != None:
            quick_train = args.quick_train
        if args.addMap != None:
            addMap = args.addMap
        if args.mapType != None:
            mapType = args.mapType
            if mapType != "nomap":
                addMap = True
        if args.grounding != None:
            grounding = args.grounding
        if args.addLUType != None:
            addLUType = args.addLUType
        if args.learning_rate != None:
            learning_rate = args.learning_rate
        if args.entityRetrievalType != None:
            entityRetrievalType = args.entityRetrievalType
        if args.lexicalReferences != None:
            lexicalReferences = args.lexicalReferences
        if args.additional_training_data_path != None:
            additional_training_data_path = args.additional_training_data_path


        trainer = Trainer(language, model=modelName, model_variant=modelVariant, task=task, learning_rate=learning_rate, batch_size=batch_size, use_cuda=use_cuda, num_train_epochs=epochs, target_type=target_type, early_stopping=early_stopping, num_beans=num_beams, return_sequences=return_sequences)
        print("Training and saving models for all folds!")
        trainer.train_saving_all_folds_models(n_fold, quick_train=quick_train, addMap=addMap, map_type=mapType, addLUType=addLUType, grounding=grounding, entityRetrievalType=entityRetrievalType, lexicalReferences=lexicalReferences, thresholdW2V=thresholdW2V, thresholdLDIST=thresholdLDIST, additional_training_data_path=additional_training_data_path)
        print("TRAIN FINISHED")

    # predict only options
    elif args.mode == 'predict':
        print('Starting predict mode...')
        if args.model_dir != None:
            model_dir = args.model_dir
        if args.input != None:
            text = args.input
        if args.huric_file_path != None:
            huric_file_path = args.huric_file_path
            if args.entityRetrievalType != None:
                entityRetrievalType = args.entityRetrievalType
            addMap = True
            hp = HuricParser(Language.ENGLISH)
            [_, sentence, _], _ = hp.parseHuricFile(huric_file_path, task, "", addMap, noMap=False, map_type="lmd", addLUType=False, grounding="yes", entityRetrievalType=entityRetrievalType, lan=language)
            text += " # " + sentence.split(" # ")[1]
            print("File parsed correctly!")
            print(f"The sentence with the map is: '{text}'")
        else:
            print("Huric file path not given, no map added (maybe it's already appended to the input?)")

        predictor = Predictor(model_dir=model_dir, num_beans=num_beams, return_sequences=return_sequences)
        result = predictor.predict(task, text)
        print(result)

    else:
        print("Invalid `" + str(args.mode) + "` mode!")
        print("You have to chose `train` or `predict` mode")
        print("EXAMPLE: `python main.py train`")

if __name__ == "__main__":
    main()


##############################################################
end_time = datetime.now()
difference_time = end_time - start_time
printable_difference_time = difference_time
printable_end_time = end_time.strftime("%H:%M:%S")
print(f"PASSED {printable_difference_time}")
print(f"ENDED AT {printable_end_time}")