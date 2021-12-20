from typing import List
from .cwn_annot_types import (
    AnnotCommit, AnnotRecord, 
    AnnotError,  AnnotAction, 
    AnnotCategory)
from CwnGraph import CwnGraphUtils

class CwnPatcher:    
    def __init__(self, commit: AnnotCommit):
        self.commit = commit
        self.errors = []
        
    def patch(self, V, E, meta):                
        tape: List[AnnotRecord] = self.commit.tape
        for annot_x in tape:
            if annot_x.category.is_edge():
                self.patch_edge(V, E, annot_x)
            elif annot_x.category.is_node():
                self.patch_node(V, annot_x)
            else:
                self.errors.append((AnnotError.UnknownAnnotCategory, annot_x.category))

    def patch_edge(self, V, E, rec: AnnotRecord):
        if rec.action == AnnotAction.Delete:
            if rec.raw_id in E:
                del E[rec.raw_id]
            else:
                self.errors.append((AnnotError.DeletionError, rec.raw_id))
        elif rec.action in (AnnotAction.Edit, AnnotAction.Create):
            edge_id = rec.raw_id
            if edge_id[0] in V and edge_id[1] in V:
                E[rec.raw_id] = rec.data
            else:
                self.errors.append((AnnotError.NodeIdNotFound, rec.raw_id))

        else:
            self.errors.append((AnnotError.UnsupportedAnnotError, rec.action))

        return E

    def patch_node(self, V, rec: AnnotRecord):
        if rec.action == AnnotAction.Delete:
            if rec.raw_id in V:
                del V[rec.raw_id]
            else:
                self.errors.append((AnnotError.DeletionError, rec.raw_id))
        elif rec.action in (AnnotAction.Edit, AnnotAction.Create):
            V[rec.raw_id] = rec.data
        else:
            self.errors.append((AnnotError.UnsupportedAnnotError, rec.action))

        return V

    def patch_meta(self, meta, commit_meta):
        return meta
