from parse import parse
from stdf_sub_wlan_sweep import StdfSubWlanSweep


def test_stdf_sub_wlan_sweep_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep3.stdf"
    parse(stdf_path, StdfSubWlanSweep("sweep"))
