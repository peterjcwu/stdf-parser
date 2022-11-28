import re
from stdfparser import parse, StdfPub
from stdfparser.stdf_sub_txt import StdfSubTxt


def test_record_filter_success():
    stdf_path = r"C:\workspace\Tools\stdf-parser\lab\fc_a1_qfn_wifi_shmoo_min_svc_rssi_mcs4_20220826124302.zip"
    pub = StdfPub(stdf_path)
    sub = StdfSubTxt("base", re.sub(r"\.stdf(\.gz)?$", ".txt", stdf_path))
    parse(pub, sub)
