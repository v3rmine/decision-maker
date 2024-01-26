# General Purpose Service Robot [![status](https://cicd.planchon.dev/api/v1/teams/main/pipelines/cpe.robot-project-mirror/badge)](https://cicd.planchon.dev/teams/main/pipelines/cpe.robot-project-mirror)

[RoboCup](https://robocup.org/) scenario manager

Vidéo de présentation : https://youtu.be/VEUW_xUpAgg

## Contributeurs

- Julien CAPOSIENA ([@julien-cpsn](https://github.com/Julien-cpsn))
- Johan PLANCHON ([@joxcat](https://github.com/joxcat))

## TOC
- [General Purpose Service Robot ](#general-purpose-service-robot-)
  - [Contributeurs](#contributeurs)
  - [TOC](#toc)
  - [Introduction](#introduction)
    - [Définitions](#définitions)
  - [Technique](#technique)
    - [Contraintes](#contraintes)
    - [Structure](#structure)
  - [Autre](#autre)
    - [CICD](#cicd)
    - [Setup Jetson AGX Orin Devkit](#setup-jetson-agx-orin-devkit)


## Introduction

### Définitions

- **[Ontologie en informatique](https://en.wikipedia.org/wiki/Ontology_(information_science)):** Representation, formal naming, and definitions of the categories, properties, and relations between the concepts, data, or entities that pertain to one, many, or all domains of discourse.
- **[Sementic Role Labelling](https://en.wikipedia.org/wiki/Semantic_role_labeling):** Process of assigning labels to words or phrases in a sentence that indicates their semantic role in the sentence, such as that of an agent, goal, or result.

## Technique

### Contraintes

- Ontologie en [TOML](https://en.wikipedia.org/wiki/TOML) (pas YAML beurk)
- [ROS 2 Humble](https://docs.ros.org/en/humble/index.html) (EOL : May 2027)
- Python 3.11 (EOL : October 2027)

### Structure

- [ExplorationLLM](./ExplorationLLM/README.md): Exploration de la piste des LLM et **état de l'art**
- [Full_Pipeline](./Full_Pipeline/README.md): **Pipeline complet de compréhension** mixant SRL, algorithmie et LLM (SpaCy)
- [GPSRGenDataset](./GPSRGenDataset/README.md): Exploration de pistes pour la génération la plus automatisée possible d'un dataset à jour (Robocup 2023)
- [ParseOntology](./ParseOntology/README.md): Librairie pour parser le fichier d'ontologie
- [SRL_SpaCy](./SRL_SpaCy/README.md): Exploration de la piste du Semantic role labelling (SpaCy)

## Autre


### Notre super modèle maison

Il sert à labeliser quelques goals pour l'instant mais on peu sans soucis penser à le train sur un plus grand dataset.
https://huggingface.co/julien-cpsn/BERT-GSPR-text-classification

### CICD

[Pipeline](https://cicd.planchon.dev/teams/main/pipelines/cpe.robot-project-mirror)

### Setup Jetson AGX Orin Devkit
1. OEM setup ubuntu
2. Setup eth0 jusqu'au prochain reboot
```sh
#!/bin/sh
ip link set eth0 down
ip link set eth0 address <cloned mac address>
ip link set eth0 up 
```
3. update & upgrade
4. Install `htop`, `build-essential`
5. Setup nvidia https://developer.nvidia.com/embedded/learn/get-started-jetson-agx-orin-devkit
6. Ajout cuda au PATH : `echo 'export PATH="$PATH:/usr/local/cuda/bin"' >> ~/.bashrc`
7. Monitor jetson usage : https://rnext.it/jetson_stats/
