from pathlib import Path
import pytest
from CwnAnnot.cwn_overwatch import CwnOverwatch

@pytest.fixture()
def watcher():
    CwnOverwatch.login_with_sainfo(
        Path(__file__).parent / "../var/cwnannot-c493274d28a8.json")
    return CwnOverwatch.getInstance()

@pytest.mark.skip()   
def test_get_counter(watcher):        
    assert watcher.get_counter("lemma_id") != None
    assert watcher.get_counter("synset_id") != None

def test_increment_sense_id(watcher):
    assert watcher.increment_sense_id({"id": "052291b5"}) == "052291b6"
    assert watcher.increment_sense_id({"id": "052291c9"}) == "052291d0"
    assert watcher.increment_sense_id({"id": "05229101"}) == "05229102"
    assert watcher.increment_sense_id({"id": "05229199"}) == "052291a0"