# Brain-experiment (wip name)
> Code from https://github.com/tvergho/sentence-transformers-burn
> Se base sur [la recherche sur l'état de l'art](../Research/README.md)
> **Mis en pose après 1j de travail par manque de temps**

## Process
1. Bert/Bart pour extraire les tâches, leur ordre et sur quelles tâches elles dépendent
2. Loop sur la récupération des informations manquantes/d'affinage des instructions
3. Bert/Bart pour extraire les paramètres
4. Traitement?

## Liens en vrac
### Dataset
- https://github.com/crux82/huric/tree/master

### ONNX
- https://github.com/NVIDIA/TensorRT/tree/main/tools/onnx-graphsurgeon/examples
- https://github.com/NVIDIA/TensorRT/tree/main/tools/onnx-graphsurgeon
- https://onnx.ai/onnx/api/compose.html
- https://github.com/onnx/models/blob/main/validated/text/machine_comprehension/t5/model/t5-decoder-with-lm-head-12.onnx
- https://github.com/onnx/models/blob/main/validated/vision/classification/resnet/model/resnet50-v2-7.onnx

### Spacy
- https://demos.explosion.ai/displacy?text=Robot%20please%20go%20to%20the%20couch%2C%20meet%20Robin%2C%20and%20guide%20him&model=en_core_web_sm&cpu=0&cph=0
- https://github.com/explosion/spaCy/blob/master/spacy/glossary.py
- https://spacy.io/api/top-level#spacy.explain
