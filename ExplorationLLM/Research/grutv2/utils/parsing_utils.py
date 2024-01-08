
from scipy import spatial
from itertools import zip_longest
from transformers import BartTokenizer, AutoTokenizer
import spacy.language
import pandas as pd 
import os
from utils.confusion_matrix import ConfusionMatrix
from utils.enums import Language, SRL_Output
from utils.levenshetin_distance import levenshetin_similarity
import numpy

from utils.luDictComputer import LUDictComputer

#############################################################################
#               INITILIZE WORD EMBEDDINGS BEFORE USING IT                   #
#############################################################################
# add if "data/word_embeddings.txt" exists
word_embeddings = { 'en': {}, 'it': {}}
word_embedding_file_en = "data/word_embeddings_en.txt"
word_embedding_file_it = "data/word_embeddings_it.txt"
if os.path.exists(word_embedding_file_en) and os.path.exists(word_embedding_file_it):
    # open and store english word_embedding
    with open(word_embedding_file_en, 'r', encoding="UTF-8") as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            if index != 0:
                line_splitted = line.replace("\n", "").split("\t")
                # WARNING I removed the POS
                # TODO: in future add it back, after you compute POS tagging on input sentence
                word = line_splitted[0].split("::")[0]
                word_embeddings['en'][word] = [float(x) for x in line_splitted[-1].split(",")]
    # open and store italian word_embedding
    with open(word_embedding_file_it, 'r', encoding="UTF-8") as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            if index != 0:
                line_splitted = line.replace("\n", "").split("\t")
                # WARNING I removed the POS
                # TODO: in future add it back, after you compute POS tagging on input sentence
                word = line_splitted[0].split("::")[0]
                word_embeddings['it'][word] = [float(x) for x in line_splitted[-1].split(",")]
else:
    print("WORD EMBEDDINGS NOT FOUND\nEXIT")
    quit()
#############################################################################

def get_frame_lists_from_SRL_prediction(prediction: str, truth: str):
    predicted_frames_output = []
    truth_frames_output = []

    pred_obj = from_srl_string_to_obj(prediction)
    for frame in pred_obj:
        predicted_frames_output.append(frame['name'].upper())

    truth_obj = from_srl_string_to_obj(truth)
    for frame in truth_obj:
        truth_frames_output.append(frame['name'].upper())

    return predicted_frames_output, truth_frames_output


def get_entities_lists_from_SRL_prediction(prediction: str, truth: str):
    predicted_entities_output = []
    truth_entities_output = []

    pred_obj = from_srl_string_to_obj(prediction)
    for frame in pred_obj:
        for fe in frame['frameElements']:
            if fe['in_text']:
                predicted_entities_output.append(fe['argument'])
            else:
                # else is a list of entities
                for entity in fe['argument']:
                    predicted_entities_output.append(entity)


    truth_obj = from_srl_string_to_obj(truth)
    for frame in truth_obj:
        for fe in frame['frameElements']:
            if fe['in_text']:
                truth_entities_output.append(fe['argument'])
            else:
                # else is a list of entities
                for entity in fe['argument']:
                    truth_entities_output.append(entity)
    
    return predicted_entities_output, truth_entities_output


def get_arguments_lists_from_SRL_prediction(prediction: str, truth: str):
    predicted_arguments_output = []
    truth_arguments_output = []

    pred_obj = from_srl_string_to_obj(prediction)
    for frame in pred_obj:
        for fe in frame['frameElements']:
            predicted_arguments_output.append(fe['name'].upper())


    truth_obj = from_srl_string_to_obj(truth)
    for frame in truth_obj:
        for fe in frame['frameElements']:
            truth_arguments_output.append(fe['name'].upper())
    
    return predicted_arguments_output, truth_arguments_output


def replaceSeparators(input: str, intext: bool = False) -> str:
    if not intext:
        input = input.replace(" ", "")
    input = input.replace(".", ":").replace("[", "").replace("]","").replace(";", ":")
    input = input.replace(SRL_Output.ARGUMENT_IN_TEXT_START.value, "").replace(SRL_Output.ARGUMENT_IN_TEXT_END.value, "")
    input = input.replace(SRL_Output.ARGUMENT_CONTAINER_START.value, "").replace(SRL_Output.ARGUMENT_CONTAINER_END.value, "")
    input = input.replace(SRL_Output.FRAME_SEPARATOR.value, "")
    return input


