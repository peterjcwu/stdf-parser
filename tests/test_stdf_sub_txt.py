import re
from stdfparser.parse import parse
from stdfparser.stdf_sub_txt import StdfSubTxt


def test_record_filter_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep_mod.stdf"
    # stdf_path = r"C:\Users\nxf79056\Downloads\KW73P_RFn_PC1_r1_KW73P02-F0_20221021171527.stdf.gz"
    parse(stdf_path, StdfSubTxt("base", re.sub(r"\.stdf(\.gz)?$", ".txt", stdf_path)))
