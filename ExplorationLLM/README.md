# Exploration de la piste des LLM

## TOC
- [Exploration de la piste des LLM](#exploration-de-la-piste-des-llm)
  - [TOC](#toc)
  - [Pistes personnelles](#pistes-personnelles)
  - [Repos de code en rapport avec le projet et préparés pour un usage avec poetry](#repos-de-code-en-rapport-avec-le-projet-et-préparés-pour-un-usage-avec-poetry)
  - [Datasets](#datasets)
  - [Résultats](#résultats)
    - [Phrases de test](#phrases-de-test)
    - [Trained LLM List](#trained-llm-list)
    - [`Take the tray and put it on the desk`](#take-the-tray-and-put-it-on-the-desk-index)
    - [`Tell me how many people are in the corridor`](#tell-me-how-many-people-are-in-the-corridor-index)
    - [`Could you meet Robin at the dining table and follow her to the dining room`](#could-you-meet-robin-at-the-dining-table-and-follow-her-to-the-dining-room-index)
    - [`Could you grasp the tray from the side table and bring it to me`](#could-you-grasp-the-tray-from-the-side-table-and-bring-it-to-me-index)
    - [`Please follow Robin from the entrance to the bedroom`](#please-follow-robin-from-the-entrance-to-the-bedroom-index)
    - [`Give me the bowl`](#give-me-the-bowl-index)
    - [`Please Tell me how many tableware there are on the bookcase`](#please-tell-me-how-many-tableware-there-are-on-the-bookcase-index)
    - [`Take the orange from the dining room to the counter`](#take-the-orange-from-the-dining-room-to-the-counter-index)
    - [`Grasp the tray and put it on the dining table`](#grasp-the-tray-and-put-it-on-the-dining-table-index)
    - [`Greet Francis at the bed and lead her to her uber`](#greet-francis-at-the-bed-and-lead-her-to-her-uber-index)

## Pistes personnelles
- [Finetuning LLM](./ExplorationLlama2/README.md): Traitement avec LLM seul via un model fine-tuned
- [Research](./Research/README.md): Analyse de l'état de l'art
- [brain-experiment](./brain-experiment/README.md): Finetunage de Bert + algorithmie

## Repos de code en rapport avec le projet et préparés pour un usage avec poetry
- [GRUT v1: Grounded language Understanding via Transformers](./Research/grutv1/README.md) (source: https://github.com/crux82/grut) (version avec uniquement compréhension du language naturel)
- [GRUT v2: Grounded language Understanding via Transformers](./Research/grutv1/README.md) (source: https://github.com/crux82/grut) (version avec liens entre paramètres et entitées d'ontologie)
- [GPSR Command Understanding](./Research/gpsr-command-understanding/README.md) (source: https://github.com/nickswalker/gpsr-command-understanding)
- [REL/SRL recherche italienne](./Research/NLP-Semantic-Role-Labeling/README.md) (source: https://github.com/andreabac3/NLP-Semantic-Role-Labeling)
- [tagE: Enabling an Embodied Agent to Understand Human Instructions](./Research/tagE/README.md) (source: https://github.com/csarkar/tagE)
- [LU4R: adaptive spoken Language Understanding For Robots](http://sag.art.uniroma2.it/lu4r.html)

## Datasets
- [Human Robot Interaction Corpus (HuRIC 2.1)](https://github.com/crux82/huric)
- [RoboCup@Home Command Generator](https://github.com/kyordhel/GPSRCmdGen)
- [Rockin - FBM3@Home: Speech Understanding](https://web.archive.org/web/20170603103044/http://thewiki.rockinrobotchallenge.eu/index.php?title=Datasets#FBM3.40Home:_Speech_Understanding)

## Résultats
### Phrases de test
- [Take the tray and put it on the desk](#take-the-tray-and-put-it-on-the-desk-index)
- [Tell me how many people are in the corridor](#tell-me-how-many-people-are-in-the-corridor-index)
- [Could you meet Robin at the dining table and follow her to the dining room](#could-you-meet-robin-at-the-dining-table-and-follow-her-to-the-dining-room-index)
- [Could you grasp the tray from the side table and bring it to me](#could-you-grasp-the-tray-from-the-side-table-and-bring-it-to-me-index)
- [Please follow Robin from the entrance to the bedroom](#please-follow-robin-from-the-entrance-to-the-bedroom-index)
- [Give me the bowl](#give-me-the-bowl-index)
- [Please Tell me how many tableware there are on the bookcase](#please-tell-me-how-many-tableware-there-are-on-the-bookcase-index)
- [Take the orange from the dining room to the counter](#take-the-orange-from-the-dining-room-to-the-counter-index)
- [Grasp the tray and put it on the dining table](#grasp-the-tray-and-put-it-on-the-dining-table-index)
- [Greet Francis at the bed and lead her to her uber](#greet-francis-at-the-bed-and-lead-her-to-her-uber-index)

### Trained LLM List

| Version LLM                                | Durée d'entrainement      | Poid     | Best Epoch         |
| ------------------------------------------ | ------------------------- | -------- | ------------------ |
| elmo_seq2seq                               | 4min48s (2.11s/epoch)     | 1.5G     | 106/136 (78%)      |
| glove_seq2seq                              | 1min50s (**0.74s**/epoch) | **66M**  | 137/149 (92%)      |
| seq2seq                                    | 4min32s (2.21s/epoch)     | **66M**  | **93/123**  (76%)  |
| albert-base-v2transformer_seq2seq          | 3min02s (1.22s/epoch)     | 273M     | 135/149 (91%)      |
| bert-base-uncasedtransformer_seq2seq       | 3min19s (1.47s/epoch)     | 1.7G     | 105/135 (78%)      |
| bert-large-uncasedtransformer_seq2seq      | 7min16s (**2.93s**/epoch) | **5.1G** | 139/149 (93%)      |
| distilbert-base-uncasedtransformer_seq2seq | 2min25s (1.16s/epoch)     | 1.1G     | 95/125  (76%)      |
| distilgpt2transformer_seq2seq              | 3min15s (1.31s/epoch)     | 1.4G     | 129/149 (87%)      |
| distilroberta-basetransformer_seq2seq      | 2min51s (1.27s/epoch)     | 1.3G     | 105/135 (78%)      |
| gpt2transformer_seq2seq                    | 4min    (1.61s/epoch)     | 1.5G     | 148/149 (99%)      |
| roberta-basetransformer_seq2seq            | 3min50s (1.54s/epoch)     | 1.8G     | 121/149 (81%)      |
| xlnet-base-casedtransformer_seq2seq        | 4min07s (1.66s/epoch)     | 1.4G     | **149/149** (100%) |
| grut-v1-bart   | 15min10s | 533M | NA |
| grut-v1-bart-grut   | 28min32s | 533M | NA |
| grut-v1-mt5   | 1h22min | 2.2G | NA |
| grut-v1-mt5-grut   | 101m | 2.2G | NA |
| grut-v2-bart   | 14min44s | 533M | NA |
| grut-v2-bart-grut   | 32min59s | 533M | NA |
| grut-v2-t5   | 1h11min | 2.2G | NA |
| grut-v2-t5-grut   | 1h26min | 2.2G | NA |

### `Take the tray and put it on the desk` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                        | Durée (cold) |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( is_a $1 \" <object> \" ) ) ) )`                                    | 3.45s        |
| glove_seq2seq                              | `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ) \" <location> \" )`                           | 3.15s        |
| seq2seq                                    | `( say ( lambda $1 e ( thinnest $1 3 ) ( at $1 \" <location> \" ) ) )`                          | 3.05s        |
| albert-base-v2transformer_seq2seq          | `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ) \" <location> \" )`                           | 139ms        |
| bert-base-uncasedtransformer_seq2seq       | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`                                          | 190ms        |
| bert-large-uncasedtransformer_seq2seq      | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ) ( lambda $1 e ( is_a $1 \" bowl \" ) ) )`      | 205ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ) ( lambda $1 e ( is_a $1 \" bowl \" ) ) )`      | 189ms        |
| distilgpt2transformer_seq2seq              | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <location> \" ) ) ) )`                    | 151ms        |
| distilroberta-basetransformer_seq2seq      | `( bring ( lambda $1 e ( and ( heaviest $1 ) ) \" <location> \" )`                              | 186ms        |
| gpt2transformer_seq2seq                    | `( say ( lambda $1 e ( lambda $2 e ( person $2 ) ( gender $2 $1 ) ( at $2 \" <room> \" ) ) ) )` | 193ms        |
| roberta-basetransformer_seq2seq            | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`                                          | 196ms        |
| xlnet-base-casedtransformer_seq2seq        | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) UNKNOWN )`                      | 157ms        |
| grut-v1-bart | `["TAKING(Theme(Theme('the tray')) - PLACING(Theme"]` | 4s |
| grut-v1-bart-grut | `["ATTACHING(Item('the tray')) - PLACING(Theme('"]` | 4s |
| grut-v1-mt5 | `["TAKING(Theme('the tray')) - PLACING(Theme('it'), Goal"]` | 11.7s |
| grut-v1-mt5-grut | `["TAKING(Theme('the tray')) - PLACING(Theme('it'), Goal"]` | 11.3s |
| grut-v2-bart | `["TAKING(Theme('it'), Goal('on the desk')) - PLAC"]` | 3s |
| grut-v2-bart-grut | `["TAKING(Theme('it'), Goal('on the desk'))"]` | 3.21s |
| grut-v2-mt5 | `["TAKING(Theme('the tray')) - PLACING(Theme('it'), Goal"]` | 10.7s |
| grut-v2-mt5-grut | `["TAKING(Theme('the tray')) - PLACING(Theme('it'), Goal"]` | 12.4s |

### `Tell me how many people are in the corridor` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                          | Durée (cold) |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) ) )`                          | 3.38s        |
| glove_seq2seq                              | `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <location> \" ) ) ) )`      | 3.06s        |
| seq2seq                                    | `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <room> \" ) ) ) )`          | 3.97s        |
| albert-base-v2transformer_seq2seq          | `( say ( count ( lambda $1 e ( person $1 ) ( female $1 ) ( at $1 \" <room> \" ) ) ) )`            | 153ms        |
| bert-base-uncasedtransformer_seq2seq       | `( say ( count ( lambda $1 e ( person $1 ) ( lying $1 ) ( at $1 \" <room> \" ) ) ) )`             | 148ms        |
| bert-large-uncasedtransformer_seq2seq      | `( say ( count ( lambda $1 e ( person $1 ) ( sitting $1 ) ( at $1 \" <room> \" ) ) ) )`           | 189ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( say ( count ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <room> \" ) ) ) )`              | 124ms        |
| distilgpt2transformer_seq2seq              | `( say ( count ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) ) )`                          | 135ms        |
| distilroberta-basetransformer_seq2seq      | `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <room> \" ) ) ) )`          | 152ms        |
| gpt2transformer_seq2seq                    | `( say ( count ( lambda $1 e ( person $1 ) ( female $1 ) ( at $1 \" <room> \" ) ) ) )`            | 164ms        |
| roberta-basetransformer_seq2seq            | `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <room> \" ) ) ) )`    138ms |              |
| xlnet-base-casedtransformer_seq2seq        | `( say ( count ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <room> \" ) ) ) )`              | 171ms        |
| grut-v1-bart | `["BRINGING(Agent('me'), Theme('how many people'), Location('in"]` | 4s |
| grut-v1-bart-grut | `["BEING_LOCATED(Cognizer('me'), Location('where'), Location"]` | 4s |
| grut-v1-mt5 | `["BEING_LOCATED(Theme('many people'), Location('in the corridor'))"]` | 11.7s |
| grut-v1-mt5-grut | `["TAKING(Theme('many people'), Location('in the corridor'))"]` | 10.8s |
| grut-v2-bart | `["BRINGING(Beneficiary('me'), Theme('many people'), Location('in"]` | 3s |
| grut-v2-bart-grut | `["BRINGING(Agent('you'), Location('in the corridor'))"]` | 3.13s |
| grut-v2-mt5 | `["CHANGE_DIRECTION(Theme('you'), Location('in the corridor'))"]` | 11.2s |
| grut-v2-mt5-grut | `["CHANGE_DIRECTION(Phenomenon('many people'), Area('on the corridor"]` | 12.4s |

### `Could you meet Robin at the dining table and follow her to the dining room` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                                  | Durée (cold) |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`                                            | 3.74s        |
| glove_seq2seq                              | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`            | 3.06s        |
| seq2seq                                    | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`            | 3.96s        |
| albert-base-v2transformer_seq2seq          | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) \" <location> \" )`                       | 285ms        |
| bert-base-uncasedtransformer_seq2seq       | `( lambda $1 e ( sequence ( follow ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )` | 169ms        |
| bert-large-uncasedtransformer_seq2seq      | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <room> \" ) ) )`                | 179ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( sequence ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`          | 135ms        |
| distilgpt2transformer_seq2seq              | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) )`                                    | 137ms        |
| distilroberta-basetransformer_seq2seq      | `( go \" <room> \" )`                                                                                     | 136ms        |
| gpt2transformer_seq2seq                    | `( say ( count ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <room> \" ) ) ) )`                      | 174ms        |
| roberta-basetransformer_seq2seq            | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`            | 158ms        |
| xlnet-base-casedtransformer_seq2seq        | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) UNKNOWN )`                                | 169ms        |
| grut-v1-bart | `["COTHEME(Theme('you'), Goal('at the dining table'))"]` | 3.5s |
| grut-v1-bart-grut | `["MOTION(Theme('you'), Goal('to the dining table')) -"]` | 4s |
| grut-v1-mt5 | `["MOTION(Theme('you'), Goal('at the dining table')) - COTH"]` | 11.8s |
| grut-v1-mt5-grut | `["MOTION(Theme('you'), Goal('to the dining room'))"]` | 10.9s |
| grut-v2-bart | `["COTHEME(Theme('you'), Cotheme('Robin at the dining"]` | 3s |
| grut-v2-bart-grut | `["MOTION(Theme('you'), Goal('at the dining table')) -"]` | 3.22s |
| grut-v2-mt5 | `["MOTION(Theme('you'), Goal('at the dining table')) - COTH"]` | 11.3s |
| grut-v2-mt5-grut | `["MOTION(Theme('Robin at the dining table')) - COTHEME(Co"]` | 12s |

### `Could you grasp the tray from the side table and bring it to me` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                        | Durée (cold) |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) )`                          | 3.53s        |
| glove_seq2seq                              | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`                                          | 3.02s        |
| seq2seq                                    | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`  | 3.19s        |
| albert-base-v2transformer_seq2seq          | `( bring ( lambda $1 e ( person $1 ) ( at $1 \" <location> \" ) ) )`                            | 120ms        |
| bert-base-uncasedtransformer_seq2seq       | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <location> \" ) ) )`               | 128ms        |
| bert-large-uncasedtransformer_seq2seq      | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ) )`                                             | 166ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <location> \" ) ) )`               | 134ms        |
| distilgpt2transformer_seq2seq              | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <location> \" ) ) ) )`                    | 118ms        |
| distilroberta-basetransformer_seq2seq      | `( bring ( lambda $1 e ( rightmost $1 \" <location> \" ) ) )`                                   | 83ms         |
| gpt2transformer_seq2seq                    | `( say ( lambda $1 e ( lambda $2 e ( person $2 ) ( gender $2 $1 ) ( at $2 \" <room> \" ) ) ) )` | 179ms        |
| roberta-basetransformer_seq2seq            | `( bring ( lambda $1 e ( person $1 ) ( at $1 \" <location> \" ) ) )`                            | 133ms        |
| xlnet-base-casedtransformer_seq2seq        | `( bring ( lambda $1 e ( largest $1 ) ) \" <location> \" )`                                     | 135ms        |
| grut-v1-bart | `["MANIPULATION(Entity('you'), Theme('the tray'), Source('from"]` | 4s |
| grut-v1-bart-grut | `["MANIPULATION(Agent('you'), Device('the tray'), Source('from"]` | 4s |
| grut-v1-mt5 | `["GIVING(Agent('you'), Theme('the tray'), Source('from the side table"]` | 11.7s |
| grut-v1-mt5-grut | `["GIVING(Agent('you'), Theme('the tray'), Source('from the side table"]` | 11.2s |
| grut-v2-bart | `["MANIPULATION(Entity('you'),Entity('the tray'), Source('from"]` | 3s |
| grut-v2-bart-grut | `["MANIPULATION(Entity('the tray'), Source('from the side table'"]` | 3.16s |
| grut-v2-mt5 | `["MANIPULATION(Entity('you'), Theme('the tray'), Source('from the side"]` | 11.4s |
| grut-v2-mt5-grut | `["MANIPULATION(Entity('the tray'), Source('from the side table')) -"]` | 12s |

### `Please follow Robin from the entrance to the bedroom` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                       | Durée (cold) |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( follow ( lambda $1 e ( person $1 ) ( at $1 \" <location> \" ) ) )`                          | 3.43s        |
| glove_seq2seq                              | `UNKNOWN`                                                                                      | 3.06s        |
| seq2seq                                    | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )` | 3.13s        |
| albert-base-v2transformer_seq2seq          | `( go \" <room> \" )`                                                                          | 102ms        |
| bert-base-uncasedtransformer_seq2seq       | `( go \" <room> \" )`                                                                          | 109ms        |
| bert-large-uncasedtransformer_seq2seq      | `( follow ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`                              | 276ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( say \" <room> \" )`                                                                         | 128ms        |
| distilgpt2transformer_seq2seq              | `( go \" <room> \" )`                                                                          | 117ms        |
| distilroberta-basetransformer_seq2seq      | `( go \" <room> \" )`                                                                          | 137ms        |
| gpt2transformer_seq2seq                    | `( go \" <room> \" )`                                                                          | 149ms        |
| roberta-basetransformer_seq2seq            | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`  | 134ms        |
| xlnet-base-casedtransformer_seq2seq        | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) )`                            | 132ms        |
| grut-v1-bart | `["COTHEME(Cotheme('Robin'), Path('from the entrance to"]` | 4s |
| grut-v1-bart-grut | `["COTHEME(Cotheme('Robin'), Path('from the entrance to"]` | 4s |
| grut-v1-mt5 | `["COTHEME(Cotheme('Robin'), Path('from the entrance to the bedroom'))"]` | 11.7s |
| grut-v1-mt5-grut | `["COTHEME(Cotheme('Robin'), Path('from the entrance to the bedroom'))"]` | 11.2s |
| grut-v2-bart | `["COTHEME(Cotheme('Robin'), Path('from the entrance to"]` | 3s |
| grut-v2-bart-grut | `["COTHEME(Cotheme('Robin'), Path('from the entrance to"]` | 3.15s |
| grut-v2-mt5 | `["COTHEME(Cotheme('Robin'), Path('from the entrance to the bedroom'))"]` | 11.4s |
| grut-v2-mt5-grut | `["COTHEME(Cotheme('Robin'), Path('from the entrance'), Goal('to"]` | 12.4s |

### `Give me the bowl` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                      | Durée (cold) |
| ------------------------------------------ | ------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( bring ( lambda $1 e ( is_a $1 \" cereal \" ) ) )`          | 3.35s        |
| glove_seq2seq                              | `( pour ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`         | 3.07s        |
| seq2seq                                    | `( go \" <room> \" )`                                         | 3.10s        |
| albert-base-v2transformer_seq2seq          | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`        | 131ms        |
| bert-base-uncasedtransformer_seq2seq       | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`        | 136ms        |
| bert-large-uncasedtransformer_seq2seq      | `( bring ( lambda $1 e ( is_a $1 \" bowl \" ) ) )`            | 126ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( bring ( lambda $1 e ( is_a $1 \" <category> \" ) ) )`      | 80ms         |
| distilgpt2transformer_seq2seq              | `( bring ( lambda $1 e ( rightmost $1 \" <location> \" ) ) )` | 98ms         |
| distilroberta-basetransformer_seq2seq      | `( bring ( lambda $1 e ( is_a $1 \" <location> \" ) ) )`      | 76ms         |
| gpt2transformer_seq2seq                    | `( bring ( lambda $1 e ( lightest $1 ) ) \" <location> \" )`  | 111ms        |
| roberta-basetransformer_seq2seq            | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`        | 97ms         |
| xlnet-base-casedtransformer_seq2seq        | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`        | 97ms         |
| grut-v1-bart | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 4s |
| grut-v1-bart-grut | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 4s |
| grut-v1-mt5 | `["GIVING(Beneficiary('me'), Theme('the bowl'))"]` | 11.2s |
| grut-v1-mt5-grut | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 10.8s |
| grut-v2-bart | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 3s |
| grut-v2-bart-grut | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 3s |
| grut-v2-mt5 | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 10.7s |
| grut-v2-mt5-grut | `["GIVING(Recipient('me'), Theme('the bowl'))"]` | 11.95s |

### `Please Tell me how many tableware there are on the bookcase` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                    | Durée (cold) |
| ------------------------------------------ | ------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( count ( lambda $1 e ( lightest $1 ) ( at $1 \" <room> \" ) ) ) )`                  | 3.42s        |
| glove_seq2seq                              | `( say ( count ( lambda $1 e ( person $1 ) ( sitting $1 ) ( at $1 \" <location> \" ) ) ) )` | 3.09s        |
| seq2seq                                    | `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <room> \" ) ) ) )`    | 3.10s        |
| albert-base-v2transformer_seq2seq          | `( say ( lambda $1 e ( and ( is_a $1 \" <category> \" ) ( at $1 \" <location> \" ) ) ) )`   | 130ms        |
| bert-base-uncasedtransformer_seq2seq       | `( say ( count ( lambda $1 e ( person $1 ) ( female $1 ) ( at $1 \" <room> \" ) ) ) )`      | 158ms        |
| bert-large-uncasedtransformer_seq2seq      | `( say ( count ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <room> \" ) ) ) )`       | 203ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <room> \" ) ) ) )`    | 167ms        |
| distilgpt2transformer_seq2seq              | `( say ( count ( lambda $1 e ( person $1 ) ( female $1 ) ( at $1 \" <room> \" ) ) ) )`      | 141ms        |
| distilroberta-basetransformer_seq2seq      | `( say ( count ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) ) )`                    | 140ms        |
| gpt2transformer_seq2seq                    | `( say ( count ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <room> \" ) ) ) )`        | 153ms        |
| roberta-basetransformer_seq2seq            | `( say ( count ( lambda $1 e ( person $1 ) ( sitting $1 ) ( at $1 \" <room> \" ) ) ) )`     | 146ms        |
| xlnet-base-casedtransformer_seq2seq        | `( say ( count ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <location> \" ) ) ) )`    | 162ms        |
| grut-v1-bart | `["BRINGING(Agent('me'), Theme('how many tableware'), Location('"]` | 4s |
| grut-v1-bart-grut | `["BRINGING(Beneficiary('me'), Theme('how many tableware'), Location"]` | 4s |
| grut-v1-mt5 | `["BEING_LOCATED(Theme('many tableware'), Location('on the bookcase'))"]` | 11.7s |
| grut-v1-mt5-grut | `["ATTACHING(Item('the tableware'), Location('on the bookcase'))"]` | 11.5s |
| grut-v2-bart | `["BRINGING(Beneficiary('me'), Theme('many tableware'), Location('"]` | 3s |
| grut-v2-bart-grut | `["BRINGING(Agent('you'), Theme('many tableware')) - BE"]` | 3.17s |
| grut-v2-mt5 | `["CHANGE_OPERATIONAL_STATE(Agent('you'), Device('the tableware'),"]` | 11.3s |
| grut-v2-mt5-grut | `["BRINGING(Theme('many tableware'), Location('on the bookcase'))"]` | 12.38s |

### `Take the orange from the dining room to the counter` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                                       | Durée (cold) |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say \" <whattosay> \" ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`                               | 3.40s        |
| glove_seq2seq                              | `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <location> \" ) ) \" <location> \" )`               | 3.08s        |
| seq2seq                                    | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) \" <location> \" )` | 3.10s        |
| albert-base-v2transformer_seq2seq          | `( put ( lambda $1 e ( person $1 ) ( at $1 \" <location> \" ) ) \" <location> \" )`                            | 118ms        |
| bert-base-uncasedtransformer_seq2seq       | `( say ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <room> \" ) ) )`                                    | 113ms        |
| bert-large-uncasedtransformer_seq2seq      | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <room> \" ) ) )`                                  | 229ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ( at $1 \" <room> \" ) ) )`                                     | 136ms        |
| distilgpt2transformer_seq2seq              | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ) ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`       | 149ms        |
| distilroberta-basetransformer_seq2seq      | `( go \" <room> \" )`                                                                                          | 124ms        |
| gpt2transformer_seq2seq                    | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) ) )`                                       | 186ms        |
| roberta-basetransformer_seq2seq            | `UNKNOWN`                                                                                                      | 140ms        |
| xlnet-base-casedtransformer_seq2seq        | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`                                                         | 170ms        |
| grut-v1-bart | `["BRINGING(Theme('the orange'), Source('from the dining room'), Goal"]` | 4s |
| grut-v1-bart-grut | `["BRINGING(Theme('the orange'), Source('from the dining room'), Goal"]` | 4s |
| grut-v1-mt5 | `["TAKING(Theme('the orange'), Source('from the dining room'), Goal('to"]` | 11.7s |
| grut-v1-mt5-grut | `["TAKING(Theme('the orange'), Source('from the dining room'), Goal('to"]` | 11.9s |
| grut-v2-bart | `["BRINGING(Theme('the orange'), Source('from the dining room'), Goal"]` | 3s |
| grut-v2-bart-grut | `["BRINGING(Theme('the orange'), Source('from the dining room'), Goal"]` | 3.19s |
| grut-v2-mt5 | `["BRINGING(Theme('the orange'), Source('from the dining room'), Goal('"]` | 11.3s |
| grut-v2-mt5-grut | `["BRINGING(Theme('the orange'), Source('from the dining room'), Goal('"]` | 12.4s |

### `Grasp the tray and put it on the dining table` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                        | Durée (cold) |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( is_a $1 \" <object> \" ) ) )`                                      | 3.44s        |
| glove_seq2seq                              | `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ) \" <location> \" )`                           | 3.08s        |
| seq2seq                                    | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) )`                              | 3.32s        |
| albert-base-v2transformer_seq2seq          | `( put ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) \" <location> \" )`               | 120ms        |
| bert-base-uncasedtransformer_seq2seq       | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`                                          | 206ms        |
| bert-large-uncasedtransformer_seq2seq      | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ) ( lambda $1 e ( is_a $1 \" bowl \" ) ) )`      | 173ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( pour ( lambda $1 e ( is_a $1 \" cereal \" ) ) ( lambda $1 e ( is_a $1 \" bowl \" ) ) )`      | 168ms        |
| distilgpt2transformer_seq2seq              | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) )`                          | 122ms        |
| distilroberta-basetransformer_seq2seq      | `( bring ( lambda $1 e ( and ( heaviest $1 ) ( at $1 \" <location> \" ) ) ) )`                  | 110ms        |
| gpt2transformer_seq2seq                    | `( say ( lambda $1 e ( lambda $2 e ( person $2 ) ( gender $2 $1 ) ( at $2 \" <room> \" ) ) ) )` | 164ms        |
| roberta-basetransformer_seq2seq            | `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ) \" <location> \" )`                           | 160ms        |
| xlnet-base-casedtransformer_seq2seq        | `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`                                          | 164ms        |
| grut-v1-bart | `["CLOSURE(Entity('the tray')) - PLACING(Theme('"]` | 4s |
| grut-v1-bart-grut | `["MANIPULATION(Entity('the tray')) - PLACING(Theme"]` | 4s |
| grut-v1-mt5 | `["PLACING(Theme('the tray')) - PLACING(Theme('it'), Goal"]` | 11.7s |
| grut-v1-mt5-grut | `["PLACING(Theme('the tray')) - PLACING(Theme('it'), Goal"]` | 11.6s |
| grut-v2-bart | `["MANIPULATION(Entity('it'), Goal('on the dining table'))"]` | 3s |
| grut-v2-bart-grut | `["TAKING(Theme('it'), Goal('on the dining table'))"]` | 3.16s |
| grut-v2-mt5 | `["MANIPULATION(Entity('the tray')) - PLACING(Theme('it'),"]` | 11.2s |
| grut-v2-mt5-grut | `["MANIPULATION(Entity('the tray')) - PLACING(Theme('it'),"]` | 12.5s |

### `Greet Francis at the bed and lead her to her uber` ([Index](#phrases-de-test))

| Version LLM                                | Résultat                                                                                                                | Durée (cold) |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( answer \" <question> \" ) ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`                              | 3.44s        |
| glove_seq2seq                              | `( say ( lambda $1 e ( thinnest $1 ) ( name $1 \" <name> \" ) ) )`                                                      | 3.06s        |
| seq2seq                                    | `( say ( answer \" <question> \" ) ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )` | 3.12s        |
| albert-base-v2transformer_seq2seq          | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) )`                                                      | 140ms        |
| bert-base-uncasedtransformer_seq2seq       | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) )`                                                      | 149ms        |
| bert-large-uncasedtransformer_seq2seq      | `( guide ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <room> \" ) ) )`                                            | 275ms        |
| distilbert-base-uncasedtransformer_seq2seq | `( say \" <whattosay> \" ( lambda $1 e ( person $1 ) ( female $1 ) ( at $1 \" <room> \" ) ) )`                          | 149ms        |
| distilgpt2transformer_seq2seq              | `( bring ( lambda $1 e ( leftmost $1 \" <location> \" ) ) )`                                                            | 125ms        |
| distilroberta-basetransformer_seq2seq      | `( say \" <whattosay> \" )`                                                                                             | 132ms        |
| gpt2transformer_seq2seq                    | `( say ( count ( lambda $1 e ( person $1 ) ( male $1 ) ( at $1 \" <room> \" ) ) ) )`                                    | 164ms        |
| roberta-basetransformer_seq2seq            | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) )`                                                      | 121ms        |
| xlnet-base-casedtransformer_seq2seq        | `( guide ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ) \" <location> \" )`                                     | 126ms        |
| grut-v1-bart | `["Greet Francis at the bed')) - BRINGING(Theme('her'),"]` | 4s |
| grut-v1-bart-grut | `["GOTHEME(Phenomenon('at the bed')) - BR"]` | 4s |
| grut-v1-mt5 | `["BEING_LOCATED(Theme('Francis at the bed')) - LOCATING("]` | 11.7s |
| grut-v1-mt5-grut | `["TAKING(Theme('Francis at the bed')) - DIRECTION(Direction('"]` | 11.4s |
| grut-v2-bart | `["GIVING(Recipient('me'), Goal('at the bed')) -"]` | 3s |
| grut-v2-bart-grut | `["GIVING(Recipient('her'), Goal('to her uber'))"]` | 3s |
| grut-v2-mt5 | `["RELEASING(Theme(' Francis at the bed')) - LOCATING(Sought_"]` | 11.3s |
| grut-v2-mt5-grut | `["Greet Francis at the bed')) - CHANGE_DIRECTION(Direction('her'),"]` | 12.6s |