# MOTION(err(t8, t9), err2('please machine')) & CHANGE_OPERATIONAL_STATE(Agent(t8), Device('it'), Operational_state('on'))
def from_srl_string_to_obj(input: str):
    obj_list = []
    frames = input.split(" " + SRL_Output.FRAME_SEPARATOR.value + " ")

    for frame in frames:
        obj = {}
        name =  frame[:frame.find(SRL_Output.FRAME_CONTAINER_START.value)]
        obj["name"] = name.replace(" ", "").replace(SRL_Output.FRAME_CONTAINER_START.value, "").replace(SRL_Output.FRAME_CONTAINER_END.value, "")
        

        end_frame_elements_string_separator = SRL_Output.ARGUMENT_CONTAINER_END.value + SRL_Output.FRAME_CONTAINER_END.value
        if end_frame_elements_string_separator not in frame :
            end_frame_elements_string_separator = SRL_Output.ARGUMENT_CONTAINER_END.value + " " + SRL_Output.FRAME_CONTAINER_END.value
        frame_elements_string = frame[frame.find(SRL_Output.FRAME_CONTAINER_START.value) + 1:frame.find(end_frame_elements_string_separator)] 

        end_frame_element_separator = SRL_Output.ARGUMENT_CONTAINER_END.value + SRL_Output.ARGUMENT_SEPARATOR.value
        if end_frame_element_separator not in frame_elements_string:
            frameElements = frame_elements_string.split(end_frame_element_separator + " ") 
        frameElements = frame_elements_string.split(end_frame_element_separator)
        
        obj["frameElements"] = []
        for frameElement in frameElements:
            fe = {}
            name =  frameElement[:frameElement.find(SRL_Output.ARGUMENT_CONTAINER_START.value)].replace(" ", "").replace(SRL_Output.ARGUMENT_CONTAINER_START.value, "").replace(SRL_Output.ARGUMENT_CONTAINER_END.value, "")
            fe["name"] = name
            argument_string = frameElement[frameElement.find(SRL_Output.ARGUMENT_CONTAINER_START.value) + 1:]
            if len(argument_string) > 1:
                if argument_string[0] == SRL_Output.ARGUMENT_IN_TEXT_START.value or argument_string[-1] == SRL_Output.ARGUMENT_IN_TEXT_END.value:
                    fe["in_text"] = True
                    fe["argument"] = [replaceSeparators(argument_string, intext=True)]
                else:
                    fe["in_text"] = False
                    fe["argument"] = [replaceSeparators(x, intext=False) for x in argument_string.split(SRL_Output.ARGUMENT_SEPARATOR.value)]
            else:
                fe["in_text"] = True
                fe["argument"] = [""]

            obj["frameElements"].append(fe)

        obj_list.append(obj)

    return obj_list

def calculateMaxColumnLength(model_name, df, column = 'input_text'):
    print("Calculating length for column = " + column)
    # tokenizer = ""
    # if "mt5" in model_name:
    #     tokenizer = T5Tokenizer.from_pretrained(model_name)
    # elif "bart" in model_name:
    #     tokenizer = BartTokenizerFast.from_pretrained(model_name)
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # debugging lengths
    ids = df["id"].tolist()
    lengths = {}

    input_texts = df[column].tolist()
    max_length = 0
    for x, id in zip(input_texts, ids):
        inputs = tokenizer(x, return_tensors="pt")
        length = int(inputs["input_ids"].shape[1])
        if length > max_length and length < 245:
            max_length = length

        # debugging lengths
        if length in lengths.keys():
            lengths[length].append(id)
        else:
            lengths[length] = [id]

    return max_length + 10, dict(sorted(lengths.items()))


