from datetime import datetime
from typing import List, Dict, Tuple, Union
from CwnGraph import cwnio
from CwnGraph.cwn_types import (
    CwnNode,
    CwnSense, CwnLemma, 
    CwnRelation, CwnRelationType,
    CwnSynset, CwnIdNotFoundError)
from CwnGraph.cwn_graph_utils import CwnGraphUtils
from .cwn_patcher import CwnPatcher, PatchError
from .cwn_annot_types import *
from .annot_utils import CwnIdCounter
import logging

logger = logging.getLogger("CwnAnnot.CwnAnnotator")

class CwnAnnotator(CwnGraphUtils):    
    def __init__(self, cgu:CwnGraphUtils, 
                annoter: str, 
                session_name: str,                
                timestamp: float=0.):        

        self.annoter = annoter
        V = cgu.V.copy()
        E = cgu.E.copy()
        meta = cgu.meta.copy()
        super(CwnAnnotator, self).__init__(V, E, meta)

        self.tape: List[AnnotRecord] = []
        self.patched_commits: List[AnnotCommit] = []
        if timestamp == 0.:
            timestamp = datetime.timestamp(datetime.now())
        self.meta.update({
            "annoter": annoter,
            "session": session_name,        
            "timestamp": timestamp    
        })

    def __repr__(self):
        n_edit = sum(1 for x in self.tape if x.annot_action == AnnotAction.Edit)
        n_create = sum(1 for x in self.tape if x.annot_action == AnnotAction.Create)
        n_delete = sum(1 for x in self.tape if x.annot_action == AnnotAction.Delete)
        label = f"{self.meta.get('annoter')}/{self.meta.get('session')}"
        return f"<CwnAnnotator: {label}> ({n_create} Creates, {n_edit} Edits, {n_delete} Deletes)"

    def annotate(self, 
            annot_action: AnnotAction, 
            annot_category: AnnotCategory,
            raw_id=None, data={}):
        rec = AnnotRecord(self.annoter, annot_action, annot_category, raw_id, 
                        self.meta["timestamp"], data)
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
        if node.id in self.V:
            raise ValueError(f"Node ID {node.id} already exists in CWN")

        self.set_vertex(node)
        self.annotate( 
            AnnotAction.Create, annot_category,
            raw_id=node.id, data=node.data())
        return node

    def update_node(self, node: CwnNode, annot_category: AnnotCategory):
        self.set_vertex(node)
        self.annotate( 
            AnnotAction.Edit, annot_category,
            raw_id=node.id, data=node.data())
        return node

    def remove_node(self, node: CwnNode, annot_category: AnnotCategory):        
        self.remove_vertex(node)
        self.annotate( 
            AnnotAction.Delete, annot_category,
            raw_id=node.id, data={})

    def create_lemma(self, lemma: CwnLemma):                        
        return self.create_node(lemma, AnnotCategory.Lemma)

    def create_sense(self, sense: CwnSense):
        return self.create_node(sense, AnnotCategory.Sense)
    
    def create_synset(self, synset: CwnSynset):
        return self.create_node(synset, AnnotCategory.Synset)    

    def update_lemma(self, lemma: CwnLemma):
        return self.update_node(lemma, AnnotCategory.Lemma)
    
    def update_sense(self, sense: CwnSense):
        return self.update_node(sense, AnnotCategory.Sense)
    
    def update_synset(self, synset: CwnSynset):
        return self.update_node(synset, AnnotCategory.Synset)

    def remove_lemma(self, lemma: CwnLemma):
        self.remove_node(lemma, AnnotCategory.Lemma)

    def remove_sense(self, sense: CwnSense):
        self.remove_node(sense, AnnotCategory.Sense)
    
    def remove_synset(self, synset: CwnSynset):
        self.remove_node(synset, AnnotCategory.Synset)


    ##
    ## create Concept

    def create_concept(self, concept: AnnotConcept):
        """ create_concept(self, concept: AnnotConcept)

        A shortcut method creating a pair of CwnLemma and CwnSense. 
        They are marked with a `CN:` prefix in the `lemma` field of CwnLemma 
        and `definition` field of CwnSense. Upon creation, the concept can only be accessed
        with the corresponding CwnLemma and CwnSense.
        """
        cn_lemma = CwnLemma.create(self, 
                    concept.new_lemma_id, 
                    lemma=f"CN:{concept.concept_lemma}", 
                    zhuyin="")
        cn_sense = CwnSense.create(self,
                    concept.new_sense_id,
                    pos=concept.concept_pos,
                    definition="CN:"+concept.concept_definition)
        lemma_node = self.create_lemma(cn_lemma)
        sense_node = self.create_sense(cn_sense)
        rel = CwnRelation.create(self, lemma_node.id, sense_node.id, CwnRelationType.has_sense)
        self.create_relation(rel)
        return (lemma_node, sense_node)

    ##
    ## CRUD on edges (CwnRelation)
    ##     
    def set_edge(self, cwn_relation: CwnRelation):
        edge_id = cwn_relation.id
        self.E[edge_id] = cwn_relation.data()
        src_id, tgt_id = edge_id
        self.edge_src_index.setdefault(src_id, []).append(edge_id)
        self.edge_tgt_index.setdefault(tgt_id, []).append(edge_id)
    
    def remove_edge(self, cwn_relation: CwnRelation):
        if cwn_relation.id in self.E:
            edge_id = cwn_relation.id
            src_id, tgt_id = edge_id
            try:
                self.edge_src_index.get(src_id, []).remove(edge_id)
                self.edge_tgt_index.get(tgt_id, []).remove(edge_id)
            except ValueError:
                pass
            del self.E[edge_id]
        else:
            raise CwnIdNotFoundError(f"{cwn_relation.id} not found when deleting edge")

    def create_relation(self, relation: CwnRelation):                
        if relation.id in self.E:
            raise ValueError(f"Edge ID {relation.id} already exists in CWN")
        self.set_edge(relation)
        self.annotate(AnnotAction.Create, AnnotCategory.Relation,
                    raw_id=relation.id, data=relation.data())                
        return relation
    
    def update_relation(self, relation: CwnRelation):                
        self.set_edge(relation)
        self.annotate(AnnotAction.Update, AnnotCategory.Relation,
                    raw_id=relation.id, data=relation.data())                
        return relation
    
    def remove_relation(self, relation: CwnRelation):                
        self.remove_edge(relation)
        self.annotate(AnnotAction.Delete, AnnotCategory.Relation,
                    raw_id=relation.id, data={})                        
    
    ## 
    ## Cwn Annotation Manipulation Methods (CAMM)
    ##
    def patch(self, commit: AnnotCommit) -> List[PatchError]:
        if commit in self.patched_commits:
            raise ValueError("Commit already applied: "+commit.commit_id)
        self.patched_commits.append(commit)
        patcher = CwnPatcher(commit)        
        patcher.patch(self.V, self.E, self.meta)
        return patcher.errors

    def commit(self) -> AnnotCommit:
        commit_id = AnnotCommit.compute_commit_id(self.tape)
        return AnnotCommit(self.meta, commit_id, self.tape)
    
    def compile(self, image_label, note="") -> Tuple[CwnImage, AnnotBundle]:
        bundle_label = "bundle-" + self.meta["session"]

        img_meta = {
            "image_id": compute_image_id(self.V, self.E),
            "label": image_label,
            "bundle_id": bundle_label,
            "annoter": self.annoter,
            "timestamp": datetime.timestamp(datetime.now()),            
            "note": note
        }
        img = CwnImage(self.V, self.E, img_meta)

        bundle_meta = {
            "base_image": self.meta.get("image_id", "<base-v0.2>"),
            "target_image": img_meta["image_id"],
            "annoter": self.meta["annoter"],
            "timestamp": datetime.timestamp(datetime.now())
        }      

        commit_ids = [x.commit_id for x in self.patched_commits]  
        bundle = AnnotBundle(bundle_label, bundle_meta, commit_ids)

        return img, bundle
