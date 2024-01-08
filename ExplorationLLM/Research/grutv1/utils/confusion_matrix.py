

class ConfusionMatrix:
    def __init__(self) -> None:
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0

    def get_accuracy(self) -> float:
        return (self.tp + self.tn) / (self.tp + self.fp + self.tn + self.fn) if self.tp != 0 and self.tn != 0 else 0
    def get_precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp != 0 else 0
    def get_recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp != 0 else 0
    def get_f1(self) -> float:
        return (2 * self.get_precision() * self.get_recall()) / (self.get_precision() + self.get_recall()) if self.get_precision() != 0 and self.get_recall() != 0 else 0

    
    def print_confusion_matrix(self) -> None:
        print("TP\t", self.tp, "\nFP\t", self.fp, "\nFN\t", self.fn, "\nTN\t", self.tn)
        print("ACCURACY:\t", self.get_accuracy())
        print("PRECISION:\t", self.get_precision())
        print("RECALL:\t\t", self.get_recall())
        print("F-MEASURE:\t", self.get_f1())
    
    def save_to_file(self, file):
        file = open(file, "w") 
        lines = [
            "TP: " + str(self.tp), 
            "FP: " + str(self.fp), 
            "FN: " + str(self.fn), 
            "TN: " + str(self.tn),
            "ACCURACY: " + str(self.get_accuracy()),
            "PRECISION: " + str(self.get_precision()),
            "RECALL: " + str(self.get_recall()),
            "F-MEASURE: " + str(self.get_f1())
        ]   
        file.writelines('\n'.join(lines))
        file.close()
