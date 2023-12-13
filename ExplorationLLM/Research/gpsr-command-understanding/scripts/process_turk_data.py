import glob
import re

from nltk.metrics.distance import edit_distance, jaccard_distance
import pandas as pd

paraphrasings = []
new = []


def process_turk_files(paths, filter_rejected=True):
    print("Processing paths: {}".format(str(paths)))

    def drop_trailing_num(name):
        try:
            return next(re.finditer(r'[\D\.]*', name)).group(0)
        except StopIteration:
            return name

    frame = pd.concat([pd.read_csv(path, na_filter=False) for path in paths], ignore_index=True)
    if filter_rejected:
        frame.drop(frame[frame["AssignmentStatus"] == "Rejected"].index, inplace=True)

    data_views = []
    num_commands = frame.filter(regex='^Input.command', axis=1).shape[1]
    for n in range(1, num_commands + 1):
        columns = ["Input.command" + str(n), "Answer.utterance" + str(n), "Input.parse" + str(n),
                   "Input.parse_ground" + str(n), "WorkerId"]
        data_views.append(frame[columns].rename(columns=drop_trailing_num))
    paraphrasings = pd.concat(data_views)
    paraphrasings.sort_values(by="Answer.utterance", inplace=True)
    new_views = []
    num_new_commands = frame.filter(regex='^Answer.custom', axis=1).shape[1]
    for n in range(1, num_new_commands + 1):
        new_views.append(frame[["Answer.custom" + str(n), "WorkerId"]].rename(columns=drop_trailing_num))
    new = pd.concat(new_views)
    new.sort_values(by="Answer.custom", ignore_index=True, inplace=True)

    nice_names = {"Answer.utterance": "paraphrase", "Input.command": "command", "Answer.custom": "command"}
    paraphrasings.rename(columns=nice_names, inplace=True)
    new.rename(columns=nice_names, inplace=True)
    other_data = frame.drop(
        columns=[c for c in frame.columns if ("Input" in c or "Answer" in c) and not (c == "Answer.comment")])
    return paraphrasings, new, other_data


paraphrasings, new, other_data = process_turk_files(glob.glob("batch_*.csv"))

paraphrasings["EditDistanceNormalized"] = paraphrasings.apply(
    lambda row: edit_distance(row["command"], row["paraphrase"]) / len(row["command"]), axis=1)
paraphrasings["EditDistance"] = paraphrasings.apply(
    lambda row: edit_distance(row["command"], row["paraphrase"]), axis=1)
paraphrasings["JaccardDistance"] = paraphrasings.apply(
    lambda row: jaccard_distance(set(row["command"].split()), set(row["paraphrase"].split())), axis=1)

print(
    "{:.2f} {:.2f} {:.2f}".format(paraphrasings["EditDistanceNormalized"].mean(), paraphrasings["EditDistance"].mean(),
                                  paraphrasings["JaccardDistance"].mean()))
by_worker = paraphrasings.groupby(paraphrasings["WorkerId"])
for name, group in by_worker:
    print(name)
    for i, (original, paraphrase) in group[["command", "paraphrase"]].iterrows():
        print(original)
        print(paraphrase)
        print("")

turker_performance = pd.DataFrame()
turker_performance["HITTime"] = other_data.groupby("WorkerId")["WorkTimeInSeconds"].mean()
turker_performance["MeanNormalizedEditDistance"] = paraphrasings.groupby("WorkerId")["EditDistanceNormalized"].mean()
turker_performance["MeanJaccardDistance"] = paraphrasings.groupby("WorkerId")["JaccardDistance"].mean()
turker_performance["Comment"] = other_data.groupby("WorkerId")["Answer.comment"]
for _, (original, parse, paraphrase, edit, jaccard) in paraphrasings[
    ["command", "Input.parse", "paraphrase", "EditDistance", "JaccardDistance"]].iterrows():  # noqa
    print(original)
    print(parse)
    print(paraphrase)
    print("dist: ed{:.2f} ja{:.2f}".format(edit, jaccard))
    print("")

print("--------------")
new_by_worker = new.groupby(new["WorkerId"])
for name, group in new_by_worker:
    print(name)
    for custom_utt in group["command"]:
        print(custom_utt)
        print("")

print("{} workers provided {} paraphrases and {} new commands".format(len(by_worker), len(paraphrasings), len(new)))

with open("paraphrasings.txt", 'w') as outfile:
    for _, (paraphrase, command) in paraphrasings[["paraphrase", "command"]].sort_values(
            by="paraphrase").iterrows():
        outfile.write(command + "\n")
        outfile.write(paraphrase + "\n")

with open("paraphrasings_grounded.txt", 'w') as outfile:
    for _, (paraphrase, logical_ground) in paraphrasings[["paraphrase", "Input.parse_ground"]].sort_values(
            by="paraphrase").iterrows():
        outfile.write(paraphrase + "\n")
        outfile.write(logical_ground + "\n")

with open("orig_para_logical.txt", 'w') as outfile:
    for _, (paraphrase, command, logical_ground) in paraphrasings[
        ["paraphrase", "command", "Input.parse_ground"]].sort_values(
            by="paraphrase").iterrows():
        outfile.write(command + "\n")
        outfile.write(paraphrase + "\n")
        outfile.write(logical_ground + "\n")

with open("custom.txt", 'w') as outfile:
    for command in new["command"].sort_values():
        outfile.write(command + "\n")
