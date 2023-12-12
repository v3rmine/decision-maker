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


def parse_output(tasks, task_split, arg_split):
    task_list = list()
    task_count = 0
    arg_count = 0

    for task in tasks.split(';'):

        if len(task.strip(' ')) == 0:
            break

        elements = task.split(',')
        t_type = elements[0].split(':')
        task_name = t_type[0].strip()

        if len(t_type) == 2 and task_name in task_split:
            task_val = t_type[1].strip()

            task_count += 1
            task_split[task_name] += 1

            arg_list = list()
            for element in elements[1:]:
                a_type = element.split(':')
                arg_name = a_type[0].strip()
                if len(a_type) == 3 and arg_name in arg_split:
                    arg_val = a_type[1].strip()
                    arg_gnd = a_type[2].strip()
                    arg_list.append((arg_name, arg_val, arg_gnd))
                    arg_count += 1
                    arg_split[arg_name] += 1
                elif len(a_type) == 2 and arg_name in arg_split:
                    arg_val = a_type[1].strip()
                    arg_list.append((arg_name, arg_val))
                    arg_count += 1
                    arg_split[arg_name] += 1

            task_list.append((task_name, task_val, arg_list))
    return task_list, task_count, arg_count


def calculate_accuracy(pred_list, gt_list, task_name_to_ids, arg_name_to_ids,
                       with_arg_grounding=True, task_wise_accuracy=False):
    init_value = 0.000001
    match_count = 0
    total_gt_arg_count = init_value
    total_pred_arg_count = init_value

    gt_task_split = dict()
    pred_task_split = dict()
    match_task_split = dict()
    for task in task_name_to_ids:
        gt_task_split[task.lower()] = init_value
        pred_task_split[task.lower()] = init_value
        match_task_split[task.lower()] = init_value

    gt_arg_split = dict()
    pred_arg_split = dict()
    match_arg_split = dict()
    for arg in arg_name_to_ids:
        gt_arg_split[arg.lower()] = init_value
        pred_arg_split[arg.lower()] = init_value
        match_arg_split[arg.lower()] = init_value

    for pred, gt in zip(pred_list, gt_list):
        gt_task_list, gt_task_count, gt_arg_count = parse_output(gt, gt_task_split, gt_arg_split)
        pred_task_list, pred_task_count, pred_arg_count = parse_output(pred, pred_task_split, pred_arg_split)

        total_gt_arg_count += gt_arg_count
        total_pred_arg_count += pred_arg_count

        covered_task = [0] * len(gt_task_list)
        for pred_task in pred_task_list:
            for j in range(len(gt_task_list)):
                if pred_task[0] == gt_task_list[j][0] and pred_task[1] == gt_task_list[j][1] \
                        and covered_task[j] == 0:
                    match_task_split[pred_task[0]] += 1
                    covered_task[j] = 1
                    for pred_arg in pred_task[2]:
                        match = 0
                        for gt_arg in gt_task_list[j][2]:
                            if with_arg_grounding:
                                if len(pred_arg) == 3 and pred_arg[0] == gt_arg[0] and pred_arg[1] == gt_arg[1] \
                                        and pred_arg[2] == gt_arg[2]:
                                    match_arg_split[pred_arg[0]] += 1
                                    match = 1
                                    break
                            else:
                                if pred_arg[0] == gt_arg[0] and pred_arg[1] == gt_arg[1]:
                                    match_arg_split[pred_arg[0]] += 1
                                    match = 1
                                    break
                        if match:
                            match_count += 1
                    break

    precision = match_count / total_pred_arg_count
    recall = match_count / total_gt_arg_count
    f1_score = 2 * (precision * recall) / (precision + recall + 0.0000001)

    if task_wise_accuracy:
        for task in task_name_to_ids:
            precision = match_task_split[task] / gt_task_split[task]
            recall = match_task_split[task] / pred_task_split[task]
            f1_score = 2 * (precision * recall) / (precision + recall + 0.0000001)
            print("{},{},{},{}".format(task, round(precision, 2), round(recall, 2), round(f1_score, 2)))
        print("\n")
        for arg in arg_name_to_ids:
            precision = match_arg_split[arg] / gt_arg_split[arg]
            recall = match_arg_split[arg] / pred_arg_split[arg]
            f1_score = 2 * (precision * recall) / (precision + recall + 0.0000001)
            print("{},{},{},{}".format(arg, round(precision, 2), round(recall, 2), round(f1_score, 2)))

        print("\nPrecision: {}, Recall: {}, F1: {}".format(round(precision, 4), round(recall, 4), round(f1_score, 4)))
    return f1_score
