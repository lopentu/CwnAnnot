from typing import List, Tuple
from .cwn_annot_types import (
    AnnotCommit, AnnotRecord, 
    AnnotError,  AnnotAction, 
    AnnotCategory)
from CwnGraph import CwnGraphUtils

PatchError = Tuple[AnnotError, str]
class CwnPatcher:    
    def __init__(self, commit: AnnotCommit):
        self.commit = commit
        self.errors = []
        
    def patch(self, V, E, meta):                
        tape: List[AnnotRecord] = self.commit.tape
        for annot_x in tape:
            if annot_x.annot_category.is_edge():
                self.patch_edge(V, E, annot_x)
            elif annot_x.annot_category.is_node():
                self.patch_node(V, annot_x)
            else:
                self.errors.append((AnnotError.UnknownAnnotCategory, annot_x.annot_category))

    def patch_edge(self, V, E, rec: AnnotRecord):
        if rec.annot_action == AnnotAction.Delete:
            if rec.cwn_id in E:
                del E[rec.cwn_id]
            else:
                self.errors.append((AnnotError.DeletionError, rec.cwn_id))
        elif rec.annot_action in (AnnotAction.Edit, AnnotAction.Create):
            edge_id = rec.cwn_id
            if edge_id[0] in V and edge_id[1] in V:
                E[edge_id] = rec.data
            else:
                self.errors.append((AnnotError.NodeIdNotFound, rec.cwn_id))

        else:
            self.errors.append((AnnotError.UnsupportedAnnotError, rec.annot_action))

        return E

    def patch_node(self, V, rec: AnnotRecord):
        if rec.annot_action == AnnotAction.Delete:
            if rec.raw_id in V:
                del V[rec.cwn_id]
            else:
                self.errors.append((AnnotError.DeletionError, rec.cwn_id))
        elif rec.annot_action in (AnnotAction.Edit, AnnotAction.Create):
            V[rec.cwn_id] = rec.data
        else:
            self.errors.append((AnnotError.UnsupportedAnnotError, rec.annot_action))

        return V
