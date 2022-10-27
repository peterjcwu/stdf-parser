from stdfparser.parse import parse
from stdfparser.stdf_sub_wlan_sweep import StdfSubWlanSweep


def test_stdf_sub_wlan_sweep_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf2\sweep_with_svc.stdf"
    # stdf_path = r"C:\Users\nxf79056\Downloads\KW73P_RFn_PC1_r1_KW73P02-F0_20221021171527.stdf.gz"
    parse("redfinch", stdf_path, StdfSubWlanSweep)
