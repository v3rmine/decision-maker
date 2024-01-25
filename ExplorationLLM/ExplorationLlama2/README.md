# Exploration LLM
> Cette piste a été abandonnée pour des raison du manque de temps pour faire un dataset correct, ainsi que le temps d'inférence de Llama2 qui est trop élevé sur le Jetson.

## Exploration solution llama2
- Code pour appeller le serveur de llama.cpp : [llama2-binding-function.py](./llama2-binding-function.py)
- Code pour invoquer directement le modèle avec Python : [llama2-binding-function.py](./llama2-binding-function.py)

### Objectif
#### Prompt utilisateur
```json
{ "prompt":"Go to the kitchen and grab a banana" }
```

#### Réponse assistant
```json
[
    {
        "function": "get_location",
        "args": [{ "location_name": "kitchen" }],
        "store_result": "$kitchen_location"
    }, {
        "function": "goto_location",
        "args": [{ "to": "$kitchen_location" }]
    }, {
        "function": "search_element",
        "args": [{ "element": "banana" }],
        "store_result": "$banana_location"
    }, {
        "function": "grab_element",
        "args": [{ "where": "$banana_location" }]
    }
]
```

### Setup llama
1. `git clone https://github.com/ggerganov/llama.cpp ~/Git/llama.cpp`
2. `cd ~/Git/llama.cpp`
3. `sed -i 's|NVCC_FLAGS += -arch=native|NVCC_FLAGS += -arch=compute_87|' Makefile` (`compute_87` is the corresponding arch of Jetson ORIN)
4. `make LLAMA_CUBLAS=1`

### Choix taille modèle llama
> Temps d'inférence basé sur le Jetson

- Q3_K_M => ~10s (le plus proche du temps objectif de 5s max)
- Q4_K_M => ~40s
- Q5_K_M => ~1min30

### Choix modèle llama (en Q3_K_M, 3bits)
- https://huggingface.co/TheBloke/claude2-alpaca-7B-GGUF => objet JSON exploitable et comprends bien les consignes simples, compliqué de gérer l'historique
- https://huggingface.co/TheBloke/Wizard-Vicuna-7B-Uncensored-GGUF => renvoie un objet JSON exploitable facilement, mais beaucoup de mal à comprendre les consignes
- https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF => optimisé pour le chat, compliquer d'avoir un retour exploitable
- https://huggingface.co/TheBloke/open-llama-3b-v2-wizard-evol-instuct-v2-196k-GGUF => bug dans le serveur de llama.cpp, impossible de lancer des modèles avec une plage de contexte supérieure à 512.

### Retours
Les premiers retour sont concluents, nous pensons qu'avec un TPU optimisé pour la génération de texte, un modèle généraliste finetuné sur des exemples de requêtes avec retours et contraint avec le format JSON. Il est possible de générer une chaine d'appel depuis un simple prompt en language naturel. Cependant entre la contrainte de temps et celle de puissance, nous ne poursuivrons pas cette piste pour la suite du projet.

### Recherche autour de Rocket3-b (temps d'inférence très court)
prompt:
```
<pre>
<|im_start|>user
I will send a task and you will reply using only the known functions.
In case of any missing function the you respond with just "ERROR".
You know the following functions:
- `GET_CURRENT_LOCATION(): LOCATION` Get the current location
- `GO(to: LOCATION)` Move to some coordinates
- `GET_LOCATION(location_name: STRING): LOCATION` Return the location associated with a location name
- `SEARCH(object_name: STRING): LOCATION` Search for an object
- `GRAB(where: LOCATION)` Grab an element at some coordinates
The first task is:
Bring me back one of the apple from the kitchen<|im_end|>
<|im_start|>assistant
$initial_loc = GET_CURRENT_LOCATION()
$kitchen_location = GET_LOCATION(location_name:"kitchen")
GO(to:$kitchen_location)
$apple_location = SEARCH(object_name:"apple")
GRAB($apple_location)
GO(to:$initial_loc)<|im_end|>
<|im_start|>user
Bring me back one of the apple from the kitchen<|im_end|>
<|im_start|>assistant\n
</pre>
```
