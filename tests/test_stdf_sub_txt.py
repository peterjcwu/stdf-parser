from stdfparser.parse import parse
from stdfparser.stdf_sub_txt import StdfSubTxt


def test_record_filter_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep_mod.stdf"
    parse(stdf_path, StdfSubTxt("base", stdf_path.replace(".stdf", ".txt")))
