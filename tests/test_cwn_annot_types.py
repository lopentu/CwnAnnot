from CwnAnnot import *

def test_AnnotRecord_todict():
    rec_x = AnnotRecord("me", AnnotAction.Create, AnnotCategory.Lemma, "asdf")
    data = rec_x.to_dict()
    rec_y = AnnotRecord.from_dict(data)
    assert hash(rec_x) == hash(rec_y)