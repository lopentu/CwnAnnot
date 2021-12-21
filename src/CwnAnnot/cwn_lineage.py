import json
from google.cloud import firestore
from .cwn_annot_types import AnnotCommit

class CwnLineage:
    __instance = None
    __sainfo = None

    @staticmethod
    def getInstance(key_path=None):
        if CwnLineage.__instance is None:            
            CwnLineage.login_with_sainfo(key_path)
            CwnLineage.__instance = CwnLineage()
        return CwnLineage.__instance

    @staticmethod
    def login_with_sainfo(service_account_key_path):
        if not service_account_key_path:
            raise ValueError("Please specify service account")
        with open(service_account_key_path, "r") as fin:
            CwnLineage.__sainfo = json.load(fin)

    def __init__(self):
        if CwnLineage.__instance is not None:
            raise ValueError("CwnLinage is a singleton class. Use getInstance().")
        service_account_info = CwnLineage.__sainfo
        self.db = firestore.Client.from_service_account_info(service_account_info)        
        self.sa_email = service_account_info["client_email"].split("@")[0]
    
    def create_commit(self, commit: AnnotCommit):
        commit_coll = self.db.collection("commits")
        doc_ref = commit_coll.document(commit.commit_id)
        return doc_ref.set(commit.to_dict())                

    def get_commit(self, commit_id) -> AnnotCommit:
        commit_coll = self.db.collection("commits")
        doc_ref = commit_coll.document(commit_id)
        commit_dict = doc_ref.get().to_dict()
        commit = AnnotCommit.from_dict(commit_dict)
        return commit

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
