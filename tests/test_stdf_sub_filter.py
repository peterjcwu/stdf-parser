from stdfparser.stdf_sub_filter import StdfSubFilter
from stdfparser import parse, StdfPub


def test_record_filter_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf"
    pub = StdfPub(stdf_path)
    sub = StdfSubFilter("base", stdf_path.replace(".stdf", "_mod.stdf"))
    parse(pub, sub)