def getLUDescriptions(sentence, lan: Language, nlp: spacy.language.Language):
    doc = nlp(sentence)

    lu_dict_filename = "./data/lu_dict_" + lan.value + ".txt"
    file = open(lu_dict_filename, 'r')
    lines = file.readlines()
    
    lus = {}
    for line in lines:
        line_splitted = line.split("\t")
        lus[line_splitted[0]] = line_splitted[1].replace("\n", "").split(',')

    # if you find these special cases, add indexes to "consumed_indexes"
    sentence_lus = []
    consumed_indexes = []
    sentence_splitted = sentence.split(" ")
    if "go along" in sentence:
        sentence_lus.append("go along can evoke COTHEME")
        consumed_indexes.append(sentence_splitted.index("go"))
        consumed_indexes.append(sentence_splitted.index("along"))
    if "let go" in sentence:
        sentence_lus.append("let go can evoke RELEASING")
        consumed_indexes.append(sentence_splitted.index("go"))
        consumed_indexes.append(sentence_splitted.index("let"))
    if "pick up" in sentence:
        sentence_lus.append("pick up can evoke TAKING")
        consumed_indexes.append(sentence_splitted.index("pick"))
        consumed_indexes.append(sentence_splitted.index("up"))

    for sent in doc.sents:
        for i, word in enumerate(sent):
            lemma = word.lemma_
            if lemma in lus and i not in consumed_indexes:
                if lan == "en":
                    sentence_lus.append(lemma + " can evoke " + " or ".join(lus[lemma]))
                elif lan == "it":
                    sentence_lus.append(lemma + " può evocare " + " oppure ".join(lus[lemma]))

    # print(f"Sentence {sentence} \t lus {sentence_lus}")
    return sentence_lus


def precomputeLUDescriptions(filename, ids, sentences, lan = 'en'):
    lines = []

    for id, sen in zip(ids, sentences):
        lines.append(str(id) + "\t" + ",".join(getLUDescriptions(sen, lan))+"\n")

    file = open(filename, 'w')
    file.writelines(lines)
    print(f"Done writing {filename} with {len(lines)} values")


def computeLUDescriptionsIfDontExist(filename, lan: Language):
    if not os.path.exists(filename):
        print("Computing LU DESCRIPTIONS")
        # precompute lus dictionary
        luDC = LUDictComputer(lan)
        luDC.precompute()

        # precompute lus description for every sentence
        sentences = pd.read_csv('./data/huric_sentences_' + lan.value + '.csv')
        precomputeLUDescriptions(filename, sentences['id'].tolist(), sentences['sentence'].tolist())


def getMaxLength(strings, model_name = "bart"):
    #tokenizer = BartTokenizer.from_pretrained(model_name)
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    max = 0
    for string in strings:
        inputs = tokenizer(string, return_tensors="pt")
        if len(inputs['input_ids'][0]) > max:
            max = len(inputs['input_ids'][0])

    return max + 10


def compute_e2e_cm(predictions, truths) -> ConfusionMatrix:
    cm = ConfusionMatrix()

    for predictions_list, truths_list in zip(predictions, truths):
        for truth in truths_list:
            if truth in predictions_list:
                cm.tp +=1
            else:
                cm.fn +=1

        for pred in predictions_list:
            if pred not in truths_list:
                cm.fp +=1
    return cm
        
def isPredictionCorrect(text, truth, pred):
    prediction_obj_list = from_srl_string_to_obj(pred)
    truth_obj_list = from_srl_string_to_obj(truth)

    e2e_pred_examples = []
    e2e_truth_examples = []
    predicted_frames = []
    truth_frames = []
    for pred_frame_obj, truth_frame_obj in zip_longest(prediction_obj_list, truth_obj_list, fillvalue={}):
        if pred_frame_obj:
            predicted_frames.append(pred_frame_obj['name'] )
        if truth_frame_obj:
            truth_frames.append(truth_frame_obj['name'] )

        if 'frameElements' in pred_frame_obj:
            for fe in pred_frame_obj['frameElements']:
                for argument in fe['argument']:
                    e2e_pred_examples.append(pred_frame_obj['name'] + "_" + fe['name'] + "_" + argument)
        else:
            print(f"No frame elements PREDICTED for {text}")

        if 'frameElements' in truth_frame_obj:
            for fe in truth_frame_obj['frameElements']:
                for argument in fe['argument']:
                    e2e_truth_examples.append(truth_frame_obj['name'] + "_" + fe['name'] + "_" + argument)
        else:
            print(f"No frame elements TRUTH for {text}")

    e2e_cm = compute_e2e_cm([e2e_pred_examples], [e2e_truth_examples])
    isTotallyCorrect = e2e_cm.get_f1() == 1.0

    allFramesCorrect = True
    for predicted_frame in predicted_frames:
        if predicted_frame not in truth_frames:
            allFramesCorrect = False
            break
    for truth_frame in truth_frames:
        if truth_frame not in predicted_frames:
            allFramesCorrect = False
            break
    
    return isTotallyCorrect, allFramesCorrect


