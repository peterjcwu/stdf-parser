import os
from parser_base import ParserBase


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


def test_parse_fd():
    parser = ParserBase()
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\"FC_CHAR_SRH_gang__1111_20211111092056.stdf.gz")
    assert os.path.isfile(stdf)
    parser.parse(stdf)


def test_parse_fd2():
    stdf = os.path.abspath(r"C:\Users\nxf79056\Downloads\TR7W6414.000_SYSB02BMJ000_20220116125443.stdf.gz")
    assert os.path.isfile(stdf)
    ParserBase().parse(stdf)
