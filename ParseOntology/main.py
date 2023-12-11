import tomllib
from typing import List, Optional

class ParseTOMLOntologyException(Exception):
    """
    Raised when something goes wrong while parsing an Ontology TOML file
    """
    pass

class Entity:
    def __init__(self, name: str, attributes: List[str]):
        self.name = name
        self.attributes = attributes

class Relation:
    def __init__(self, name: str, from_: Entity, to: Entity):
        self.name = name
        self.from_ = from_
        self.to = to

class Task:
    def __init__(self, name: str, steps: List[str]):
        self.name = name
        self.steps = steps


class Ontology:
    def __init__(self):
        self.name: str = 'default_name'
        self.entities: List[Entity] = []
        self.relations: List[Relation] = []
        self.tasks: List[Task] = []

    def find_entity(self, name: str) -> Optional[Entity]:
        """
        Find an entity inside the ontology

        :param name:
        :return:
        """
        for entity in self.entities:
            if entity.name == name:
                return entity

        return None

def parseOntologyConfig(file_name) -> Ontology:
    """
    Parse a TOML ontology file and returns a filled Ontology object

    :param file_name:
    :return:
    """
    print('Parsing Ontology...')

    file = open(file_name, "rb")
    data = tomllib.load(file)

    # Ontology

    ontology = Ontology()

    if 'ontology' not in data:
        raise ParseTOMLOntologyException('You must provide an "ontology" table')

    if 'name' not in data['ontology']:
        raise ParseTOMLOntologyException('The "ontology" table must have a "name" key/value')

    if not isinstance(data['ontology']['name'], str):
        raise ParseTOMLOntologyException('The "ontology" name must be a string')

    ontology.name = data['ontology']['name']

    # Entities

    if 'entities' not in data:
        raise ParseTOMLOntologyException('You must provide an "entities" table')

    if not isinstance(data['entities'], dict):
        raise ParseTOMLOntologyException('The "entities" must be a table')

    # > Attributes

    if 'attributes' not in data['entities']:
        raise ParseTOMLOntologyException('The "entities" table must have a "attributes" sub-table')

    if not isinstance(data['entities']['attributes'], dict):
        raise ParseTOMLOntologyException('The "entities" "attributes" must be a table')

    for key in data['entities']['attributes']:
        if not isinstance(data['entities']['attributes'][key], list):
            raise ParseTOMLOntologyException(f'The attributes of the entity "{key}" must be inside an array')

        attributes = data['entities']['attributes'][key]

        for attribute in attributes:
            if not isinstance(attribute, str):
                raise ParseTOMLOntologyException(f'The attribute "{attribute}" of the entity "{key}" must be a string')
    

        entity = Entity(key, attributes)
        ontology.entities.append(entity)

    # > Relations

    if 'relations' not in data['entities']:
        raise ParseTOMLOntologyException('The "entities" table must have a "relations" sub-table')

    if not isinstance(data['entities']['relations'], dict):
        raise ParseTOMLOntologyException('The "entities" "relations" must be a table')

    for key in data['entities']['relations']:
        if not isinstance(data['entities']['relations'][key], dict):
            raise ParseTOMLOntologyException('The entity relations must be inside of an inline table')

        relation = data['entities']['relations'][key]

        if not 'from' in relation:
            raise ParseTOMLOntologyException(f'The entity relation "{key}" must contain a "from" key/value')

        from_ = relation['from']

        if not isinstance(from_, str):
            raise ParseTOMLOntologyException(f'The entity relation "{key}" "from" value must be a string')

        relation_from = ontology.find_entity(from_)

        if relation_from is None:
            raise ParseTOMLOntologyException(f'The entity relation "{key}" "from" "{from_}" was not found in the list of entities')

        if not 'to' in relation:
            raise ParseTOMLOntologyException(f'The entity relation "{key}" must contain a "to" key/value')

        to_ = relation['to']

        if not isinstance(to_, str):
            raise ParseTOMLOntologyException(f'The entity relation "{key}" "to" value must be a string')

        relation_to = ontology.find_entity(to_)

        if relation_to is None:
            raise ParseTOMLOntologyException(f'The entity relation "{key}" "to" "{to_}" was not found in the list of entities')


        relation_ = Relation(key, relation_from, relation_to)
        ontology.relations.append(relation_)

    # Task

    if 'tasks' not in data:
        raise ParseTOMLOntologyException('You must provide an "tasks" table')

    if not isinstance(data['tasks'], dict):
        raise ParseTOMLOntologyException('The "tasks" must be a table')

    for key in data['tasks']:
        if not isinstance(data['tasks'][key], dict):
            raise ParseTOMLOntologyException(f'The task "{key}" must be a sub-table')

        task = data['tasks'][key]

        if not 'steps' in task:
            raise ParseTOMLOntologyException(f'The task "{key}" must have a "steps" key/value')

        if not isinstance(task['steps'], list):
            raise ParseTOMLOntologyException(f'The task "{key}" "steps" value must be an array')

        steps = task['steps']

        for step in task['steps']:
            if not isinstance(step, str):
                raise ParseTOMLOntologyException(f'The value "{step}" of the task "{key}" "steps" must be a string')
    
        task_ = Task(key, steps)
        ontology.tasks.append(task_)

    print('Parsing done!')
    print(f'Got ontology "{ontology.name}" with {len(ontology.entities)} entitie(s), {len(ontology.relations)} relation(s), and {len(ontology.tasks)} task(s)')

    return ontology

if __name__ == "__main__":
    ontology = parseOntologyConfig("ontology.toml")