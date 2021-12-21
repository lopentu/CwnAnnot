from CwnGraph import CwnGraphUtils
from CwnGraph import CwnLemma

class CwnIdCounter:
    def __init__(self, cgu: CwnGraphUtils, 
            extra_lemma_ids=[], 
            extra_synset_ids=[], 
            extra_lemma_senses={}):        
        lemma_ids = []
        synset_ids = []
        for k, v in cgu.V.items():
            if v["node_type"] == "lemma":
                lemma_ids.append(k)
            if v["node_type"] == "synset":
                synset_ids.append(k)                

        for x in extra_lemma_ids:
            lemma_ids.append(x)
        for x in extra_synset_ids:
            synset_ids.append(x)

        lemma_ids.sort(key=lambda x: (len(x), x))
        synset_ids.sort(key=lambda x: (len(x), x))

        self.lemma_ids = lemma_ids
        self.synset_ids = synset_ids

        self.lemma_senses = self.get_lemma_sense_ids(lemma_ids, cgu, extra_lemma_senses)

    def last_lemma_id(self):
        return self.lemma_ids[-1]
    
    def last_synset_id(self):
        return self.synset_ids[-1]
    
    def last_sense_id(self, lemma_id):
        if lemma_id not in self.lemma_senses:
            self.lemma_senses[lemma_id] = lemma_id + "00"
        return self.lemma_senses[lemma_id]

    def get_lemma_sense_ids(self, lemma_ids, cgu, extra_lemma_senses={}):        
        lemma_senses = {}
        for lid in lemma_ids:
            lemma = CwnLemma(lid, cgu)
            senses = lemma.senses
            sense_ids = [x.id for x in senses] + extra_lemma_senses.get(lemma.id, [])
            sense_ids = sorted(sense_ids)            
            lemma_senses[lemma.id] = sense_ids[-1] if sense_ids else (lemma.id+"00")
        return lemma_senses

    def new_lemma_id(self):
        lemma_id = self.last_lemma_id()
        new_id = "{:06d}".format(int(lemma_id) + 1)
        self.lemma_ids.append(new_id)
        return new_id
    
    def new_synset_id(self):
        synset_id = self.last_synset_id()
        new_id = "syn_{:06d}".format(int(synset_id[4:]) + 1)        
        self.synset_ids.append(new_id)
        return new_id

    def new_sense_id(self, lemma_id):
        last_sense_id = self.last_sense_id(lemma_id)
        lemma_id = last_sense_id[:-2]
        cur_sense_id = last_sense_id[-2:]
        try:
            cur_sense_id = int(cur_sense_id)
            new_sense_num = cur_sense_id + 1
            if new_sense_num > 99:
                new_sense_num = "a0"
            else:
                new_sense_num = "{:02d}".format(new_sense_num)
        except ValueError:
            # there might be an alphabet in the second last character
            # e.g. 打[052291a3]
            prefix = last_sense_id["id"][-2]
            cur_sense_id = int(last_sense_id[-1])
            new_sense_num = cur_sense_id + 1
            if new_sense_num > 9:
                prefix = chr(ord(prefix) + 1)
                new_sense_num = prefix + "0"
            else:
                new_sense_num = prefix + str(new_sense_num)

        self.lemma_senses[lemma_id] = lemma_id + new_sense_num
        return lemma_id + new_sense_num   
