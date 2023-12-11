import tomllib
from models import Memory, Ontology, Location, InterestPoint, Human, Object, Languages, Robot, Middlewares, ABILITIES, \
    ability_to_task_list, Task, ACCEPTED_TYPES, BASE_ENTITIES, ENTITIES_NOT_ALLOWED


class ParseTOMLOntologyException(Exception):
    """
    Raised when something goes wrong while parsing an Ontology TOML file
    """
    pass

def parseOntologyConfig(file_name: str) -> Ontology:
    """
       Parse a TOML ontology file and returns a filled Ontology object

       :param file_name:
       :return:
       """
    print('Parsing Ontology...')

    file = open(file_name, "rb")
    data = tomllib.load(file)

    # === Ontology ===

    ontology = Ontology()

    if 'Ontology' not in data:
        raise ParseTOMLOntologyException('You must provide a "Ontology" table')

    # Ontology > Name

    if 'name' not in data['Ontology']:
        raise ParseTOMLOntologyException('The "Ontology" table must have a "name" key/value')

    if not isinstance(data['Ontology']['name'], str):
        raise ParseTOMLOntologyException('The "Ontology.name" parameter value must be a string')

    ontology.name = data['Ontology']['name']

    # Ontology > Description

    if 'description' not in data['Ontology']:
        raise ParseTOMLOntologyException('The "Ontology" table must have a "description" key/value')

    if not isinstance(data['Ontology']['description'], str):
        raise ParseTOMLOntologyException('The "Ontology.description" parameter value must be a string')

    ontology.description = data['Ontology']['description']

    # Ontology > Language

    if 'language' not in data['Ontology']:
        raise ParseTOMLOntologyException('The "Ontology" table must have a "language" key/value')

    language_str = data['Ontology']['language']
    languages = [lang.value for lang in Languages]

    if not isinstance(language_str, str):
        raise ParseTOMLOntologyException('The "Ontology.language" parameter value must be a string')

    if not language_str in languages:
        raise ParseTOMLOntologyException(f'The "Ontology.language" parameter value "{language_str}" must be a value of the following list: {languages}')

    ontology.name = data['Ontology']['name']


    # === Robot ===

    robot = Robot()

    if 'Robot' not in data:
        raise ParseTOMLOntologyException('You must provide a "Robot" table')

    # Robot > Name

    if 'name' not in data['Robot']:
        raise ParseTOMLOntologyException('The "Robot" table must have a "name" key/value')

    if not isinstance(data['Robot']['name'], str):
        raise ParseTOMLOntologyException('The "Robot.name" parameter value must be a string')

    robot.name = data['Robot']['name']

    # Robot > Middleware

    if 'middleware' not in data['Robot']:
        raise ParseTOMLOntologyException('The "Robot" table must have a "middleware" key/value')

    middlewares_str = data['Robot']['middleware']
    middlewares = [middleware.value for middleware in Middlewares]

    if not isinstance(middlewares_str, str):
        raise ParseTOMLOntologyException('The "Robot.middleware" parameter value must be a string')

    if not middlewares_str in middlewares:
        raise ParseTOMLOntologyException(f'The "Robot.middleware" parameter value "{middlewares_str}" must be a value of the following list: {middlewares}')

    robot.middleware = data['Robot']['middleware']

    # Robot > Abilities

    if 'Abilities' not in data['Robot']:
        raise ParseTOMLOntologyException('The "Robot" table must have a "Abilities" table')

    abilities = data['Robot']['Abilities']

    if not isinstance(abilities, dict):
        raise ParseTOMLOntologyException('The "Robot.Abilities" parameter value must be a table')

    for key in abilities:
        if not key in ABILITIES:
            raise ParseTOMLOntologyException(f'The "Robot.Abilities" parameter keys must be the following list: {list(ABILITIES)}')

        ability = abilities[key]

        if not isinstance(ability, list):
            raise ParseTOMLOntologyException(f'The "Robot.Abilities" parameter value "{key}" must be an array')


        if len(ability) == 1 and ability[0] == '*':
            tasks = ability_to_task_list(key)
            ontology.available_tasks += tasks
        else:
            for task_name in ability:
                if not task_name in ABILITIES[key]:
                    raise ParseTOMLOntologyException(f'The "Robot.Abilities.{key}" parameter value "{task_name}" must be in the following list: {list(ABILITIES[key])}')

                task = Task(task_name, key, ABILITIES[key][task_name]['params'], ABILITIES[key][task_name]['returns'])
                ontology.available_tasks.append(task)

    # === Entities ===

    if 'Entities' not in data:
        raise ParseTOMLOntologyException('The "Robot" table must have a "Entities" table')

    entities = data['Entities']

    if not isinstance(entities, dict):
        raise ParseTOMLOntologyException('The "Ontology.Entities" parameter value must be a table')

    for entity_name in entities:
        entity = entities[entity_name]

        if not isinstance(entity, dict):
            raise ParseTOMLOntologyException(f'The "Ontology.Entities" parameter value "{entity_name}" must be a table')

        if entity_name in BASE_ENTITIES:
            entity_class = eval(entity_name)
        elif entity_name in ENTITIES_NOT_ALLOWED:
            raise ParseTOMLOntologyException(f'The entity name "{entity_name}" is not allowed')
        else:
            entity_class = type(entity_name, (object,), {
                '__annotations__': {}
            })

        for key in entity:
            value_type = type(entity[key])

            if value_type not in ACCEPTED_TYPES:
                raise ParseTOMLOntologyException(f'The "Ontology.Entities.{entity_name}" parameter value "{key}" type must be in the following list: {ACCEPTED_TYPES}')

            entity_class.__annotations__[key] = value_type
            setattr(entity_class, key, entity[key])

            lower_entity_name = entity_name.lower()
            new_task_params = { lower_entity_name: entity_class }
            new_task = Task(f'get_{key}', lower_entity_name, new_task_params, value_type)
            ontology.available_tasks.append(new_task)


        ontology.entities[entity_name] = entity_class

    # ========

    print('Parsing done!')
    #┌└┐┌
    print('┌——————————————————┐')
    print('│ -*- Ontology -*- │')
    print('├——————————————————┘')
    print('│')
    print('│ Name:', ontology.name)
    print('│ Description:', ontology.description)
    print('│ Language:', ontology.language.value)
    print('│')
    print('├————————————┐')
    print('│  Entities  │')
    print('├————————————┘')
    print('│')
    ontology.print_entities(prefix='│ - ')
    print('│')
    print('├—————————┐')
    print('│  Tasks  │')
    print('├—————————┘')
    print('│')
    ontology.print_tasks(prefix='│ - ')
    print('└———————————————— ·')

    return ontology


if __name__ == "__main__":
    ontology = parseOntologyConfig('ontology_v2.toml')