# General Purpose Service Robot

[RoboCup](https://robocup.org/) scenario manager

## Introduction


### Definitions

- **[Ontologie en informatique](https://en.wikipedia.org/wiki/Ontology_(information_science)):** Representation, formal naming, and definitions of the categories, properties, and relations between the concepts, data, or entities that pertain to one, many, or all domains of discourse.

- **[Sementic Role Labelling](https://en.wikipedia.org/wiki/Semantic_role_labeling):** Process of assigning labels to words or phrases in a sentence that indicates their semantic role in the sentence, such as that of an agent, goal, or result.


## Technical

### Constraints

- Ontologie en [TOML](https://en.wikipedia.org/wiki/TOML) (pas YAML beurk)
- [ROS 2 Humble](https://docs.ros.org/en/humble/index.html) (EOL : May 2027)
- Python 3.11 (EOL : October 2027)

### Solutions

1. LLM fonctionnel via un model fine-tuned
2. Semantic role labelling (SpaCy)
3. LLM REL (SpaCy)? LangChain?

## Contributors

- Julien CAPOSIENA ([@julien-cpsn](https://github.com/Julien-cpsn))
- Johan PLANCHON ([@joxcat](https://github.com/joxcat))