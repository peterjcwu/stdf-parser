from stdfparser import StdfPub, DBConn, parse
from stdfparser.stdf_sub_embedded_doc import StdfSubEmbeddedDoc


def test_stdf_sub_wlan_sweep_success():
    stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf2\sweep_with_svc.stdf.gz"
    pub = StdfPub(stdf_path)

    db_conn = DBConn("embedded")
    sub = StdfSubEmbeddedDoc(db_conn, stdf_path)

    parse(pub, sub)
