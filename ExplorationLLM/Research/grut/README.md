# Introduction
This repository contains the code for two papers:
- **GrUT v1.0 (Grounded language Understanding via Transformers): Embedding Contextual Information in seq2seq models for Grounded Semantic Role Labeling** published in the **AIxIA 2022** conference by *Claudiu Daniel Hromei* (Tor Vergata, University of Rome; Università Campus Bio-Medico di Roma), *Lorenzo Cristofori* (Tor Vergata, University of Rome), *Danilo Croce* (Tor Vergata, University of Rome) and *Roberto Basili* (Tor Vergata, University of Rome). The paper can be found [here](https://link.springer.com/chapter/10.1007/978-3-031-27181-6_33).  
- **GrUT v2.0 (Grounded language Understanding via Transformers): Grounding end-to-end Architectures for Semantic Role Labeling in Human Robot Interaction** published in the **NL4AI** workshop at AIxIA 2022 conference by *Claudiu Daniel Hromei* (Tor Vergata, University of Rome; Università Campus Bio-Medico di Roma), *Danilo Croce* (Tor Vergata, University of Rome) and *Roberto Basili* (Tor Vergata, University of Rome). The paper can be found [here](https://ceur-ws.org/Vol-3287/paper5.pdf).  

GrUT is a neural approach for the interpretation of robotic spoken commands that is consistent with (i) the world (with all the entities therein), (ii) the robotic platform (with all its inner representations and capabilities), and (iii) the linguistic information derived from the user’s utterance. It is a sequence-to-sequence method that performs Grounded Semantic Role Labeling in an end-to-end manner, thus avoiding the traditional cascade of interpretation tasks to be solved and effectively linking arguments on the basis of the status and properties of the real-world.  

Given a command, "*take the book to the bedroom*", GrUT v1.0 will output a pure linguistic interpretation based on the [Frame Semantics](https://framenet.icsi.berkeley.edu/fndrupal/) theory, i.e.`BRINGING(Theme('the book'), Goal('to the bedroom'))`, which means to take *the book* wherever it is and *bring* it *to the bedroom*. Here *the book* and *the bedroom* are real existing entities in the robot environment, each of which described by an identifier (ID), its position (x,y,z), a list of lexical references (labels like *book*, *volume*, *bedroom*, etc.). The interpretation is consistent both with the command *and* the map of the surrounding environment.  

We released here GrUT v2.0, that is an extension of the original work where the model is expected to produce indexed interpretations in the robot Knowledge Base through the identifier of the real existing entities, rather than rewriting the span of text. Given the same command as before, "*take the book to the bedroom*", GrUT v2.0 will output a fully grounded interpretation, i.e. `Bringing(Theme(b1), Goal(b5))`, where *b1* is the identifier of the BOOK entity and *b5* is the identifier of the BEDROOM entity.

Moreover, in the 1.0 version, all the entities, whose name exactly match at least one word in the command, are retrieved and fed in the input, so that the model can use its attention mechanism to make reference to the entities. The Exact Match is not suitable to retrieve objects like *volume* or *sofa* if the command contains *book* or *couch*, respectively. In the extended work, we propose 2 additional *LexicalSimilarity* functions to retrieve entities and improve the retrieval step:
- *Levenshtein Similarity*, based on the Levenshtein Distance, as a "soft" string matching able to capture morphological reatedness between input word pairs.
- *Neural Semantic Similarity*, based on W2V embeddings, it corresponds to the cosine similarity between embeddings representing input word pairs. It is capable of semantic similarity as words with the same meaning are close to each other in the W2V space.

This code runs the GrUT experiment over a public dataset ([HuRIC 2.1](https://github.com/crux82/huric)) for the Semantic Role Labeling (SRL) task and compares its performances with a simple ready to use model, namely BART, finetuned on the same dataset.  

As a result, we show an error reduction of 26% for the Frame Prediction (FP) task and 23% for the Argument Identification and Classification (AIC) task. You can find more details about the tasks in the paper.


# Create Environment
Create a new environment:  

    conda create --name venv  

And activate it:  

    conda activate venv


# Install Required Lib
You can install them from `requirements.txt` file with:  

    pip install -r requirements.txt  

Then download spacy:  

    python -m spacy download en_core_web_sm  

**NOTE**: for torch, you need python version <= 3.9.x    
**NOTE**: you need specific version of torch based on cuda version (our current version is cuda11):    

    python -m pip install torch==1.9.0+cu111 torchvision==0.10.0+cu111 -f https://download.pytorch.org/whl/torch_stable.html


## Other requirements
- HuRIC 2.1 dataset. You can download it manually and put it in `data` folder or use:  

    `git clone https://github.com/crux82/huric.git data`  

- You should use `nohup` or `nodemon` to start your training, as you don't want to wait for it to finish :)  


# How to use GrUT
**You need to download the model first and put it in a subfolder**, in this example we put GrUT v1.0 in `model/grut_v1` and GrUT v2.0 in `model/grut_v2`. Depending on the model selected, you can use GrUT 1.0 or GrUT 2.0 and it will generate pure linguistic (1.0) or grounded (2.0) interpretations.  

Given a command like "*take the book to the bedroom*", with GrUT v1.0 you should use:

    python grut.py predict -i "take the book to the bedroom # b1 also known as book or textbook is an instance of class BOOK & b5 also known as bedroom or bed room is an instance of class BEDROOM" -m model/grut_v1  

and you will get in output: `BRINGING(Theme('the book'), Goal('to the bedroom'))`  

If you want a fully grounded logical form, you can use the GrUT v2.0 with the following command:

    python grut.py predict -i "take the book to the bedroom # b1 also known as book or textbook is an instance of class BOOK & b5 also known as bedroom or bed room is an instance of class BEDROOM" -m model/grut_v2

and you will get: `Bringing(Theme(b1), Goal(b5))`, where the names of the entities can change because they are generated dinamically. Anyhow, the system logs the map description, so you can check if they match.  

**Notice** that here the map is explictly concatenated to the input, but if you want the model to parse a file for you, just add the path with the `-hrc` option:  

    python grut.py predict -i "take the book to the bedroom" -hrc data/huric/en/S4R/2748.hrc -m model/grut_v1 

You should get the same output as before.


### Options
Here you can find a list of the options.

    -h   : help.
    -m   : define path to model. (default to "/model/")
    -t   : define the task. (default to "SRL")
    -i   : input to be predicted.
    -hrc : path to huric file to be used as map. (if no path is provided, it is assumed the map description is already appended to the input)

**Notice** that the input needs to be in the form described in the paper, i.e. with existential and spatial map description prepended to the input and divided by `#`.


# How to train GrUT
This repository provides the code to fine tune 2 models: **GrUT**, that takes a command and the environment description in natural language as input to provide the interpretation, and **BART**, that takes only the command as input to provide the interpretation.
In **bold** you will find the name of the model, as reported in the paper, a brief description and the code to execute the command in order to train it.  

- **BART_base**: BART base, as released by huggingface  

    `nohup python -u grut.py train -mn bart -mv base -t SRL -bs 32 -uc True -ep 50 -nf 10 -tt SRL > logs/testing_verbose_with_prints_bart_base.out &`  

- **GRUT**: BART with existential and spatial map description

    `nohup python -u grut.py train -mn bart -mv base -t SRL -bs 32 -uc True -ep 50 -nf 10 -tt SRL -gr half -map lmd > logs/testing_verbose_with_prints_grut.out &`  
    

### Options
Here you can find a list of the options used to train the models.

    -h : help.
    -am : define whether to add map description or not, default False.
    -bs : define batch size, 4 by default.
    -ep : define numbers of epochs for training, 1 by default.
    -es : define if using early stopping considering epoch during training or not, the default is True.
    -mn : define model name: bart (default), t5, mt5.
    -mv : define model size: small, base (default), large, ecc.
    -nf : define numbers of fold in kfold.
    -uc : define if use GPU True/False.
    -t  : define task type: FP(Frame Prediction), BD(Boundary Detection), AC(Argument Classification), SRL (default).
    -tt : define type of target manipulation: frame, frame+pos, frame+token, frame+sentence, SRL(default).


# Results
Results will be written inside `./model/<model_name>` folder.   
For example: if you want to train **GrUT**, <model_name> will be `bart_en_stm_lmd_halfgrounding_W2V_allLexicalReferences_<TIMESTAMP>` based on the options described here. There you will find, among others, 3 files:  
- `results_unified.xlsx` containing test set sentences, with predictions and gold standard (truth)  
- `frames_CM_unified.txt` containing confusion matrix for frames only (Frame Prediction task), merged for all X folds  
- `frame_elements_CM_unified.txt` containing confusion matrix for frame elements (arguments and types for AIC task), merged for all X folds  


# Citation
To cite the paper, please use the followings:  
```
@inproceedings{DBLP:conf/aiia/HromeiC022,
  author    = {Claudiu Daniel Hromei and
               Danilo Croce and
               Roberto Basili},
  title     = {Grounding end-to-end Architectures for Semantic Role Labeling in Human
               Robot Interaction},
  booktitle = {Proceedings of the Sixth Workshop on Natural Language for Artificial
               Intelligence {(NL4AI} 2022) co-located with 21th International Conference
               of the Italian Association for Artificial Intelligence (AI*IA 2022),
               Udine, November 30th, 2022},
  series    = {{CEUR} Workshop Proceedings},
  volume    = {3287},
  pages     = {24--38},
  publisher = {CEUR-WS.org},
  year      = {2022},
  url       = {http://ceur-ws.org/Vol-3287/paper5.pdf}
}
```
```
@inproceedings{DBLP:conf/aiia/HromeiCCB22,
  author       = {Claudiu Daniel Hromei and
                  Lorenzo Cristofori and
                  Danilo Croce and
                  Roberto Basili},
  title        = {Embedding Contextual Information in Seq2seq Models for Grounded Semantic
                  Role Labeling},
  booktitle    = {AIxIA 2022 - Advances in Artificial Intelligence - XXIst International
                  Conference of the Italian Association for Artificial Intelligence,
                  AIxIA 2022, Udine, Italy, November 28 - December 2, 2022, Proceedings},
  series       = {Lecture Notes in Computer Science},
  volume       = {13796},
  pages        = {472--485},
  publisher    = {Springer},
  year         = {2022},
  url          = {https://doi.org/10.1007/978-3-031-27181-6_33}
}
```
