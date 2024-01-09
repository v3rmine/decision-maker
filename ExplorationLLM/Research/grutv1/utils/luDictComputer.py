
import os
from xml.dom import minidom

from utils.enums import Language
from utils.files_utils import getAllFiles


class LUDictComputer:
    def __init__(self, lan: Language) -> None:
        self.lan = lan


    def parseHuricFile(self, huricFile):
        file = minidom.parse(huricFile)

        tokens = file.getElementsByTagName('tokens')[0].getElementsByTagName('token')
        semantics = file.getElementsByTagName('semantics')[0]
        frames_object_list = semantics.getElementsByTagName('frames')[0].getElementsByTagName('frame')

        frames_list = []
        for frame_object in frames_object_list:
            frame = {
                "name": frame_object.attributes['name'].value, 
                "lus": ""
                }

            # retrieve lus tokens
            lus_tokens_object_list = frame_object.getElementsByTagName('lexicalUnit')[0].getElementsByTagName('token')
            lus_tokens_list = []
            for token in lus_tokens_object_list:
                lus_tokens_list.append(token.attributes['id'].value)

            # retrieve lus lemmas from tokens
            for token in tokens:
                sentence_token = token.attributes['id'].value
                if sentence_token in lus_tokens_list:
                    if frame['lus'] == "":
                        frame['lus'] = token.attributes['lemma'].value
                    else:
                        frame['lus'] +=  " " + token.attributes['lemma'].value
                    
            frames_list.append(frame)
    
        return frames_list


    def precompute(self):
        if not os.path.exists("./data/lu_dict"):
            print("Computing LU DICT")
            files = getAllFiles("./data/huric/" + self.lan.value)
            lus_dict = {}

            for file in files:
                frames_list = self.parseHuricFile(file)

                for frame in frames_list:
                    lus = frame['lus']
                    if lus in lus_dict.keys():
                        if frame['name'].upper() not in lus_dict[lus]:
                            lus_dict[lus].append(frame['name'].upper())
                    else:
                        lus_dict[lus] = [frame['name'].upper()]
            
            lines = []
            for k,v in lus_dict.items():
                lines.append(k + "\t" + ",".join(v) + "\n")

            file = open("./data/lu_dict", 'w')
            file.writelines(lines)
            length = len(lus_dict.keys())
            print(f"DONE writing ./data/lu_dict with {length} keys")
        
        
        