import asyncio
from stdfparser import StdfPub, StdfSub


def test_record_publisher_success():
    # stdf_path = r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf"

    p = StdfPub(stdf_path)
    s = StdfSub("base")
    p.register(s)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            p.parse(),
            s.listen(),
        ))
