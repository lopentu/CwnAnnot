from enum import Enum
from re import L
from typing import List
from datetime import datetime
from hashlib import sha1

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

    def is_node(self):
        return 1 <= int(self) <= 3
    
    def is_edge(self):
        return int(self) == 4


class AnnotError(Enum):
    DeletionError = 10
    NodeIdNoutFoundError = 20
    UnsupportedAnnotError = 91
    UnknownAnnotCategory = 92    

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
    
    def __hash__(self):
        return hash(self.annot_id)

class AnnotCommit:
    def __init__(self, commit_id, tape=[], meta={}):
        self.meta = meta
        self.commit_id = commit_id
        self.__tape: List[AnnotRecord] = tape
    
    @property
    def tape(self):
        return self.__tape

    @staticmethod
    def compute_commit_id(tape: List[AnnotRecord]):
        h = sha1()
        for rec_x in tape:
            h.update(hash(rec_x).to_bytes(32, 'little'))
        return h.digest().hex()

    @classmethod
    def create(cls, tape: List[AnnotRecord], commit_meta): 
        commit_id = AnnotCommit.compute_commit_id(tape)
        AnnotCommit(commit_id, commit_meta, tape)

class AnnotBranch:
    def __init__(self, commits, top_image=None):
        self.commits: List[AnnotCommit] = commits
        self.__top_image = top_image
    
    @property
    def top_image(self):
        return self.__top_image

    def has_closed(self):
        return self.top_image is not None