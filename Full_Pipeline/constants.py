from typing_extensions import List

from models import InterestPoint, Object, Human, Location
from pipeline import Task, TaskList, Goal, RetrieveProperty, GoalList

BASE_TASKS = TaskList([
    # navigation_2d
    Task('get_current_interest_point', category='navigation_2d', params={}, returns=InterestPoint),
    Task('get_object_interest_point', category='navigation_2d', params={'object': Object}, returns=InterestPoint),
    Task('get_human_interest_point', category='navigation_2d', params={'human': Human}, returns=InterestPoint),
    Task('get_interest_point_location', category='navigation_2d', params={'interest_point': InterestPoint}, returns=Location),
    Task('go_to_location', category='navigation_2d', params={'location': Location}, returns=bool),
    Task('go_to_interest_point', category='navigation_2d', params={'interest_point': InterestPoint}, returns=bool),

    # vision
    Task('detect_object', category='vision', params={'object': Object}, returns=Object),
    Task('detect_human', category='vision', params={'human': Human}, returns=Human),
    Task('detect_objects', category='vision', params={}, returns=List[Object]),
    Task('detect_humans', category='vision', params={}, returns=List[Object]),
    # TODO: 'gesture_recognition'

    # object_grasping
    Task('grab_object', category='object_grasping', params={'object': Object}, returns=bool),
    Task('put_object', category='object_grasping', params={'object': Object}, returns=bool),
    # TODO: 'push_object', 'pull_object'

    # speech_recognition
    Task('speech_to_text', category='speech_recognition', params={}, returns=str),
    Task('detect_sound', category='speech_recognition', params={}, returns=bool),
    # TODO: 'detect_language'

    # text_to_speech
    Task('say', category='text_to_speech', params={'text': str}, returns=None),
    # TODO: 'change_language'

    # display
    Task('display_text', category='display', params={'text': str}, returns=None),
    # TODO: 'display_image', 'display_video'

    # audio
    Task('play_sound', category='audio', params={'sound_name': str}, returns=None),
])

BASE_GOALS = GoalList([
    Goal(
        'DESCRIPTION',
        params=[],
        pipeline=[],
        validation=lambda: f'Great.',
        finished=lambda: '',
    ),
    Goal(
        'GRAB AN OBJECT',
        params=['OBJECT'],
        pipeline=[
            BASE_TASKS['detect_object'],
            BASE_TASKS['grab_object'],
        ],
        validation=lambda object: f'I am going to grab a {object}.',
        finished=lambda object: f'I am done grabbing a {object}.',
    ),
    Goal(
        'GRAB AN OBJECT IN A LOCATION',
        params=['OBJECT', 'LOCATION'],
        pipeline=[
            BASE_TASKS['go_to_location'],
            BASE_TASKS['detect_object'],
            BASE_TASKS['grab_object'],
        ],
        validation=lambda object, location: f'I am going to grab a {object} in the {location}.',
        finished=lambda object, location: f'I am done grabbing {object} in the {location}.',
    ),
    Goal(
        'BRING AN OBJECT TO SOMEONE',
        params=['OBJECT', 'HUMAN'],
        pipeline=[
            BASE_TASKS['detect_object'],
            BASE_TASKS['grab_object'],
            BASE_TASKS['detect_human'],
            RetrieveProperty(Human, InterestPoint, 'interest_point'),
            BASE_TASKS['go_to_interest_point'],
        ],
        validation=lambda object, human: f'I am going to bring a {object} to {human}.',
        finished=lambda object, human: f'I am done bringing {object} to {human}.',
    ),
    Goal(
        'BRING AN OBJECT TO SOMEONE FROM A LOCATION',
        params=['OBJECT', 'HUMAN', 'LOCATION'],
        pipeline=[
            BASE_TASKS['go_to_location'],
            BASE_TASKS['detect_object'],
            BASE_TASKS['grab_object'],
            BASE_TASKS['detect_human'],
            RetrieveProperty(Human, InterestPoint, 'interest_point'),
            BASE_TASKS['go_to_interest_point'],
        ],
        validation=lambda object, human, location: f'I am going to bring a {object} to {human} from the {location}.',
        finished=lambda object, human, location: f'I am done bringing {object} to {human} from the {location}.',
    ),
    Goal(
        'SAY SOMETHING',
        params=[],
        pipeline=[
        ],
        validation=lambda _: f'',
        finished=lambda _: f'',
    ),
    Goal(
        'GO TO LOCATION',
        params=['LOCATION'],
        pipeline=[
            BASE_TASKS['go_to_location'],
        ],
        validation=lambda location: f'I am going to the {location}',
        finished=lambda location: f'I am done going to the {location}',
    ),
])
