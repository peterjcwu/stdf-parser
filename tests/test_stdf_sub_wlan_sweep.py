from stdfparser import StdfPub, DBConn, parse
from stdfparser.stdf_sub_wlan_sweep import StdfSubWlanSweep


def test_stdf_sub_wlan_sweep_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf2\sweep_with_svc.stdf.gz"
    pub = StdfPub(stdf_path)

    db_conn = DBConn("redfinch", stdf_path)
    sub = StdfSubWlanSweep(db_conn)

    parse(pub, sub)
