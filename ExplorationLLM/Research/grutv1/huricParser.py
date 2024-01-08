
from xml.dom import minidom
import random
import csv
import numpy as np
import spacy

from utils.enums import Language, SRL_Input, SRL_Output
from utils.files_utils import getAllFiles
from utils.parsing_utils import computeLUDescriptionsIfDontExist, entity_in_sentence

chars = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']

class HuricParser:

    def __init__(self, lan: Language) -> None:
        self.entitiesName = []
        self.entitiesIndex = 0
        self.lan = lan

        # initialize spacy here
        model = 'en_core_web_sm' if (self.lan.value == 'en' or self.lan.value == 'english') else 'it_core_news_sm'
        self.nlp = spacy.load(model)

        # compute entities name here
        # just precompute 3000 random entity names
        for _ in range(3000):
            self.entitiesName.append(chars[int(random.randrange(0, len(chars)-1))] + numbers[int(random.randrange(0, len(numbers)-1))])

    def getNextEntityName(self):
        nextEntityName = self.entitiesName[self.entitiesIndex % len(self.entitiesName)]
        self.entitiesIndex += 1
        # nextEntityName = chars[int(random.randrange(0, len(chars)-1))]
        # return "entity:" + nextEntityName
        return nextEntityName

    # TODO in future: if sentence not in file, compute ludescription and add it to file
    def getLUDescriptions(self, id, sentence: str):
        # first check if sentence has already been pre computed
        computeLUDescriptionsIfDontExist('./data/sentences_lus_descriptions', self.lan)
        file = open('./data/sentences_lus_descriptions', 'r')
        array = file.readlines()
        for el in array:
            splitted = el.split("\t")
            if id == splitted[0]:
                # if found, return description as array splitting the string by comma
                return splitted[1].replace("\n", "").split(",") if splitted[1] != "\n" else []

        # else compute it on the fly
        doc = self.nlp(sentence)

        file = open('./data/lu_dict', 'r')
        lines = file.readlines()
        
        lus = {}
        for line in lines:
            line_splitted = line.split("\t")
            lus[line_splitted[0]] = line_splitted[1].replace("\n", "").upper().split(',')

        # if you find these special cases, add indexes to "consumed_indexes"
        sentence_lus = []
        consumed_indexes = []
        sentence_splitted = sentence.split(" ")
        if "go along" in sentence:
            sentence_lus.append("go along can evoke COTHEME")
            consumed_indexes.append(sentence_splitted.index("go"))
            consumed_indexes.append(sentence_splitted.index("along"))
        if "let go" in sentence:
            sentence_lus.append("let go can evoke RELEASING")
            consumed_indexes.append(sentence_splitted.index("go"))
            consumed_indexes.append(sentence_splitted.index("let"))
        if "pick up" in sentence:
            sentence_lus.append("pick up can evoke TAKING")
            consumed_indexes.append(sentence_splitted.index("pick"))
            consumed_indexes.append(sentence_splitted.index("up"))

        for sent in doc.sents:
            for i, word in enumerate(sent):
                lemma = word.lemma_
                if lemma in lus and i not in consumed_indexes:
                    if self.lan.value == "en":
                        sentence_lus.append(lemma + " can evoke " + " or ".join(lus[lemma]))
                    elif self.lan.value == "it":
                        sentence_lus.append(lemma + " può evocare " + " oppure ".join(lus[lemma]))

        # print(f"Sentence {sentence} \t lus {sentence_lus}")
        return sentence_lus

    def parseHuricFile(self, huricFile, task, type: str, addMap: bool, noMap: bool, map_type: str, addLUType: bool, grounding: str):
        # parse an xml file by name
        file = minidom.parse(huricFile)

        # use getElementsByTagName() to get tag
        # sentences = file.getElementsByTagName('sentence')

        id = file.getElementsByTagName("huricExample")[0].attributes['id'].value

        sentence = file.getElementsByTagName('sentence')[0].firstChild.data

        tokens = file.getElementsByTagName('tokens')[0].getElementsByTagName('token')

        semantics = file.getElementsByTagName('semantics')[0]

        frame_list = semantics.getElementsByTagName('frames')[0].getElementsByTagName('frame')

        
        entities = file.getElementsByTagName("semanticMap")[0].getElementsByTagName('entities')[0].getElementsByTagName('entity')
        # lexicalGroundings = file.getElementsByTagName("lexicalGroundings")[0].getElementsByTagName('lexicalGrounding')

        # if lexicalGroundings:
        #     sentence_map, atoms = self.parseMap(entities, lexicalGroundings, lexicalizedMap)
        # else:
        #     sentence_map, atoms = self.computeLexicalGroundingsANDparseMap(entities, sentence, lexicalizedMap)
        sentence_map, atoms = self.computeLexicalGroundingsANDparseMap(entities, sentence, map_type)
        
        output = ""
        output_obj = {}
        
        if task == "FP":
            if type == "frame":
                output = self.fromHuricFramesToFrames(frame_list)
            elif type == "frame+pos":
                output = self.fromHuricFramesToFramesPos(frame_list)
            elif type == "frame+token":
                output = self.fromHuricFramesToFramesToken(frame_list, tokens)
            elif type == "frame+sentence":
                output = self.fromHuricFramestoFramesSentence(frame_list, sentence)
        
        elif task == "BD":
            # aggiungere boundary detection
            return None
        elif task == "AC":
            # aggiungere argument classification
            return None
        elif task == "SRL":
            if noMap:
                id = "999" + id
            output_obj[id] = {}
            output, output_obj[id] = self.fromHuricToSRL(sentence, atoms, frame_list, addMap, noMap, grounding, map_type)
            output_obj[id]["sentence"] = sentence

        if addLUType:
            luDescriptions = self.getLUDescriptions(id, sentence)
            if luDescriptions:
                separator = " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " "
                sentence += " " + SRL_Input.FEATURE_SEPARATOR.value + " " + separator.join(luDescriptions)

        if addMap and grounding != "no":
            sentence += " " + SRL_Input.FEATURE_SEPARATOR.value + " " + sentence_map
            # sentence += " " + SRL_Input.FEATURE_SEPARATOR.value + " " + sentence_map if sentence_map != "" else " " + SRL_Input.FEATURE_SEPARATOR.value + " NOMAP"
        # elif not addMap:
        #     pass
        # elif noMap or grounding == "no":
        #     sentence += " " + SRL_Input.FEATURE_SEPARATOR.value + " NOMAP"

        return [id, sentence, output], output_obj

    def fromHuricFramesToFrames(self, frame_list):
        frames_output = ""

        for frame in frame_list:
            name = frame.attributes['name'].value.upper()

            if frames_output != "":
                frames_output = frames_output + " " + SRL_Output.FRAME_SEPARATOR.value + " " + name
            else:
                frames_output = name
        
        return frames_output

    def fromHuricFramesToFramesPos(self, frame_list):
        frames_output = ""

        for frame in frame_list:
            name = frame.attributes['name'].value
            pos = frame.getElementsByTagName('lexicalUnit')[0].getElementsByTagName('token')[0].attributes['id'].value

            if frames_output != "":
                frames_output = frames_output + " " + SRL_Output.FRAME_SEPARATOR.value + " " + name + ' ' + pos + ' ' + pos
            else:
                frames_output = name + ' ' + pos + ' ' + pos
        
        return frames_output
    
    def fromHuricFramesToFramesToken(self, frame_list, tokens):
        frames_output = ""

        for frame in frame_list:
            name = frame.attributes['name'].value.upper()
            pos = frame.getElementsByTagName('lexicalUnit')[0].getElementsByTagName('token')[0].attributes['id'].value
            token = tokens[int(pos) - 1].attributes['surface'].value

            if frames_output != "":
                frames_output = frames_output + " " + SRL_Output.FRAME_SEPARATOR.value + " " + name + ' ' + token
            else:
                frames_output = name + ' ' + token
        
        return frames_output

    def fromHuricFramestoFramesSentence(self, frame_list, sentence):
        sentence_list = sentence.split(" ")

        for frame in frame_list:
            name = frame.attributes['name'].value.upper()
            pos = frame.getElementsByTagName('lexicalUnit')[0].getElementsByTagName('token')[0].attributes['id'].value
            sentence_list[int(pos)-1] = name
        
        frames_output = ' '.join([str(elem) for elem in sentence_list])
        return frames_output

    def parseMap(self, entities, lexicalGroundings, lexicalizedMap: bool):
        
        atoms = {}

        for lexicalGrounding in lexicalGroundings:
            atom = lexicalGrounding.attributes['atom'].value
            tokenId = lexicalGrounding.attributes['tokenId'].value
            if atom in atoms.keys():
                atoms[atom]["tokenId"].append(tokenId)
            else:
                atoms[atom] = {"tokenId": [tokenId], "type": "", "name": [], "contain_ability": False, "x": 0, "y": 0, "z": 0}
        
        entities_list = []

        for entity in entities:
            atom = entity.attributes['atom'].value
            entities_list.append(atom)
            x = entity.getElementsByTagName('coordinate')[0].attributes['x'].value
            y = entity.getElementsByTagName('coordinate')[0].attributes['y'].value
            z = entity.getElementsByTagName('coordinate')[0].attributes['z'].value
            attributes = entity.getElementsByTagName('attributes')[0].getElementsByTagName('attribute')

            lexical_refs_found= False
            contain_ability_found= False
            for attribute in attributes:
                if attribute.attributes['name'].value == "lexical_references" and atom in atoms.keys():
                    atoms[atom]["type"] = entity.attributes['type'].value.upper()
                    for index, lexicalRef in enumerate(attribute.getElementsByTagName('value')):
                        if index <= 1:
                            atoms[atom]["name"].append(lexicalRef.firstChild.data.replace("_", " "))
                    atoms[atom]['x'] = x
                    atoms[atom]['y'] = y
                    atoms[atom]['z'] = z
                    
                    lexical_refs_found = True
                elif attribute.attributes['name'].value == "contain_ability" and atom in atoms.keys():
                    if attribute.getElementsByTagName('value')[0].firstChild.data == "true":
                        atoms[atom]["contain_ability"] = True
                    contain_ability_found = True

                if lexical_refs_found and contain_ability_found:
                    break
        
        # remove atom without corresponding entity
        atoms_list = list(atoms.keys())
        for atom in atoms_list:
            if atom not in entities_list:
                atoms.pop(atom)

        map = ""
        entities_name_list = []
        for _, value in atoms.items():
            
            # generate candidate name until it's unique for this sentence
            candidate_name = self.getNextEntityName()
            while candidate_name in entities_name_list:
                candidate_name = self.getNextEntityName()

            value['objectName'] = candidate_name
            entities_name_list.append(candidate_name)
            
            if value['name'] != "" and value['type'] != "" and value['objectName'] != "":
                if lexicalizedMap:
                    if self.lan.value == "en":
                        description = " also known as " + " or ".join(value['name']) + " is an instance of class "
                    elif self.lan.value == "it":
                        description = " conosciuto anche come " + " oppure ".join(value['name']) + " è un'istanza della classe "

                    v = value['objectName'] + description + value['type']
                else:
                    v = value['name'][0] + SRL_Input.TYPE_SEPARATOR.value + value['type'] + SRL_Input.CLASS_SEPARATOR.value + value['objectName']
                map = map + " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " " + v if map != "" else v

        distancesStringForMap = self.getDistancesStringForMap(atoms, lexicalizedMap)
        if distancesStringForMap != "":
            map = map + " " + SRL_Input.FEATURE_SEPARATOR.value + " " + distancesStringForMap

        containAbilityStringForMap = self.getContainAbilityStringForMap(atoms, lexicalizedMap)
        if containAbilityStringForMap != "":
            map = map + " " + SRL_Input.FEATURE_SEPARATOR.value + " " + containAbilityStringForMap

        # feature (more relations) to add in the future
        # onTopStringForMap = self.getOnTopStringForMap(atoms, lexicalizedMap)
        # if onTopStringForMap != "":
        #     map = map + " " + SRL_Input.FEATURE_SEPARATOR.value + " " + onTopStringForMap

        return map, atoms


    def computeLexicalGroundingsANDparseMap(self, entities, sentence, map_type):

        entities_list = []
        atoms = {}

        for entity in entities:
            # get info about entity
            attributes = entity.getElementsByTagName('attributes')[0].getElementsByTagName('attribute')
            atom = entity.attributes['atom'].value
            entities_list.append(atom)
            x = entity.getElementsByTagName('coordinate')[0].attributes['x'].value
            y = entity.getElementsByTagName('coordinate')[0].attributes['y'].value
            z = entity.getElementsByTagName('coordinate')[0].attributes['z'].value

            lexical_refs_found= False
            contain_ability_found= False

            # take its lexical_references and contain_ability
            lexical_references = []
            contain_ability = False
            for attribute in attributes:
                if attribute.attributes['name'].value == "lexical_references":
                    for lexicalRef in attribute.getElementsByTagName('value'):
                        if lexicalRef.firstChild:
                            lexical_references.append(lexicalRef.firstChild.data.replace("_", " "))
                        else:
                            print("********************WARNING********************")
                            print(f"'{atom}' in '{sentence}' has no lexical_ref")

                    lexical_refs_found = True
                elif attribute.attributes['name'].value == "contain_ability":
                    if attribute.getElementsByTagName('value')[0].firstChild.data == "true":
                        contain_ability = True
                    contain_ability_found = True

                if lexical_refs_found and contain_ability_found:
                    break

            # loop through lexical_references and find match in text
            token_ids = []
            for lex_ref in lexical_references:
                entity_in_sentence_tokens = entity_in_sentence(lex_ref, sentence)
                if entity_in_sentence_tokens:
                    token_ids.extend(entity_in_sentence_tokens)
                # if token_ids is not []

            if token_ids:
                # create atom
                atoms[atom] = {
                    "tokenId": token_ids, 
                    "type": entity.attributes['type'].value.upper(), 
                    "name": lexical_references, 
                    "contain_ability": contain_ability,
                    "x": x, "y": y, "z": z
                    }
    
        # remove atom without corresponding entity
        atoms_list = list(atoms.keys())
        for atom in atoms_list:
            if atom not in entities_list:
                atoms.pop(atom)

        map = ""
        if map_type != "nomap":
            entities_name_list = []
            for _, value in atoms.items():
                
                # generate candidate name until it's unique for this sentence
                candidate_name = self.getNextEntityName()
                while candidate_name in entities_name_list:
                    candidate_name = self.getNextEntityName()

                value['objectName'] = candidate_name
                entities_name_list.append(candidate_name)
                
                if value['name'] != "" and value['type'] != "" and value['objectName'] != "":
                    v = ""
                    if map_type == "lmd":
                        if self.lan.value == "en":
                            description = " also known as " + " or ".join(value['name']) + " is an instance of class "
                        elif self.lan.value == "it":
                            description = " conosciuto anche come " + " oppure ".join(value['name']) + " è un'istanza della classe "

                        v = value['objectName'] + description + value['type']
                    elif map_type == "smd":
                        v = value['name'][0] + SRL_Input.TYPE_SEPARATOR.value + value['type'] + SRL_Input.CLASS_SEPARATOR.value + value['objectName']
                    elif map_type == "cmd":
                        if self.lan.value == "en":
                            v = "there is a " + value['type']
                        elif self.lan.value == "it":
                            v = "c'è un " + value['type']
                    else:
                        print(f"MAP TYPE '{map_type}' NOT SUPPORTED!")
                    map = map + " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " " + v if map != "" else v

            distancesStringForMap = self.getDistancesStringForMap(atoms, map_type)
            if distancesStringForMap != "":
                map = map + " " + SRL_Input.FEATURE_SEPARATOR.value + " " + distancesStringForMap

            containAbilityStringForMap = self.getContainAbilityStringForMap(atoms, map_type)
            if containAbilityStringForMap != "":
                map = map + " " + SRL_Input.FEATURE_SEPARATOR.value + " " + containAbilityStringForMap

            # feature (more relations) to add in the future
            # onTopStringForMap = self.getOnTopStringForMap(atoms, map_type)
            # if onTopStringForMap != "":
            #     map = map + " " + SRL_Input.FEATURE_SEPARATOR.value + " " + onTopStringForMap

        return map, atoms

    def fromHuricToSRL(self, sentence, atoms, frame_list, addMap: bool, noMap: bool, grounding: str, map_type: str):
        output = {}
        sentence_list = sentence.split(" ")

        #construct frames and frameElements dict
        i = 0
        for frame in frame_list:
            output[i] = {}
            output[i]["name"] = frame.attributes['name'].value.upper()

            frame_elements = frame.getElementsByTagName('frameElements')[0].getElementsByTagName('frameElement')

            output[i]["frame_elements"] = {}
            j = 0
            for frame_element in frame_elements:
                type = frame_element.attributes['type'].value
                output[i]["frame_elements"][j] = {}
                output[i]["frame_elements"][j]["name"] = type
                output[i]["frame_elements"][j]["tokens"] = []
                #lista dei valori del frame element
                output[i]["frame_elements"][j]["values"] = []

                tokens = frame_element.getElementsByTagName('token')
                for token in tokens:
                    output[i]["frame_elements"][j]["tokens"].append(token.attributes['id'].value)
                
                output[i]["frame_elements"][j]["found"] = False
                output[i]["frame_elements"][j]["in_text"] = False
                j += 1

            i += 1

        if addMap and (not noMap) and grounding == "full":
            #set objectName to ei for frame_element in map
            for _, atom in atoms.items():
                ids = atom["tokenId"]
                type = atom["type"]
                name = atom["name"][0]
                objectName = atom["objectName"]

                for i, frame in output.items():
                    for j, frame_element in frame["frame_elements"].items():
                        
                        # inters = len(set(ids).intersection(frame_element["tokens"]))
                        # print()
                        # print(f'intersection {inters} for {frame_element["tokens"]} for argument {frame_element["name"]} and {ids} for {name}')
                        # print()

                        if len(set(ids).intersection(frame_element["tokens"])) > 0:
                            frame_element["found"] = True
                            value = {}
                            value["objectName"] = objectName
                            value["token"] = name
                            value["type"] = type
                            value["tokens"] = ids
                            frame_element["values"].append(value)
        
        #set objectName to tokens in sentence for frame_element not in map
        for i, frame in output.items():
            for j, frame_element in frame["frame_elements"].items():
                if not frame_element["found"]:
                    start = int(frame_element["tokens"][0])
                    end = int(frame_element["tokens"][-1])
                    frame_element["objectName"] = ' '.join([str(elem) for elem in sentence_list[start-1:end]])
                    frame_element["token"] = frame_element["objectName"]
                    frame_element["found"] = True 
                    frame_element["in_text"] = True

        #construct output_string from frames and frameElements
        output_string = ""
        for i, frame in output.items():
            frame_string = frame["name"] + SRL_Output.FRAME_CONTAINER_START.value
            for j, frame_element in frame["frame_elements"].items():
                
                if len(frame_element["values"]) > 0:
                    # sort by tokens position
                    frame_element["values"].sort(key = lambda x: int(x['tokens'][0]))

                    object_name = ""
                    if map_type == "cmd":
                        object_name = frame_element["values"][0]["type"]
                    else:
                        object_name = frame_element["values"][0]["objectName"]

                    # take objectName of first entity
                    frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + object_name + SRL_Output.ARGUMENT_CONTAINER_END.value
                    
                elif frame_element["in_text"]:
                    frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + SRL_Output.ARGUMENT_IN_TEXT_START.value + frame_element["objectName"] + SRL_Output.ARGUMENT_IN_TEXT_END.value + SRL_Output.ARGUMENT_CONTAINER_END.value
                else:
                    # empty frame element
                    frame_element_string = frame_element["name"] + SRL_Output.ARGUMENT_CONTAINER_START.value + SRL_Output.ARGUMENT_CONTAINER_END.value
                    
                if j == 0:
                    # add first argument
                    frame_string += frame_element_string
                else:
                    # concatenate argument with separator
                    frame_string += SRL_Output.ARGUMENT_SEPARATOR.value + " " + frame_element_string
                
            frame_string += SRL_Output.FRAME_CONTAINER_END.value

            if output_string == "":
                # add first frame
                output_string = frame_string
            else:
                # concatenate frame with separator
                output_string += " " + SRL_Output.FRAME_SEPARATOR.value + " " + frame_string

        return output_string, output

    def getContainAbilityStringForMap(self, atoms, map_type):
        containAbilityStringForMap = ""

        for key, value in atoms.items():
            if value['contain_ability']:
                v = ""
                if map_type == "lmd":
                    if self.lan.value == "en":
                        contain_ability_relation = " can contain other objects"
                    elif self.lan.value == "it":
                        contain_ability_relation = " può contenere altri oggetti"
                    
                    v = atoms[key]["objectName"] + contain_ability_relation
                elif map_type == "smd":
                    if self.lan.value == "en":
                        contain_ability_relation = " CONTAIN ABILITY"
                    elif self.lan.value == "it":
                        contain_ability_relation = " ABILITà DI CONTENERE"

                    v = atoms[key]["objectName"] + contain_ability_relation
                elif map_type == "cmd":
                    if self.lan.value == "en":
                        contain_ability_relation = " can contain other objects"
                    elif self.lan.value == "it":
                        contain_ability_relation = " può contenere altri oggetti"
                    v = atoms[key]["type"] + contain_ability_relation

                containAbilityStringForMap = containAbilityStringForMap + " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " " + v if containAbilityStringForMap != "" else v
                    
        return containAbilityStringForMap
        
        
    def getDistancesStringForMap(self, atoms, map_type):
        distancesStringForMap = ""

        distances = self.computeDistance(atoms)

        checkedEntities = []
        for key, _ in atoms.items():

            for key2, distance in distances[key].items():

                if distance <= float(1.9) and key2 not in checkedEntities:
                    v = ""
                    if map_type == "lmd":
                        if self.lan.value == "en":
                            near_relation = " is near "
                        elif self.lan.value == "it":
                            near_relation = " è vicino "
                        
                        v = atoms[key]["objectName"] + near_relation + atoms[key2]["objectName"]
                    elif map_type == "smd":
                        if self.lan.value == "en":
                            near_relation = " NEAR "
                        elif self.lan.value == "it":
                            near_relation = " VICINO "

                        v = atoms[key]["objectName"] + near_relation + atoms[key2]["objectName"]
                    elif map_type == "cmd":
                        if self.lan.value == "en":
                            near_relation = " is near "
                        elif self.lan.value == "it":
                            near_relation = " è vicino "

                        v = atoms[key]["type"] + near_relation + atoms[key2]["type"]
                    
                    distancesStringForMap = distancesStringForMap + " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " " + v if distancesStringForMap != "" else v
                    
            # if I already checked an entity, no need to check it again and add duplicates
            # e.g. e2 NEAR e3 & e3 NEAR e2
            checkedEntities.append(key)

        return distancesStringForMap

    def computeDistance(self, atoms):
        dist = {}
        for key, value in atoms.items():
            p1 = np.array([[float(value['x'])], [float(value['y'])], [float(value['z'])]])
            dist[key] = {}

            for key2, value2 in atoms.items():
                if key != key2:
                    p2 = np.array([[float(value2['x'])], [float(value2['y'])], [float(value2['z'])]])

                    squared_dist = np.sum((p1-p2)**2, axis=0)
                    dist[key][key2] = float(np.sqrt(squared_dist))
        
        return dist


    def getOnTopStringForMap(self, atoms, lexicalizedMap):
        onTopStringForMap = ""

        onTopDict = self.computeOnTop(atoms)

        checkedEntities = []
        for key, _ in atoms.items():
            for key2, onTop in onTopDict[key].items():

                if onTop and key2 not in checkedEntities:
                    if lexicalizedMap:
                        if self.lan.value == "en":
                            ontop_relation = " is on top of "
                        elif self.lan.value == "it":
                            ontop_relation = " sta sopra "
                        
                        v = atoms[key]["objectName"] + ontop_relation + atoms[key2]["objectName"]
                        onTopStringForMap = onTopStringForMap + " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " " + v if onTopStringForMap != "" else v
                    else:
                        if self.lan.value == "en":
                            ontop_relation = " ON TOP "
                        elif self.lan.value == "it":
                            ontop_relation = " SOPRA "

                        v = atoms[key]["objectName"] + ontop_relation + atoms[key2]["objectName"]
                        onTopStringForMap = onTopStringForMap + " " + SRL_Input.FEATURE_ELEMENT_SEPARATOR.value + " " + v if onTopStringForMap != "" else v

            # if I already checked an entity, no need to check it again and add duplicates
            # e.g. e2 ON TOP e3 & e3 ON TOP e2
            checkedEntities.append(key)

        return onTopStringForMap

    def computeOnTop(self, atoms):
        dict = {}
        for key, value in atoms.items():
            x1, y1, z1 = float(value["x"]), float(value["y"]), float(value["z"])
            dict[key] = {}

            for key2, value2 in atoms.items():
                if key != key2:
                    x2, y2, z2 = float(value2["x"]), float(value2["y"]), float(value2["z"])

                    if x1 == x2 and y1 == y2 and z1 >= z2 :
                        dict[key][key2] = True
        
        return dict

    def parse(self, path, task, type: str, addMap: bool, map_type: str, noMapExamples: bool = False, addLUType: bool = False, grounding:str = "no"):

        files = getAllFiles(path + self.lan.value)

        files_parsed = []
        outputs_obj = {}

        for file in files:
            huric_file_parsed, output_obj = self.parseHuricFile(file, task, type, addMap, noMap=False, map_type=map_type, addLUType=addLUType, grounding=grounding)
            if output_obj:
                outputs_obj.update(output_obj)
            files_parsed.append(huric_file_parsed)

            if noMapExamples:
                # if sentence does not contain NOMAP, we can generate a NOMAP example to expand training set
                if (" # NOMAP" not in huric_file_parsed[1]) and addMap:
                    huric_file_parsed_nomap, output_obj_nomap = self.parseHuricFile(file, task, type, addMap=False, noMap=True, map_type="nomap", addLUType=False, grounding="no")
                    if output_obj:
                        outputs_obj.update(output_obj_nomap)
                    files_parsed.append(huric_file_parsed_nomap)

        # print(files_parsed[:100])
        
        return files_parsed, outputs_obj
    
    def parseAndWrite(self, path, task, toFile, type: str = "frame", addMap: bool = False, map_type: str = "nomap", addLUType: bool = False, grounding: str = "no"):
        
        header = ['id', 'input_text', 'target_text']

        files_parsed, outputs_obj = self.parse(path, task, type, addMap, map_type, addLUType=addLUType, grounding=grounding)

        print(f"Writing HURIC DATASET to {toFile}")
        with open(toFile, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            writer.writerow(header)

            writer.writerows(files_parsed)
        
        return outputs_obj


    def getIdAndSentence(self, file):
        fileParsed = minidom.parse(file)
        id = fileParsed.getElementsByTagName("huricExample")[0].attributes['id'].value
        sentence = fileParsed.getElementsByTagName('sentence')[0].firstChild.data
        return id, sentence


    def writeHuricSentences(self, datasetFilePath, sentencesFilePath):
        files = getAllFiles(datasetFilePath + self.lan.value)
        sentences = []
        header = ['id', 'sentence']

        for file in files:
            id, sentence = self.getIdAndSentence(file)
            sentences.append([id, sentence])

        print("Writing HURIC Sentences to file!")
        with open(sentencesFilePath, 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(sentences)

    
    


