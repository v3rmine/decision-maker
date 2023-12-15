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

### `Tell me how many people are in the corridor`

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

### `Could you meet Robin at the dining table and follow her to the dining room`

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

### `Could you grasp the tray from the side table and bring it to me`

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

### `Please follow Robin from the entrance to the bedroom`

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

### `Give me the bowl`

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

### `Please Tell me how many tableware there are on the bookcase`

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

### `Take the orange from the dining room to the counter`

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

### `Grasp the tray and put it on the dining table`

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

### `Greet Francis at the bed and lead her to her uber`

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