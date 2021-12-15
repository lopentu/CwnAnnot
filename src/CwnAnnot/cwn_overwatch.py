from google.cloud import firestore

class CwnOverwatch:
    __instance = None

    @staticmethod
    def getInstance():
        if CwnOverwatch.__instance is None:
            CwnOverwatch.__instance = CwnOverwatch()
        return CwnOverwatch.__instance

    def __init__(self, service_account_info):
        if CwnOverwatch.__instance is not None:
            raise ValueError("CwnOverwatch is a singleton. Use getInstance() instead.")
        
        self.db = firestore.Client.from_service_account_info(service_account_info)
    
    def create_lemma_id(self):
        pass

    def create_sense_id(self):
        pass

    def create_synset_id(self):
        pass
    
    def query_annotations(self, node_type, annot_action, annoter):
        pass

    def query_senses(self, sense_id):
        pass
    
    def query_lemmas(self, lemma_id):
        pass

    def query_synset(self, synset_id):
        pass
    
    def query_relations(self, edge_id):
        pass
        
