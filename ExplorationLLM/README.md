# Exploration de la piste des LLM

## Pistes
- [LLM fonctionnel via un model fine-tuned](./ExplorationLlama2/README.md)
- [Spacy et LLM](./LlmSpacy/README.md)

## gpsr-command-understanding
### Phrases de test
```
Take the tray and put it on the desk

Tell me how many people are in the corridor

Could you meet Robin at the dining table and follow her to the dining room

Could you grasp the tray from the side table and bring it to me

Please follow Robin from the entrance to the bedroom

Give me the bowl

Please Tell me how many tableware there are on the bookcase

Take the orange from the dining room to the counter

Grasp the tray and put it on the dining table

Greet Francis at the bed and lead her to her uber
```

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

### `Take the tray and put it on the desk`

| Version LLM                                | Résultat                                                 | Durée (cold) |
| ------------------------------------------ | -------------------------------------------------------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( is_a $1 \" <object> \" ) ) ) )` |   3.45s           |
| glove_seq2seq                              |                                              `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ) \" <location> \" )`            |        3.15s      |
| seq2seq                                    |                                                          |              |
| albert-base-v2transformer_seq2seq          |                                                          |              |
| bert-base-uncasedtransformer_seq2seq       |                                                          |              |
| bert-large-uncasedtransformer_seq2seq      |                                                          |              |
| distilbert-base-uncasedtransformer_seq2seq |                                                          |              |
| distilgpt2transformer_seq2seq              |                                                          |              |
| distilroberta-basetransformer_seq2seq      |                                                          |              |
| gpt2transformer_seq2seq                    |                                                          |              |
| roberta-basetransformer_seq2seq            |                                                          |              |
| xlnet-base-casedtransformer_seq2seq        |                                                          |              |

### `Tell me how many people are in the corridor`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               |  `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) ) )`        |  3.38s            |
| glove_seq2seq                              |  `( say ( count ( lambda $1 e ( person $1 ) ( standing $1 ) ( at $1 \" <location> \" ) ) ) )`        |  3.06s            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Could you meet Robin at the dining table and follow her to the dining room`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               |  `( say ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`   |  3.74s            |
| glove_seq2seq                              | `( follow ( lambda $1 e ( person $1 ) ( name $1 \" <name> \" ) ( at $1 \" <location> \" ) ) )`         |  3.06s            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Could you grasp the tray from the side table and bring it to me`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( lightest $1 ) ( at $1 \" <room> \" ) ) )`         |  3.53s            |
| glove_seq2seq                              |  `( bring ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`        |  3.02            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Please follow Robin from the entrance to the bedroom`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               |  `( follow ( lambda $1 e ( person $1 ) ( at $1 \" <location> \" ) ) )`        |  3.43s            |
| glove_seq2seq                              |   `UNKNOWN`       | 3.06s             |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Give me the bowl`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               |  `( bring ( lambda $1 e ( is_a $1 \" cereal \" ) ) )`        |   3.35s           |
| glove_seq2seq                              | `( pour ( lambda $1 e ( is_a $1 \" <object> \" ) ) )`         |  3.07s            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Please Tell me how many tableware there are on the bookcase`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               |  `( say ( count ( lambda $1 e ( lightest $1 ) ( at $1 \" <room> \" ) ) ) )`        |  3.42s            |
| glove_seq2seq                              |   `( say ( count ( lambda $1 e ( person $1 ) ( sitting $1 ) ( at $1 \" <location> \" ) ) ) )`       |   3.09s           |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Take the orange from the dining room to the counter`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               | `( say \" <whattosay> \" ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`         | 3.40s             |
| glove_seq2seq                              |  `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ( at $1 \" <location> \" ) ) \" <location> \" )`        |  3.08s            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Grasp the tray and put it on the dining table`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               | `( say ( lambda $1 e ( and ( is_a $1 \" <object> \" ) ) )`         |  3.44s            |
| glove_seq2seq                              | `( put ( lambda $1 e ( is_a $1 \" <object> \" ) ) \" <location> \" )`         |  3.08s            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

### `Greet Francis at the bed and lead her to her uber`

| Version LLM                                | Résultat | Durée (cold) |
| ------------------------------------------ | -------- | ------------ |
| elmo_seq2seq                               | `( say ( answer \" <question> \" ) ( lambda $1 e ( person $1 ) ( at $1 \" <room> \" ) ) )`         | 3.44s             |
| glove_seq2seq                              | `( say ( lambda $1 e ( thinnest $1 ) ( name $1 \" <name> \" ) ) )`         |  3.06s            |
| seq2seq                                    |          |              |
| albert-base-v2transformer_seq2seq          |          |              |
| bert-base-uncasedtransformer_seq2seq       |          |              |
| bert-large-uncasedtransformer_seq2seq      |          |              |
| distilbert-base-uncasedtransformer_seq2seq |          |              |
| distilgpt2transformer_seq2seq              |          |              |
| distilroberta-basetransformer_seq2seq      |          |              |
| gpt2transformer_seq2seq                    |          |              |
| roberta-basetransformer_seq2seq            |          |              |
| xlnet-base-casedtransformer_seq2seq        |          |              |

## Papier de Recherche
- [Language and Robotics: Complex SentenceUnderstanding](https://sci-hub.se/10.1007/978-3-030-27529-7_54)
- [Enabling human-like task identification from natural conversation](https://arxiv.org/abs/2008.10073)
- [Natural Spoken Instructions Understanding for Robot with Dependency Parsing](https://sci-hub.se/10.1109/CYBER46603.2019.9066566)
- [Mapping natural language procedures descriptions to linear temporal logic templates](https://link.springer.com/article/10.1007/s10489-023-04882-0)
- [Foundation Model based Open Vocabulary Task Planning andExecutive System for General Purpose Service Robots](https://arxiv.org/abs/2308.03357)
- [tagE: Enabling an Embodied Agent to Understand Human Instructions](https://arxiv.org/abs/2310.15605)
- [Neural Semantic Parsing with Anonymization for Command Understanding in General-Purpose Service Robots](https://arxiv.org/abs/1907.01115v1)

## Repository de Code
- [REL/SRL recherche italienne](./Research/NLP-Semantic-Role-Labeling/README.md) (source: https://github.com/andreabac3/NLP-Semantic-Role-Labeling)
- [tagE: Enabling an Embodied Agent to Understand Human Instructions](./Research/tagE/README.md) (source: https://github.com/csarkar/tagE)
- [LU4R: adaptive spoken Language Understanding For Robots](http://sag.art.uniroma2.it/lu4r.html)

## Datasets
- [Human Robot Interaction Corpus (HuRIC 2.1)](https://github.com/crux82/huric)
- [RoboCup@Home Command Generator](https://github.com/kyordhel/GPSRCmdGen)
- [Rockin - FBM3@Home: Speech Understanding](https://web.archive.org/web/20170603103044/http://thewiki.rockinrobotchallenge.eu/index.php?title=Datasets#FBM3.40Home:_Speech_Understanding)