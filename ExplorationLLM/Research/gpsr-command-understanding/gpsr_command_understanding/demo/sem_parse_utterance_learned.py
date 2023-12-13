"""
A REPL that demonstrates how to use a learned model to parse commands.
"""
from allennlp.models import load_archive
from allennlp.predictors import Predictor
import sys

from gpsr_command_understanding.anonymizer import NumberingAnonymizer
from gpsr_command_understanding.generator.loading_helpers import load_paired, GRAMMAR_YEAR_TO_MODULE
from gpsr_command_understanding.parser import AnonymizingParser, LearnedParser

# We need to register the model/predictors in this submodule
import gpsr_command_understanding.models


def main():
    if len(sys.argv) == 2:
        archive_path = sys.argv[1]
    else:
        print("Pass a path to a model archive file")
        exit(1)
    archive = load_archive(archive_file=archive_path)
    predictor = Predictor.from_archive(archive, predictor_name="command_parser")

    generator = load_paired("gpsr", GRAMMAR_YEAR_TO_MODULE[2019])

    # Use the regular knowledgebase to strip entity names out of the input text
    parser = LearnedParser(predictor)
    anonymizer = NumberingAnonymizer.from_knowledge_base(generator.knowledge_base)
    anonymizing_parser = AnonymizingParser(parser, anonymizer)

    while True:
        print("Type in a command")
        utterance = input()
        parsed = anonymizing_parser(utterance, verbose=True)

        if parsed:
            print(parsed)
        else:
            print("Could not parse utterance based on the command grammar")


if __name__ == "__main__":
    main()
