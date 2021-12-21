from enum import Enum
from re import L
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
from hashlib import sha1
from CwnGraph import CwnImage

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


@dataclass
class CommitMetadata:    
    timestamp: float = 0.
    annoter: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, indict):
        inst = cls()
        for k, v in indict:
            if k not in inst.__dict__: continue
            inst.__dict__[k] = v
        return inst

class AnnotCommit:    
    def __init__(self, meta: Dict[str, str], 
                    commit_id: str, 
                    tape: List[AnnotRecord]):
        self.meta = AnnotCommit.from_dict(meta)
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


@dataclass
class BundleMetadata:
    base_image: str = ""
    target_image: str = "" 
    label: str = ""
    timestamp: float = 0.
    annoter: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, indict):
        inst = cls()
        for k, v in indict:
            if k not in inst.__dict__: continue
            inst.__dict__[k] = v
        return inst

class AnnotBundle:
    def __init__(self, meta: Dict[str, str], 
                 commit_ids: List[str]):
        self.meta: BundleMetadata = BundleMetadata.form_dict(meta)
        self.commit_ids = commit_ids                
        self.commits: Dict[str, AnnotCommit] = {}
    
    @property
    def target_image(self):
        return self.meta.target_image

    def is_completed(self):
        return bool(self.meta.target_image)

