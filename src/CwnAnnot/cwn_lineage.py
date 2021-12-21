from CwnGraph import CwnGraphUtils

from CwnAnnot.cwn_annot_types import AnnotCommit

class CwnLinage:
    __instance = None

    @staticmethod
    def getInstance():
        if CwnLinage.__instance is None:
            CwnLinage.__instance = CwnLinage()

        return CwnLinage.__instance

    def __init__(self):
        if CwnLinage.__instance is not None:
            raise ValueError("CwnLinage is a singleton class. Use getInstance().")
    
    def create_commit(self, commit: AnnotCommit):
        pass

    def get_commit(self, commit_id) -> AnnotCommit:
        pass

    def create_bundle(self, base_image, bundle_label):
        pass

    def get_bundle(self, bundle_label):
        pass

    def delete_bundle(self, bundle_label):
        pass

    def get_image(self, image_label):
        pass

    def create_image(self, V, E, meta):
        pass
