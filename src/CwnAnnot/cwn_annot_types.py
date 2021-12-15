from enum import Enum
from datetime import datetime
class AnnotAction(Enum):
    Create = 1
    Edit = 2
    Delete = 3

class AnnotCategory(Enum):
    Lemma = 1
    Sense = 2
    Synset = 3
    Relation = 4
    Other = 5

class AnnotRecord:
    def __init__(self, annoter: str,
                       annot_action:AnnotAction,
                       annot_category: AnnotCategory,
                       raw_id: str=None, data={}):
        self.annoter = annoter
        self.action = annot_action
        self.category = annot_category
        self.raw_id = raw_id
        self.data = data
        self.timestamp = datetime.timestamp(datetime.now())