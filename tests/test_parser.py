import os
from stdfparser import ParserBase


def test_parse_lot2():
    parser = ParserBase()
    stdf = os.path.abspath(os.path.join(__file__, os.pardir, "data", "lot2.stdf"))
    assert os.path.isfile(stdf)
    parser.parse(stdf)


def test_parse_lot3():
    parser = ParserBase()
    stdf = os.path.abspath(os.path.join(__file__, os.pardir, "data", "lot3.stdf"))
    assert os.path.isfile(stdf)
    parser.parse(stdf)
