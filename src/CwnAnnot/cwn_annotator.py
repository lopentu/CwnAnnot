import os
import json
from datetime import datetime
import pickle
from typing import List, Dict, Tuple, Union
from CwnGraph import cwnio
from CwnGraph.cwn_types import (
    CwnNode,
    CwnSense, CwnLemma, 
    CwnRelation, CwnRelationType,
    CwnSynset, CwnIdNotFoundError)
from CwnGraph.cwn_graph_utils import CwnGraphUtils

from CwnAnnot.cwn_patcher import CwnPatcher
from .cwn_annot_types import *
from .cwn_overwatch import CwnOverwatch

class CwnAnnotator:
    def __init__(self, cgu:CwnGraphUtils, 
                annoter: str, 
                session_name: str):
        self.cgu = cgu
        self.annoter = annoter
        self.V = cgu.V.copy()
        self.E = cgu.E.copy()
        self.meta = cgu.meta.copy()
        self.tape: List[AnnotRecord] = []
        self.meta.update({
            "annoter": annoter,
            "session": session_name,
            "annot_date": datetime.now().strftime("%y%m%d%H%M%S"),
        })

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

    def annotate(self, 
            annot_action: AnnotAction, 
            annot_category: AnnotCategory,
            raw_id=None, data={}):
        rec = AnnotRecord(self.annoter, annot_action, annot_category, raw_id, data)
        self.tape.append(rec)
        return rec
    
    ##
    ## CRUD on vertices (CwnNode, CwnSense, CwnLemma, CwnSynset)
    ## 
    ## There are three layers of operations:
    ## * graph data level: set_vertex, remove_vertex
    ## * annotation level: create_node, udpate_node, remove_node
    ##      this level binds the data operation and annotation records
    ## * CWN type level: create_lemma, update_lemma, remove_lemma,
    ##      create_sense, update_sense, ...
    ##      This level provides operation interface to end users.

    def set_vertex(self, node: CwnNode):
        self.V[node.id] = node.data()
    
    def remove_vertex(self, node: CwnNode):
        if node.id in self.V:
            del self.V[node.id]
        else:
            raise CwnIdNotFoundError(f"{node.id} not found when deleting")

    def create_node(self, node: CwnNode, annot_category: AnnotCategory):
        self.set_vertex(node)
        self.annotate( 
            AnnotAction.Create, annot_category,
            raw_id=node.id, data=node.data)
        return node

    def update_node(self, node: CwnNode, annot_category: AnnotCategory):
        self.set_vertex(node)
        self.annotate( 
            AnnotAction.Edit, annot_category,
            raw_id=node.id, data=node.data)
        return node

    def remove_node(self, node: CwnNode, annot_category: AnnotCategory):        
        self.delete_vertex(node)
        self.annotate( 
            AnnotAction.Delete, annot_category,
            raw_id=node.id, data={})

    def create_lemma(self, lemma: CwnLemma):                        
        self.create_node(lemma, AnnotCategory.Lemma)

    def create_sense(self, sense: CwnSense):
        self.create_node(sense, AnnotCategory.Sense)
    
    def create_synset(self, synset: CwnSynset):
        self.create_node(synset, AnnotCategory.Synset)    

    def update_lemma(self, lemma: CwnLemma):
        self.update_node(lemma, AnnotCategory.Lemma)
    
    def update_sense(self, sense: CwnSense):
        self.update_node(sense, AnnotCategory.Sense)
    
    def update_synset(self, synset: CwnSynset):
        self.update_node(synset, AnnotCategory.Synset)

    def remove_lemma(self, lemma: CwnLemma):
        self.remove_node(lemma, AnnotCategory.Lemma)

    def remove_sense(self, sense: CwnSense):
        self.remove_node(sense, AnnotCategory.Sense)
    
    def remove_synset(self, synset: CwnSynset):
        self.remove_node(synset, AnnotCategory.Synset)

    ##
    ## CRUD on edges (CwnRelation)
    ##     
    def set_edge(self, cwn_relation: CwnRelation):
        self.E[cwn_relation.id] = cwn_relation.data()
    
    def remove_edge(self, cwn_relation: CwnRelation):
        if cwn_relation.id in self.E:
            del self.E[cwn_relation.id]
        else:
            raise CwnIdNotFoundError(f"{cwn_relation.id} not found when deleting edge")

    def create_relation(self, relation: CwnRelation):                
        self.set_edge(relation)
        self.annotate(AnnotAction.Create, AnnotCategory.Relation,
                    raw_id=relation.id, data=relation.data)                
        return relation
    
    def update_relation(self, relation: CwnRelation):                
        self.set_edge(relation)
        self.annotate(AnnotAction.Update, AnnotCategory.Relation,
                    raw_id=relation.id, data=relation.data)                
        return relation
    
    def remove_relation(self, relation: CwnRelation):                
        self.remove_edge(relation)
        self.annotate(AnnotAction.Delete, AnnotCategory.Relation,
                    raw_id=relation.id, data={})                
        return relation    
    
    ## 
    ## Interaction methods
    ##
    def patch(self, commit: AnnotCommit) -> None:
        patcher = CwnPatcher(commit)
        self.V, self.E, self.meta = patcher.patch(self.V, self.E, self.meta)
    
    def patch_all(self, bundle: AnnotBundle) -> None:
        bundle.load_commits()
        for commit_x in bundle.commits:
            self.patch(commit_x)

    def commit(self) -> AnnotCommit:
        commit_id = AnnotCommit.compute_commit_id(self.tape)
        return AnnotCommit(self.meta, commit_id, self.tape)
    
    def compile(self) -> CwnImage:
        img = CwnImage(self.V, self.E, self.meta)
