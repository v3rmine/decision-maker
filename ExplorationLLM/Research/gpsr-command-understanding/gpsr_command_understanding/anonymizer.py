import re
from collections import defaultdict


class CaseInsensitiveDict(dict):
    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())


class Anonymizer(object):
    def __init__(self, objects, categories, names, locations, rooms, gestures, whattosay):
        """
        Give the entities that will be anonymized. Matching and replacement is
        case insensitive.
        
        :param objects: 
        :param categories: 
        :param names: 
        :param locations: 
        :param rooms: 
        :param gestures: 
        :param whattosay: 
        """
        self.names = names
        self.categories = categories
        self.locations = locations
        self.rooms = rooms
        self.objects = objects
        self.gestures = gestures
        self.whattosay = whattosay
        replacements = CaseInsensitiveDict()
        for name in self.names:
            replacements[name] = "name"

        for location in self.locations:
            replacements[location] = "location"

        for room in self.rooms:
            replacements[room] = "room"

        # Note they're we're explicitly clumping beacons and placements (which may overlap)
        # together to make anonymizing/parsing easier.
        """
        for beacon in self.beacons:
            replacements[beacon] = "location beacon"

        for placement in self.placements:
            replacements[placement] = "location placement"
        """
        for object in self.objects:
            replacements[object] = "object"

        for gesture in self.gestures:
            replacements[gesture] = "gesture"

        for category in self.categories:
            replacements[category] = "category"

        for whattosay in self.whattosay:
            replacements[whattosay] = "whattosay"

        replacements["objects"] = "category"

        self.replacements = replacements
        escaped = {re.escape(k): v for k, v in replacements.items()}
        self.pattern = re.compile("\\b(" + "|".join(escaped.keys()) + ")\\b", re.IGNORECASE)

    def __call__(self, utterance, return_replacements=False):
        """
        Replaces entity occurrences with their specified replacement string (usually a type token).
        "apple apple banana" -> "object object object"
        :param utterance: 
        :param return_replacements: 
        :return: 
        """
        anonymized = utterance
        replacements = defaultdict(lambda: set())
        for match in self.pattern.finditer(utterance):
            match_str = match.group()
            replacements[match_str].add(self.replacements[match_str])
            anonymized = anonymized.replace(match_str, self.replacements[match_str])
        if return_replacements:
            return anonymized, replacements
        else:
            return anonymized

    @staticmethod
    def from_knowledge_base(kb):
        # Room is a subtype of location, but we make an exception and anonymize it as "roomN"
        isroom = kb.attributes["location"]["isroom"]
        rooms = []
        for key, isroom in isroom.items():
            if isroom:
                rooms.append(key)
        return Anonymizer(kb.by_name["object"], kb.by_name["category"], kb.by_name["name"], kb.by_name["location"],
                          rooms, kb.by_name["gesture"], kb.by_name["whattosay"])


class NumberingAnonymizer(Anonymizer):
    @staticmethod
    def from_knowledge_base(kb):
        plain = Anonymizer.from_knowledge_base(kb)
        return NumberingAnonymizer(plain.objects, plain.categories, plain.names, plain.locations, plain.rooms,
                                   plain.gestures, plain.whattosay)

    def __call__(self, utterance, return_replacements=False):
        """
        Replaces entities with some other token (usually a type token) with a number appended.
        "apple apple" -> "object0 object1"
        "apple banana" -> "object0 object1"
        We expect objects to be referred to once in commands, thus the decision to allow even the same
        word to be mapped to multiple numbers. We assume that a repeated occurrence is actually a 
        separate entity with the same name. 
        :param utterance: 
        :param return_replacements: 
        :return: 
        """
        anonymized = utterance
        replacements = defaultdict(lambda: set())
        num_type_anon_so_far = defaultdict(lambda: 0)
        while True:
            match = self.pattern.search(anonymized)
            if not match:
                break
            string = match.group()
            replacement_type = self.replacements[string]

            current_num = num_type_anon_so_far[replacement_type]
            replacement_string = self.replacements[string] + str(current_num)
            num_type_anon_so_far[replacement_type] += 1
            replacements[string].add(replacement_string)
            anonymized = anonymized.replace(string, replacement_string, 1)
        if return_replacements:
            return anonymized, replacements
        else:
            return anonymized
