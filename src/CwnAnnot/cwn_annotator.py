import os
import json
from datetime import datetime
import pickle
from typing import List, Dict, Tuple, Union
from CwnGraph import cwnio
from CwnGraph.cwn_types import (
    CwnSense, CwnLemma, 
    CwnRelation, CwnRelationType,
    CwnSynset, CwnIdNotFoundError)
from CwnGraph.cwn_graph_utils import CwnGraphUtils
from .cwn_annot_types import *
from .cwn_overwatch import CwnOverwatch

class CwnAnnotator:
    def __init__(self, cgu:CwnGraphUtils, annoter):
        self.cgu = cgu
        self.annoter = annoter
        self.V = cgu.V.copy()
        self.E = cgu.E.copy()
        self.tape: List[AnnotRecord] = []
        self.annot_meta = {
            "base_data": cgu.meta,
            "annot_date": datetime.now().strftime("%y%m%d%H%M%S"),
        }

    def __repr__(self):
        n_edit = sum(1 for x in self.tape if x.action == AnnotAction.Edit)
        n_delete = sum(1 for x in self.tape if x.action == AnnotAction.Delete)
        return f"<CwnAnnotator: {self.label}> ({n_edit} Edits, {n_delete} Deletes)"

    @property
    def data(self):
        return (self.V, self.E)

    def load(self, fpath):

        if os.path.exists(fpath):
            print("loading saved session from ", fpath)

            self.meta, self.V, self.E = \
                cwnio.load_annot_json(fpath)
            return True

        else:
            print("cannot find ", fpath)
            return False

    def save(self, fpath):
        label = self.meta["label"]
        cwnio.ensure_dir("annot")
        cwnio.dump_annot_json(self.meta, self.V, self.E, fpath)
        with open(fpath, "wb") as fout:
            pickle.dump((self.V, self.E, self.meta), fout)    
    
    def annotate(self, annot_action: AnnotAction, raw_id=None, data={}):
        rec = AnnotRecord(self.annoter, annot_action, raw_id, data)
        self.tape.append(rec)
        return rec

    def create_lemma(self, lemma:CwnLemma):                        
        self.set_lemma(lemma)
        self.annotate(lemma.id, 
            AnnotAction.Create, AnnotCategory.Lemma,
            raw_id=lemma.id, data=lemma.data)
        return lemma

    def create_sense(self, definition, raw_id=None):
        node_id = self.new_node_id()
        self.record(node_id, AnnotAction.Edit,
                    raw_id=raw_id, annot_type="sense")

        new_sense = CwnSense(node_id, self)
        new_sense.definition = definition
        self.set_sense(new_sense)
        return new_sense

    def create_relation(self, src_id:str, tgt_id:str, rel_type:CwnRelationType):
        raw_ids = (src_id, tgt_id)
        annot_src_id = self.get_id(src_id)
        annot_tgt_id = self.get_id(tgt_id)        
        edge_id = (annot_src_id, annot_tgt_id)

        if not self.get_node_data(annot_src_id):
            raise CwnIdNotFoundError(f"{src_id} not found")
        if not self.get_node_data(annot_tgt_id):
            raise CwnIdNotFoundError(f"{tgt_id} not found")

        self.record(edge_id, AnnotAction.Edit,
                    raw_id=raw_ids, annot_type="relation")
        
        new_rel = CwnRelation(edge_id, self)        
        new_rel.relation_type = rel_type        
        self.set_relation(new_rel)
        return new_rel

    def set_lemma(self, cwn_lemma: CwnLemma):
        self.V[cwn_lemma.id] = cwn_lemma.data()

    def set_sense(self, cwn_sense: CwnSense):
        self.V[cwn_sense.id] = cwn_sense.data()

    def set_synset(self, cwn_synset: CwnSense):
        self.V[cwn_synset.id] = cwn_synset.data()

    def set_relation(self, cwn_relation: CwnRelation):
        self.E[cwn_relation.id] = cwn_relation.data()

    def remove_lemma(self, cwn_lemma: Union[str, CwnLemma]):
        if isinstance(cwn_lemma, CwnLemma):
            lemma_id = cwn_lemma.id
        else:
            lemma_id = cwn_lemma

        if lemma_id in self.V:
            self.record(lemma_id, AnnotAction.Delete, annot_type="lemma")
            del self.V[lemma_id]
            return True
        else:
            return False

    def remove_sense(self, cwn_sense: Union[str, CwnSense]):
        if isinstance(cwn_sense, CwnSense):
            sense_id = cwn_sense.id
        else:
            sense_id = cwn_sense

        if sense_id in self.V:            
            self.record(sense_id, AnnotAction.Delete, annot_type="sense")            
            del self.V[sense_id]
            return True
        else:
            return False

    def remove_relation(self, cwn_relation:Tuple[str, str, CwnRelationType]):
        if isinstance(cwn_relation, CwnRelation):
            relation_id = cwn_relation.id
        else:
            relation_id = cwn_relation

        if relation_id in self.E:
            self.record(relation_id, AnnotAction.Delete, annot_type="relation")
            del self.E[relation_id]
            return True
        else:
            return False

    def get_node_data(self, node_id):
        node_data = self.V.get(node_id, {})
        return node_data

    def get_edge_data(self, edge_id):
        edge_data = self.E.get(edge_id, {})

        return edge_data
