from typing import List
from .cwn_annot_types import AnnotRecord, AnnotAction
from CwnGraph import CwnGraphUtils

class CwnPatcher:    
    def __init__(self, base: CwnGraphUtils):
        self.V = self.base.V.copy()
        self.E = self.base.E.copy()        
        self.meta = self.base.meta.copy()
    
    @property
    def V_patched(self):
        return self.V

    @property
    def E_patched(self):
        return self.E

    @property
    def meta_patched(self):
        return self.meta

    def patch(self, annots: List[AnnotRecord]):                
        return (self.V, self.E, self.meta)
    

    