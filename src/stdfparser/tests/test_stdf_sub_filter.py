from stdf_sub_filter import StdfSubFilter
from parse import parse


def test_record_filter_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf"
    parse(stdf_path, StdfSubFilter, ("base", stdf_path.replace(".stdf", "_mod.stdf")))
