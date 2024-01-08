
from evaluator import from_srl_string_to_obj


acceptable_frames = {
    "MOTION": [ "GOAL", "THEME", "DIRECTION", "PATH", "MANNER", "AREA", "DISTANCE","SOURCE" ],
    "BRINGING": [ "THEME", "GOAL", "BENEFICIARY", "AGENT", "SOURCE", "MANNER", "AREA"],
    "COTHEME": [ "COTHEME", "MANNER", "GOAL", "THEME", "SPEED", "PATH", "AREA" ],
    "LOCATING": [ "PHENOMENON", "GROUND", "COGNIZER", "PURPOSE", "MANNER" ],
    "INSPECTING": [ "GROUND", "DESIRED_STATE", "INSPECTOR", "UNWANTED_ENTITY" ],
    "TAKING": [ "THEME", "SOURCE", "AGENT", "PURPOSE" ],
    "CHANGE_DIRECTION": [ "DIRECTION", "ANGLE", "THEME", "SPEED" ],
    "ARRIVING": [ "GOAL", "PATH", "MANNER", "THEME" ],
    "GIVING": [ "RECIPIENT", "THEME", "DONOR", "REASON" ],
    "PLACING": [ "THEME", "GOAL", "AGENT", "AREA" ],
    "CLOSURE": [ "CONTAINING_OBJECT", "CONTAINER_PORTAL", "AGENT", "DEGREE" ],
    "BEING_LOCATED": [ "THEME", "LOCATION", "PLACE" ],
    "CHANGE_OPERATIONAL_STATE": [ "DEVICE", "OPERATIONAL_STATE", "AGENT" ],
    "ATTACHING": [ "GOAL", "ITEM", "ITEMS" ],
    "RELEASING": [ "THEME", "GOAL" ],
    "PERCEPTION_ACTIVE": [ "PHENOMENON", "MANNER" ],
    "BEING_IN_CATEGORY": [ "ITEM", "CATEGORY" ],
    "MANIPULATION": [ "ENTITY" ],
}

# bring the book and the journal here, both are on the table
# BRINGING(Goal(e1, e2), Theme("here"), Agent(r1)) & BEING_LOCATED(Place(t1))
def is_formula_well_formed(formula: str, verbose = False) -> bool:
    object_list = from_srl_string_to_obj(formula)

    for frame in object_list:
        if frame['name'].upper() not in acceptable_frames.keys():
            if verbose: 
                print("FRAME " + frame['name'] + " not acceptable")
            return False
        for fe in frame['frameElements']:
            if fe['name'].upper() not in acceptable_frames[frame['name'].upper()]:
                if verbose: 
                    print("FRAME ELEMENT" + fe['name'] + " not acceptable")
                return False

    return True