def print_elements_with_no_entities():
    dictionary = {}

    df = pd.read_csv("./data/huric_dataset/en_stm_lmd_fullgrounding.csv")

    lines = [[id, srl] for id, srl in zip(df['id'], df['target_text'])]

    for line in lines:
        id = line[0]
        dictionary[id] = []
        srl = line[1]
        frames = from_srl_string_to_obj(srl)
        for frame in frames:
            for fe in frame['frameElements']:
                if fe['in_text'] and fe['argument'][0] not in ['it', 'they', 'them', 'the item', 'is hot', 'are off', 'on', 'backward', 'forward', 'off', 'back', 'left', 'right', 'quickly', 'slowly', 'from behind', 'out', 'carefully', 'that', 'to your left', 'to your right', 'to the left', 'to the right', 'with them', 'this', 'by 60 degrees', 'by almost 90 degrees', 'by 180 degrees', 'to the web', 'via backstairs', 'on it', 'her', 'fast', 'on your right side', 'on the left side', 'on the right', 'closely', 'us', 'everywhere he goes', 'which', 'veryfast', 'some', 'is on', 'is empty', "'s", 'the man', 'the pocket', 'very fast', 'here', 'over here', 'is ready', 'a little bit', 'one', 'down', 'there', 'around']:
                    dictionary[id].append(fe['argument'][0])

    dictionary2 = {k: v for k,v in dictionary.items() if v}
    print(dictionary2)


def entity_in_sentence(entity, sentence, lan: Language, nlp: spacy.language.Language = "", type: str = "STR", thresholdW2V = 0.5, thresholdLDIST = 0.8):
    sen_split = sentence.split(" ")
    entity_len = len(entity.split(" "))
    indexes = []
    for index, _ in enumerate(sen_split):
        if index + entity_len <= len(sen_split):
            chunk = " ".join(sen_split[index : index+entity_len])

            if type == "STR":
                sim = 1.0 if entity == chunk else 0.0
                if sim == 1.0:
                    indexes.extend([str(x + 1) for x in range(index, index + entity_len)])
            elif type == "LDIST":
                sim = levenshetin_similarity(entity, chunk)
                if sim >= thresholdLDIST:
                    indexes.extend([str(x + 1) for x in range(index, index + entity_len)])
            elif type == "W2V":
                if nlp:
                    sim = word2vec_similarity(entity, chunk, nlp, lan)
                    if sim >= thresholdW2V:
                        indexes.extend([str(x + 1) for x in range(index, index + entity_len)])
                else:
                    print("ERROR: nlp (a.k.a. spacy model) is not defined. You need to pass a spacy model for W2V embedding!")
                    quit()

    return indexes


def get_word_embedding(sentence: str, nlp: spacy.language.Language, lan: Language):
    global word_embeddings

    sentence_parsed = nlp(sentence)
    we = numpy.array([0.0 for _ in range(250)])

    for sent in sentence_parsed.sents:
        for word in sent:
            lemma = word.lemma_.lower()
            # if word_embeddings contains word, take embedding
            # else generate random 250 numbers between -1.0 and 1.0
            if lemma in word_embeddings :
                embedding = numpy.array(word_embeddings[lan.value][lemma])
            else:
                # if lemma is not present in main we dictionary
                # retrieve newly created we dictionary (or create it if it does not exist)
                lemma_not_found = False
                word_embedding_not_found_file = "./data/word_embeddings_not_found_" + lan.value + ".txt"
                if os.path.exists(word_embedding_not_found_file):
                    with open(word_embedding_not_found_file, "r") as f:
                        lines = f.readlines()
                        we_not_found = {}
                        for line in lines:
                            line_splitted = line.replace("\n", "").split("\t")
                            
                            word = line_splitted[0]
                            we_not_found[word] = [float(x) for x in line_splitted[-1].split(",")]

                        # search lemma here
                        # if does not exist here neither, compute random we and add it
                        if lemma in we_not_found:
                            embedding = we_not_found[lemma]
                        else:
                            lemma_not_found = True
                else:
                    lemma_not_found = True
                if lemma_not_found:
                    # save it to use it in future runs
                    with open(word_embedding_not_found_file, "a+") as f:
                        embedding = numpy.random.uniform(low=-1.0, high=1.0, size=250)
                        f.write(lemma + "\t" + ", ".join(map(str, embedding)) + "\n")
            
            we += embedding

    return we


def word2vec_similarity(a: str, b: str, nlp: spacy.language.Language, lan: Language):
    a_we = get_word_embedding(a, nlp, lan)
    b_we = get_word_embedding(b, nlp, lan)

    return 1 - spatial.distance.cosine(a_we, b_we)
