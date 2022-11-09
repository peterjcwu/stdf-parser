import re
from stdfparser import parse, StdfPub
from stdfparser.stdf_sub_txt import StdfSubTxt


def test_record_filter_success():
    stdf_path = r"C:\workspace\Tools\stdf-parser\lab\fc_bathtub_20211025110838.stdf.gz"
    pub = StdfPub(stdf_path)
    sub = StdfSubTxt("base", re.sub(r"\.stdf(\.gz)?$", ".txt", stdf_path))
    parse(pub, sub)
