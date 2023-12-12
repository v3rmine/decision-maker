"""
A REPL that demonstrates how to use the grammar-based parser to parse commands.
"""
import sys

from gpsr_command_understanding.anonymizer import NumberingAnonymizer
from gpsr_command_understanding.generator.loading_helpers import load_paired, GRAMMAR_YEAR_TO_MODULE
from gpsr_command_understanding.parser import GrammarBasedParser, AnonymizingParser


def main():
    year = 2018
    if len(sys.argv) == 2:
        year = int(sys.argv[1])
    generator = load_paired("gpsr", GRAMMAR_YEAR_TO_MODULE[year])

    parser = GrammarBasedParser(generator.rules)
    anonymizer = NumberingAnonymizer.from_knowledge_base(generator.knowledge_base)
    parser = AnonymizingParser(parser, anonymizer)
    while True:
        print("Type in a command")
        utterance = input()
        parsed = parser(utterance, verbose=True)

        if parsed:
            print(parsed.pretty())
        else:
            print("Could not parse utterance based on the command grammar")


if __name__ == "__main__":
    main()
