# GPSRGenDataset
> Cette piste a été mise en pose le temps de réfléchir a quelle infos prioriser dans le dataset et comment les générer.

## TOC
- [GPSRGenDataset](#gpsrgendataset)
  - [TOC](#toc)
  - [Compatibilitée avec Huric](#compatibilitée-avec-huric)
  - [Génération de 10000 exemples avec GPSRGen 2023](#génération-de-10000-exemples-avec-gpsrgen-2023)
  - [Génération du dataset](#génération-du-dataset)
    - [Prérequis](#prérequis)
    - [Génération](#génération)
  - [Expérimentation du process d'une ligne](#expérimentation-du-process-dune-ligne)
    - [Prérequis](#prérequis-1)
    - [Process](#process)


## Compatibilitée avec [Huric](https://github.com/crux82/huric)
- Création d'une [template](./huric/huric-template.xml)
- Mapping des [types](./huric/huric_types.rs)
- Test de compatibilité: [test_prompt_processing](./tests/process-dataset/test_process-prompt_huric.py)
- Quelques frames de test d'Huric: [Robocup](./tests/huric_test_frame_dataset.csv)

## Génération de 10000 exemples avec GPSRGen 2023
- [raw_dataset.csv](./raw_dataset.csv)
- Commandes indexées par ID afin de pouvoir y faire référence même si on décide de ne traiter qu'une partie du dataset

## Génération du dataset
### Prérequis
- rust (et cargo): https://rustup.rs/
  - rust-script `cargo install rust-script`
- docker

### Génération
```sh
# Variables d'env par défaut
# GEN_COUNT = 1000 (nombre de générations)
# GPSR_CMDGEN_IMAGE = ghcr.io/joxcat/gpsrcmdgen-gpsr:v2023.2 (image docker de GPSRCmdGen)
# OUT_FILE = raw-dataset.csv
./gen-dataset.rs
```

## Expérimentation du process d'une ligne
### Prérequis
- python 3.11
- poetry (`pip install poetry`)

```sh
poetry env use 3.11
poetry install
```

### Process
```sh
echo 'go to the kitchen' | poetry run process-prompt.py
```