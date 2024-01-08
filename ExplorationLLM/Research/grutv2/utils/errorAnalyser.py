import pandas as pd
from utils.parsing_utils import from_srl_string_to_obj

class ErrorAnalyzer:
    def __init__(self, input_path = "./", input_filename = "results_unified.xlsx", output_path = None, output_filename = "error_analysis.txt", top_len:int = 5):
        if(not input_path.endswith("/")):
            input_path += "/"
        self.input_path = input_path
        self.input_filename = input_filename
        if(output_path == None):
            self.output_path = input_path
        else:
            self.output_path = output_path
        self.output_filename = output_filename
        self.top_len = top_len
        self.EXAMPLES = 0
        self.TOT_EXAMPLES = 0
        self.EXAMPLES_P = 0
        self.NOT_WELL_FORMATTED_C = 0
        self.NOT_WELL_FORMATTED_IDS = []
        self.FRAME_C = 0
        self.TOT_FRAME = 0
        self.FRAME_P = 0
        self.EXAMPLES_WITH_FRAME_ERRORS = 0
        self.EXAMPLES_WITH_FRAME_ERRORS_P = 0
        self.FRAME_ELEMENT_C = 0
        self.TOT_FRAME_ELEMENT = 0
        self.FRAME_ELEMENT_P = 0
        self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS = 0
        self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS_P = 0
        self.ARGUMENT_C = 0
        self.TOT_ARGUMENT = 0
        self.ARGUMENT_P = 0
        self.EXAMPLES_WITH_ARGUMENT_ERRORS = 0
        self.EXAMPLES_WITH_ARGUMENT_ERRORS_P = 0
        self.ENTITY_C = 0
        self.TOT_ENTITY = 0
        self.ENTITY_P = 0
        self.EXAMPLES_WITH_ENTITY_ERRORS = 0
        self.EXAMPLES_WITH_ENTITY_ERRORS_P = 0
        self.FRAME_MISSING = {}
        self.FRAME_ADDED = {}
        self.FRAME_ELEMENT_MISSING = {}
        self.FRAME_ELEMENT_ADDED = {}
    
    
    def analyze(self):
        path = self.input_path + self.input_filename
        print(f"Started analyzing '{path}'")
        #errors types: NOT_WELL_FORMATTED - FRAME - FRAME_ELEMENT - ARGUMENT - ENTITY
        errors, self.TOT_EXAMPLES = self.read_xlsx_file()
        
        for index, row in errors.iterrows():
            id = row['id']
            input_text = row['input_text']
            truth = row['truth']
            prediction = row['prediction']
            truth_obj = from_srl_string_to_obj(truth)
            try:
                prediction_obj = from_srl_string_to_obj(prediction)
            except:
                self.NOT_WELL_FORMATTED_C += 1
                self.NOT_WELL_FORMATTED_IDS.append(id)
                prediction_obj = []
                
            self.EXAMPLES += 1
            self.TOT_FRAME += len(truth_obj)
            frame_error = False
            frame_element_error = False
            argument_text_error = False
            argument_entity_error = False
            
            if(len(truth_obj) >= len(prediction_obj)):
                for frame_t in truth_obj:
                    frames_found = [frame_p for frame_p in prediction_obj if frame_p['name'].upper() == frame_t['name'].upper()]
                    if len(frames_found) == 0:
                        if frame_t['name'].upper() not in self.FRAME_MISSING:
                            self.FRAME_MISSING[frame_t['name'].upper()] = 0
                        self.FRAME_MISSING[frame_t['name'].upper()] += 1
                        self.FRAME_C += 1
                        frame_error = True
                        
            else: 
                for frame_p in prediction_obj:
                    frames_found = [frame_t for frame_t in truth_obj if frame_t['name'].upper() == frame_p['name'].upper()]
                    if len(frames_found) == 0:
                        if frame_p['name'].upper() not in self.FRAME_ADDED:
                            self.FRAME_ADDED[frame_p['name'].upper()] = 0
                        self.FRAME_ADDED[frame_p['name'].upper()] += 1
                        self.FRAME_C += 1
                        frame_error = True
            
            if(frame_error):
                self.EXAMPLES_WITH_FRAME_ERRORS += 1
                frame_error = False            
            
            for frame_t in truth_obj:
                frame_elements_t = frame_t['frameElements']
                self.TOT_FRAME_ELEMENT += len(frame_elements_t)

                for frame_p in prediction_obj:
                    frame_elements_p = frame_p['frameElements']
                    
                    if(len(frame_elements_t) >= len(frame_elements_p)):
                        for frame_element_t in frame_elements_t:
                            frame_elements_found = [frame_element_p for frame_element_p in frame_elements_p if frame_element_p['name'].upper() == frame_element_t['name'].upper()]
                            
                            if len(frame_elements_found) == 0:
                                if frame_element_t['name'].upper() not in self.FRAME_ELEMENT_MISSING:
                                    self.FRAME_ELEMENT_MISSING[frame_element_t['name'].upper()] = 0
                                self.FRAME_ELEMENT_MISSING[frame_element_t['name'].upper()] += 1
                                self.FRAME_ELEMENT_C += 1
                                frame_element_error = True
                                
                            elif len(frame_elements_found) == 1:
                                for frame_element_p in frame_elements_p:
                                    if(frame_element_p['name'].upper() == frame_element_t['name'].upper()):
                                        error = self.check_errors_argument(frame_element_t, frame_element_p)
                                        if( error == "TEXT" ):
                                            argument_text_error = True
                                        elif( error == "ENTITY" ):
                                            argument_entity_error = True
                    
                    else:
                        for frame_element_p in frame_elements_p:
                            frame_elements_found = [frame_element_t for frame_element_t in frame_elements_t if frame_element_t['name'].upper() == frame_element_p['name'].upper()]
                            
                            if len(frame_elements_found) == 0:
                                if frame_element_p['name'].upper() not in self.FRAME_ELEMENT_ADDED:
                                    self.FRAME_ELEMENT_ADDED[frame_element_p['name'].upper()] = 0
                                self.FRAME_ELEMENT_ADDED[frame_element_p['name'].upper()] += 1
                                self.FRAME_ELEMENT_C += 1
                                frame_element_error = True
                                
                            elif len(frame_elements_found) == 1:
                                for frame_element_t in frame_elements_t:
                                    if(frame_element_p['name'].upper() == frame_element_t['name'].upper()):
                                        error = self.check_errors_argument(frame_element_t, frame_element_p)
                                        if( error == "TEXT" ):
                                            argument_text_error = True
                                        elif( error == "ENTITY" ):
                                            argument_entity_error = True
                                        
            if(frame_element_error):
                self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS += 1
                frame_element_error = False 
            
            if(argument_text_error):
                self.EXAMPLES_WITH_ARGUMENT_ERRORS += 1
                argument_text_error = False 
                
            if(argument_entity_error):
                self.EXAMPLES_WITH_ENTITY_ERRORS += 1
                argument_entity_error = False 
                        
        
        self.FRAME_MISSING = dict(sorted(self.FRAME_MISSING.items(), key=lambda item: item[1], reverse=True))
        self.FRAME_ADDED = dict(sorted(self.FRAME_ADDED.items(), key=lambda item: item[1], reverse=True))
        self.FRAME_ELEMENT_MISSING = dict(sorted(self.FRAME_ELEMENT_MISSING.items(), key=lambda item: item[1], reverse=True))
        self.FRAME_ELEMENT_ADDED = dict(sorted(self.FRAME_ELEMENT_ADDED.items(), key=lambda item: item[1], reverse=True))
        
        self.EXAMPLES_P = round(100 * float(self.EXAMPLES)/float(self.TOT_EXAMPLES), 2)
        
        self.FRAME_P = round(100 * float(self.FRAME_C)/float(self.TOT_FRAME), 2) if self.TOT_FRAME != 0 else 0
        self.FRAME_ELEMENT_P = round(100 * float(self.FRAME_ELEMENT_C)/float(self.TOT_FRAME_ELEMENT), 2) if self.TOT_FRAME_ELEMENT != 0 else 0
        self.ARGUMENT_P = round(100 * float(self.ARGUMENT_C)/float(self.TOT_ARGUMENT), 2) if self.TOT_ARGUMENT != 0 else 0
        self.ENTITY_P = round(100 * float(self.ENTITY_C)/float(self.TOT_ENTITY), 2) if self.TOT_ENTITY != 0 else 0
        
        self.EXAMPLES_WITH_FRAME_ERRORS_P = round(100 * float(self.EXAMPLES_WITH_FRAME_ERRORS)/float(self.EXAMPLES), 2) if self.EXAMPLES != 0 else 0
        self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS_P = round(100 * float(self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS)/float(self.EXAMPLES), 2) if self.EXAMPLES != 0 else 0
        self.EXAMPLES_WITH_ARGUMENT_ERRORS_P = round(100 * float(self.EXAMPLES_WITH_ARGUMENT_ERRORS)/float(self.EXAMPLES), 2) if self.EXAMPLES != 0 else 0
        self.EXAMPLES_WITH_ENTITY_ERRORS_P = round(100 * float(self.EXAMPLES_WITH_ENTITY_ERRORS)/float(self.EXAMPLES), 2) if self.EXAMPLES != 0 else 0
        
        self.exportErrorAnalysis()
                 
    '''                    
        print("FRAME_C: " + str(self.FRAME_C))
        print("FRAME_MISSING: " + str(self.FRAME_MISSING))
        print("FRAME_ADDED: " + str(self.FRAME_ADDED))
        print("FRAME_ELEMENT_C: " + str(self.FRAME_ELEMENT_C))
        print("FRAME_ELEMENT_MISSING: " + str(self.FRAME_ELEMENT_MISSING))
        print("FRAME_ELEMENT_ADDED: " + str(self.FRAME_ELEMENT_ADDED))
        print("ARGUMENT_C: " + str(self.ARGUMENT_C))
        print("ENTITY_C: " + str(self.ENTITY_C))
    ''' 
        
            
    
    def check_errors_argument(self, frame_element_t, frame_element_p):
        
        argument_error = False
        
        if(frame_element_t['in_text']):
            self.TOT_ARGUMENT += 1
            if(frame_element_t['argument'][0].upper() != frame_element_p['argument'][0].upper()):
                self.ARGUMENT_C += 1
                argument_error = "TEXT"
        elif(not frame_element_t['in_text']):
            self.TOT_ENTITY += 1

            for argument_t, argument_p in zip(frame_element_t['argument'], frame_element_p['argument']):
                if argument_t not in frame_element_p['argument'] or argument_p not in frame_element_t['argument']:
                    self.ENTITY_C += 1
                    argument_error = "ENTITY"
        
        return argument_error
        
            
    def read_xlsx_file(self):
        excel_data = pd.read_excel(self.input_path + self.input_filename)
        data = pd.DataFrame(excel_data, columns=['id', 'input_text', 'truth', 'prediction', 'all frames correct', 'frames_list'])
        errors=data.query("not `all frames correct`")
        # errors=data[data['all frames correct'].str == False]
        return errors, len(data)
    
    
    def exportErrorAnalysis(self, output_path = None, output_filename = None):
        if(output_path == None):
            output_path = self.output_path
        if(output_filename == None):
            output_filename = self.output_filename
        
        
        
        f = open(output_path + output_filename, "w")
        f.write("ERROR ANALYSIS FOR FILE: " + self.input_filename)
        f.write("\n\n")
        f.write("EXAMPLES WITH ERRORS: " + str(self.EXAMPLES) + " PERCENTAGE: " + str(self.EXAMPLES_P) + "%" + " TOT: " + str(self.TOT_EXAMPLES))
        f.write("\n\n")
        f.write("NUMBER OF ERRORS ON FRAMES: " + str(self.FRAME_C) + " PERCENTAGE: " + str(self.FRAME_P) + "%")
        f.write("\n")
        f.write("EXAMPLES WITH FRAME ERRORS: " + str(self.EXAMPLES_WITH_FRAME_ERRORS) + " PERCENTAGE: " + str(self.EXAMPLES_WITH_FRAME_ERRORS_P) + "%")
        f.write("\n\n")
        f.write("NUMBER OF ERRORS ON FRAME ELEMENTS: " + str(self.FRAME_ELEMENT_C) + " PERCENTAGE: " + str(self.FRAME_ELEMENT_P) + "%")
        f.write("\n")
        f.write("EXAMPLES WITH FRAME ELEMENT ERRORS: " + str(self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS) + " PERCENTAGE: " + str(self.EXAMPLES_WITH_FRAME_ELEMENT_ERRORS_P) + "%")
        f.write("\n\n")
        f.write("NUMBER OF ERRORS ON ARGUMENTS: " + str(self.ARGUMENT_C) + " PERCENTAGE: " + str(self.ARGUMENT_P) + "%")
        f.write("\n")
        f.write("EXAMPLES WITH ARGUMENTS ERRORS: " + str(self.EXAMPLES_WITH_ARGUMENT_ERRORS) + " PERCENTAGE: " + str(self.EXAMPLES_WITH_ARGUMENT_ERRORS_P) + "%")
        f.write("\n\n")
        f.write("NUMBER OF ERRORS ON ENTITIES: " + str(self.ENTITY_C) + " PERCENTAGE: " + str(self.ENTITY_P) + "%")
        f.write("\n")
        f.write("EXAMPLES WITH ENTITY ERRORS: " + str(self.EXAMPLES_WITH_ENTITY_ERRORS) + " PERCENTAGE: " + str(self.EXAMPLES_WITH_ENTITY_ERRORS_P) + "%")
        f.write("\n\n")
        f.write("NUMBER OF ERRORS ON NOT WELL FORMATTED: " + str(self.NOT_WELL_FORMATTED_C))
        f.write("\n")
        f.write("IDS OF NOT WELL FORMATTED ENTRIES: " + str(self.NOT_WELL_FORMATTED_IDS))
        f.write("\n\n")
        f.write("TOP "+str(self.top_len)+" OF MOST FREQUENT ERRORS ON MISSING FRAMES:\n")
        for index, key in enumerate(self.FRAME_MISSING):
            if(index == self.top_len):
                break
            f.write(key + ": " + str(self.FRAME_MISSING[key]))
            f.write("\n")
        
        f.write("\n")
        f.write("TOP "+str(self.top_len)+" OF MOST FREQUENT ERRORS ON ADDED FRAMES:\n")
        for index, key in enumerate(self.FRAME_ADDED):
            if(index == 5):
                break
            f.write(key + ": " + str(self.FRAME_ADDED[key]))
            f.write("\n")
    
        f.write("\n")
        f.write("TOP "+str(self.top_len)+" OF MOST FREQUENT ERRORS ON MISSING FRAME ELEMENTS:\n")
        for index, key in enumerate(self.FRAME_ELEMENT_MISSING):
            if(index == 5):
                break
            f.write(key + ": " + str(self.FRAME_ELEMENT_MISSING[key]))
            f.write("\n")
        
        f.write("\n")   
        f.write("TOP "+str(self.top_len)+" OF MOST FREQUENT ERRORS ON ADDED FRAME ELEMENTS:\n")
        for index, key in enumerate(self.FRAME_ELEMENT_ADDED):
            if(index == 5):
                break
            f.write(key + ": " + str(self.FRAME_ELEMENT_ADDED[key]))
            f.write("\n")
        
        f.close()

        path = output_path + output_filename
        print(f"Saved file '{path}'")

            
        