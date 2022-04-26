from stdf import DTR
from Semi_ATE import STDF


def test_dtr_repr():
    dtr = STDF.DTR()
    dtr.set_value("TEXT_DAT", "test text")
    print(dtr)

    dtr = DTR()
    dtr.set_value("TEXT_DAT", "test text12c")
    print(dtr)
    print(dtr.__repr__())
