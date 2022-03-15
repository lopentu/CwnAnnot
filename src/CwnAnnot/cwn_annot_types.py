from enum import Enum
from re import L
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
import pickle
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
        return 1 <= self.value <= 3

    def is_edge(self):
        return self.value == 4

class AnnotError(Enum):
    DeletionError = 10
    NodeIdNoutFoundError = 20
    UnsupportedAnnotError = 91
    UnknownAnnotCategory = 92

@dataclass 
class AnnotConcept:
    new_lemma_id: str
    new_sense_id: str
    concept_lemma: str
    concept_pos: str
    concept_definition: str        

@dataclass
class AnnotRecord:
    annoter: str
    annot_action: AnnotAction
    annot_category: AnnotCategory
    cwn_id: str
    timestamp: float = 0.
    data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.timestamp == 0.:
            self.timestamp = datetime.timestamp(datetime.now())        
        action_label = self.annot_action.name
        self.annot_id = f"{self.annoter}-{action_label}-{self.cwn_id}-{self.timestamp}"

    def __repr__(self):
        return f"<AnnotRecord[{self.annot_action.name}/{self.annot_category.name}] ({self.cwn_id})>"

    def __hash__(self):
        return hash(self.annot_id)
    
    def to_dict(self):
        outdict = dataclasses.asdict(self)
        outdict["annot_action"] = self.annot_action.name
        outdict["annot_category"] = self.annot_category.name
        return outdict

    @classmethod
    def from_dict(cls, indict):
        indict = indict.copy()
        indict["annot_action"] = AnnotAction[indict["annot_action"]]
        indict["annot_category"] = AnnotCategory[indict["annot_category"]]
        cwn_id = indict["cwn_id"]
        if isinstance(cwn_id, list):
            indict["cwn_id"] = tuple(cwn_id)
        return AnnotRecord(**indict)

@dataclass
class CommitMetadata:
    timestamp: float = 0.
    annoter: str = ""
    session: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, indict):
        inst = cls()
        for k, v in indict.items():
            if k not in inst.__dict__: continue
            inst.__dict__[k] = v
        return inst

class AnnotCommit:
    def __init__(self, meta: Dict[str, str],
                    commit_id: str,
                    tape: List[AnnotRecord]):
        self.meta = CommitMetadata.from_dict(meta)
        self.commit_id = commit_id
        self.__tape: List[AnnotRecord] = tape
    
    def __repr__(self):
        return f"<AnnotCommit: {self.commit_id}, {len(self.__tape)} records>"

    def __hash__(self):
        return hash(self.commit_id)

    def __eq__(self, other):
        if isinstance(other, AnnotCommit):
            return self.commit_id == other.commit_id
        else:
            return False

    @classmethod
    def from_dict(cls, indict):        
        meta = indict["meta"]
        commit_id = indict["commit_id"]
        tape = [AnnotRecord.from_dict(x) for x in indict["tape"]]
        return AnnotCommit(meta, commit_id, tape)

    @property
    def tape(self):
        return self.__tape

    @staticmethod
    def compute_commit_id(tape: List[AnnotRecord]):        
        h = sha1()
        h.update(pickle.dumps(tape))
        return h.digest().hex()

    @property
    def note(self):
        return self.meta.get("note", "")
    
    @note.setter
    def set_note(self, value:str):
        self.meta["note"] = value

    def to_dict(self):
        out_dict = {
            "meta": dataclasses.asdict(self.meta), 
            "commit_id": self.commit_id,
            "tape": [x.to_dict() for x in self.__tape]
            }
        return out_dict

@dataclass
class BundleMetadata:
    base_image: str = ""
    target_image: str = ""    
    timestamp: float = 0.
    annoter: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, indict):
        inst = cls()
        for k, v in indict.items():
            if k not in inst.__dict__: continue
            inst.__dict__[k] = v
        return inst        

class AnnotBundle:
    def __init__(self, label: str, 
                 meta: Dict[str, str],
                 commit_ids: List[str]):
        self.label = label
        self.meta: BundleMetadata = BundleMetadata.from_dict(meta)
        self.commit_ids = commit_ids
    
    def __repr__(self):
        return f"<AnnotBundle: {self.label}, {len(self.commit_ids)} commits>"

    @classmethod
    def from_dict(cls, indict):        
        label = indict["label"]
        meta = indict["meta"]        
        commit_ids = indict["commit_ids"]
        return AnnotBundle(label, meta, commit_ids)
    
    def compute_bundle_id(self):  
        h = sha1()
        h.update(pickle.dumps(self.commit_ids))
        return h.digest().hex()

    @property
    def target_image(self):
        return self.meta.target_image

    @property
    def note(self):
        return self.meta.get("note", "")
    
    @note.setter
    def set_note(self, value:str):
        self.meta["note"] = value

    def is_completed(self):
        return bool(self.meta.target_image)

    def to_dict(self):
        out_dict = {
            "label": self.label,
            "meta": dataclasses.asdict(self.meta), 
            "commit_ids": self.commit_ids
            }
        return out_dict

def compute_image_id(V, E, base_id=""):
    from hashlib import sha1
    import pickle    
    h = sha1()
    h.update(base_id.encode())
    h.update(pickle.dumps(V))
    h.update(pickle.dumps(E))
    return h.digest().hex()


