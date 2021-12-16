from enum import Enum
from datetime import datetime
from base64 import b64encode

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
                       raw_id: str, data={}):          
        timestamp = datetime.timestamp(datetime.now())
        action_label = str(annot_action).replace("AnnotAction", "")
        self.annot_id = f"{annoter}-{action_label}-{raw_id}-{timestamp}"
        self.annoter = annoter
        self.action = annot_action
        self.category = annot_category
        self.raw_id = raw_id
        self.data = data
        self.timestamp = timestamp