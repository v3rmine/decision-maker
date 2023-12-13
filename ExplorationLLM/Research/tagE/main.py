"""
##############################################################################
TCS CONFIDENTIAL
__________________
Copyright : [2023] TATA Consultancy Services Ltd.
All Rights Reserved.

NOTICE:  All information contained herein is, and remains
the property of TATA Consultancy Services Ltd. and its suppliers,
if any. The intellectual and technical concepts contained
herein are proprietary to TATA Consultancy Services Ltd.
and its suppliers and may be covered by Foreign Patents,
patents in process, and are protected by trade secret or copyright law.
Dissemination of this information or reproduction of this material
is strictly forbidden unless prior written permission is obtained
from TATA Consultancy Services Ltd.
##############################################################################

Author : Chayan Sarkar (sarkar.chayan@tcs.com), Avik Mitra (mitra.avik1@tcs.com),
         Pradip Pramanick (pradip.pramanick@tcs.com), Tapas Nayak (nayak.taps@tcs.com)
Created : 2 January, 2023

"""

import yaml
import torch
import math
import pandas as pd
from tqdm import tqdm
from datetime import datetime

from transformers import BartConfig, BartTokenizer, BartForConditionalGeneration
from transformers import T5Config, T5Tokenizer, T5ForConditionalGeneration

from src.metrics import calculate_accuracy


def test_model(model, tokenizer, device, test_data, task_name_list, arg_name_list,
               batch_size, num_beams, min_length, max_length, with_arg_grounding, task_wise_accuracy):
    model.eval()
    total_time = 0

    out = list()
    batch_count = math.ceil(len(test_data) / batch_size)
    for batch_idx in tqdm(range(0, batch_count)):
        batch_start = batch_idx * batch_size
        cur_batch = test_data[batch_start:batch_start + batch_size]

        start = datetime.now()

        batch_input_idx = tokenizer(list(cur_batch["input"]), padding=True, return_tensors="pt")["input_ids"]
        batch_input_idx = batch_input_idx.to(device)

        summary_ids = model.generate(batch_input_idx,
                                     num_beams=num_beams,
                                     min_length=min_length,
                                     max_length=max_length)
        out += tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)

        end = datetime.now()
        total_time += (end - start).total_seconds() * 1000

    f1_score = calculate_accuracy(out, list(test_data["seq2seq_output"]), task_name_list, arg_name_list,
                                  with_arg_grounding=with_arg_grounding, task_wise_accuracy=task_wise_accuracy)

    print("time: ", total_time / len(test_data))
    return f1_score


def create_model(model_name, pretrained_path, model_weights):
    if model_name == "bart":
        tokenizer = BartTokenizer.from_pretrained(pretrained_path)
        bart_config = BartConfig.from_pretrained(pretrained_path)
        model = BartForConditionalGeneration(bart_config)
    else:
        tokenizer = T5Tokenizer.from_pretrained(pretrained_path)
        t5_config = T5Config.from_pretrained(pretrained_path)
        model = T5ForConditionalGeneration(t5_config)

    model.load_state_dict(torch.load(model_weights))

    return model, tokenizer


def get_classes(file_name):
    with open(file_name, 'r') as reader:
        class_names = [line.strip().lower() for line in reader.readlines()]
    return class_names


def main(config_file, with_arg_grounding, task_wise_accuracy):
    with open(config_file, "r") as reader:
        config = yaml.load(reader, Loader=yaml.FullLoader)

    device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    model, tokenizer = create_model(config["MODEL_NAME"], config["PRETRAINED_PATH"], config["MODEL_WEIGHTS"])

    test_data = pd.read_csv(config["TEST_DATA_FILE"])
    test_data = test_data[["input", "seq2seq_output"]]

    test_acc = test_model(model, tokenizer, device,
                          test_data=test_data,
                          task_name_list=get_classes(config["TASK_FILE"]),
                          arg_name_list=get_classes(config["ARG_FILE"]),
                          batch_size=config["BATCH_SIZE"], num_beams=config["NUM_BEAMS"],
                          min_length=config["MIN_LENGTH"], max_length=config["MAX_LENGTH"],
                          with_arg_grounding=with_arg_grounding, task_wise_accuracy=task_wise_accuracy)
    print('Test accuracy: {}'.format(test_acc))


if __name__ == '__main__':
    print("Statistics of BART based model")
    main(config_file="configs/tage_bart_config.yml", with_arg_grounding=False, task_wise_accuracy=False)

    # print("Statistics of T5 based model")
    # main(config_file="configs/tage_t5_config.yml", with_arg_grounding=False, task_wise_accuracy=False)
