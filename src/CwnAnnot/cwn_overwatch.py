import json
from google.cloud import firestore

class CwnOverwatch:
    __instance = None
    __sainfo = {}

    @staticmethod
    def getInstance(key_path=None):
        if CwnOverwatch.__instance is None:
            if key_path:
                CwnOverwatch.login_with_sainfo(key_path)
            CwnOverwatch.__instance = CwnOverwatch()
        return CwnOverwatch.__instance

    @staticmethod
    def login_with_sainfo(service_account_key_path):
        with open(service_account_key_path, "r") as fin:
            CwnOverwatch.__sainfo = json.load(fin)

    def __init__(self):
        if CwnOverwatch.__instance is not None:
            raise ValueError("CwnOverwatch is a singleton. Use getInstance() instead.")

        service_account_info = CwnOverwatch.__sainfo
        self.db = firestore.Client.from_service_account_info(service_account_info)
        self.meta = self.db.collection("cwn_meta")
        self.sa_email = service_account_info["client_email"].split("@")[0]
    
    def issue_lemma_id(self):        
        @firestore.transactional
        def inner_transaction(trans):
            counter, ref = self.get_counter("lemma_id", trans)
            cur_lemma_id = counter["id"]
            new_lemma_id = "{:06d}".format(int(cur_lemma_id) + 1)
            counter["id"] = new_lemma_id
            trans.set(ref, counter)
            return new_lemma_id
        trans = self.db.transaction()
        new_lemma_id = inner_transaction(trans)
        return new_lemma_id
    
    def issue_sense_id(self, lemma_id):        
        @firestore.transactional
        def inner_transaction(trans):
            counter, ref = self.get_sense_counter(lemma_id, trans)
            new_sense_id = self.increment_sense_id(counter)
            counter["id"] = new_sense_id
            trans.set(ref, counter)
            return new_sense_id
        trans = self.db.transaction()
        new_sense_id = inner_transaction(trans)
        return new_sense_id
    
    def issue_synset_id(self):        
        @firestore.transactional
        def inner_transaction(trans):            
            counter, ref = self.get_counter("synset_id", trans)
            cur_synset_counter = int(counter["id"].replace("syn_", ""))
            new_synset_counter = "{:06d}".format(cur_synset_counter+1)
            new_synset_id = "syn_" + new_synset_counter
            counter["id"] = new_synset_id
            trans.set(ref, counter)
            return new_synset_id

        trans = self.db.transaction()
        new_synset_id = inner_transaction(trans)
        return new_synset_id

    def get_counter(self, doc_id, trans=None):
        ref = self.meta.document(doc_id)
        counter = ref.get(transaction=trans).to_dict()
        return counter, ref

    def get_sense_counter(self, lemma_id, trans=None):
        sense_coll = self.meta.document("sense_ids")
        sense_map = sense_coll.collection("sense_map")
        sense_ref = sense_map.document(lemma_id)
        sense_doc = sense_ref.get(transaction=trans)
        if not sense_doc.exists:
            raise KeyError(f"{lemma_id} not found in registry")
        counter = sense_doc.to_dict()
        return counter, sense_ref

    def increment_sense_id(self, sense_counter):
        lemma_id = sense_counter["id"][:-2]
        cur_sense_id = sense_counter["id"][-2:]
        try:
            cur_sense_id = int(cur_sense_id)
            new_sense_id = cur_sense_id + 1
            if new_sense_id > 99:
                new_sense_id = "a0"
            else:
                new_sense_id = "{:02d}".format(new_sense_id)
        except ValueError:
            # there might be an alphabet in the second last character
            # e.g. 打[052291a3]
            prefix = sense_counter["id"][-2]
            cur_sense_id = int(sense_counter["id"][-1])
            new_sense_id = cur_sense_id + 1
            if new_sense_id > 9:
                prefix = chr(ord(prefix) + 1)
                new_sense_id = prefix + "0"
            else:
                new_sense_id = prefix + str(new_sense_id)
        return lemma_id + new_sense_id

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

