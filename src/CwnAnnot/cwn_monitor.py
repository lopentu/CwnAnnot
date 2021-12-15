
from CwnGraph.cwn_graph_utils import CwnGraphUtils

from CwnGraph import CwnGraphUtils

class CwnMonitor:
    def __init__(self):
        pass

    def check_synsets(self):
        pass

class CwnChecker:
    def check(self, cwn: CwnGraphUtils):
        raise NotImplementedError()

class CwnSynsetChecker(CwnChecker):
    def check(self, cwn:CwnGraphUtils):
        return []