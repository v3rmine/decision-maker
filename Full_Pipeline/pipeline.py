from typing_extensions import Optional, List


class PipelineException(Exception):
    pass


class PipelineElement:
    """
        Mother class of Task, Condition and RetrieveProperty
    """
    pass


class Condition(PipelineElement):
    """
        TODO
    """

    def __init__(self, condition_value):
        self.condition_value = condition_value

    def fit(self, input_value) -> bool:
        return input_value == self.condition_value


class RetrieveProperty(PipelineElement):
    """
        Output a property retrieved from an input
    """

    def __init__(self, input_type: type, output_type: type, value_key: str):
        self.input_type = input_type
        self.output_type = output_type
        self.value_key = value_key

    def fit(self, input_value):
        if type(input_value) is not self.input_type:
            raise PipelineException(f'\"{type(input_value)}\" is not equal to \"{self.input_type}\"')
        else:
            return getattr(input_value, self.value_key)


class Task(PipelineElement):
    """
        A task to be executed in the pipeline
    """

    def __init__(self, name: str, category: str, params: dict, returns: Optional[type]):
        self.name = name
        self.category = category
        self.params = params
        self.returns = returns


class Goal:
    """
        A goal that mainly represent a sequence of tasks
    """

    def __init__(self, name: str, params: List[str], pipeline: List[PipelineElement], validation: callable, finished: callable):
        self.name = name
        self.params = params
        self.pipeline = pipeline
        self.validation = validation
        self.finished = finished


class GoalList(list):
    """
        A rewrite of list using the "name" property as the item key
    """

    def __init__(self, elements: List[Goal]):
        super(GoalList, self).__init__(elements)

    def __getitem__(self, key) -> Goal:
        for item in self:
            if item.name == key:
                return item
        raise Exception(f'Key \"{key}\" not found in list')


class TaskList(list):
    """
        A rewrite of list using the "name" property as the item key that can also use the "category" property
    """

    def __init__(self, elements: List[Task]):
        super(TaskList, self).__init__(elements)

    def __getitem__(self, key) -> Task:
        for item in self:
            if item.name == key:
                return item
        raise Exception(f'Key \"{key}\" not found in list')

    def __contains__(self, key) -> bool:
        for item in self:
            if item.name == key:
                return True
        return False

    def get_categories(self):
        categories = []
        for item in self:
            if item not in categories:
                categories.append(item.category)
        return categories

    def group_by_category(self, category: str):
        task_list = TaskList([])
        for item in self:
            if item.category == category:
                task_list.append(item)
        return task_list
