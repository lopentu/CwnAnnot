from CwnGraph import CwnGraphUtils

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
    
    def get_hash(self, cwn: CwnGraphUtils):
        pass
    
    def get_parent(self, cwn_version):
        pass