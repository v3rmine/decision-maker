"""
A REPL that demonstrates how to use the generator to "parse" commands.
"""
from nltk.metrics.distance import edit_distance
import sys
import warnings
from gpsr_command_understanding.anonymizer import NumberingAnonymizer
from gpsr_command_understanding.generator.grammar import tree_printer
from gpsr_command_understanding.generator.knowledge import AnonymizedKnowledgebase
from gpsr_command_understanding.generator.loading_helpers import load_paired, GRAMMAR_YEAR_TO_MODULE
from gpsr_command_understanding.generator.paired_generator import pairs_without_placeholders
from gpsr_command_understanding.parser import AnonymizingParser, KNearestNeighborParser


def main():
    year = 2018
    if len(sys.argv) == 2:
        year = int(sys.argv[1])
    generator = load_paired("gpsr", GRAMMAR_YEAR_TO_MODULE[year])
    old_kb = generator.knowledge_base
    # Make the generator produce sentences with "anonymous" objects/locations. It wouldn't be feasible to
    # enumerate the grammar like this if we used more than few entities anyways
    generator.knowledge_base = AnonymizedKnowledgebase()
    # Get all anonymous pairs from the grammar. This involves traversing all of the user provided
    # annotations to the grammars. There are some known edgecases which trip warnings, so we'll ignore them.
    with warnings.catch_warnings(record=True) as w:
        all_pairs = pairs_without_placeholders(generator)
    print("Caught {} warnings will enumerating grammar".format(len(w)))
    ground_pairs = [generator.ground(pair, ignore_types=True) for pair in all_pairs.items()]
    baked_pairs = [(tree_printer(key), tree_printer(value)) for key, value in ground_pairs]
    # To parse, we'll look for close neighbors in the space of all generated sentences
    anon_edit_distance_parser = KNearestNeighborParser(baked_pairs, k=1, distance_threshold=5, metric=edit_distance)
    # Use the regular knowledgebase to strip entity names out of the input text
    anonymizer = NumberingAnonymizer.from_knowledge_base(old_kb)
    parser = AnonymizingParser(anon_edit_distance_parser, anonymizer)

    while True:
        print("Type in a command")
        utterance = input()
        # The AnonymyzingParser will print out the anonymized command, then the KNN parser will print out the
        # nearest neighbors
        parsed = parser(utterance, verbose=True)

        if parsed:
            print(parsed)
        else:
            print("Could not parse utterance based on the command grammar")


if __name__ == "__main__":
    main()
