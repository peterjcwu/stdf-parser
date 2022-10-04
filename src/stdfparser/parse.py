import asyncio
from stdf_pub import StdfPub
from stdf_sub import StdfSub


def parse(stdf_path: str, s: StdfSub):
    p = StdfPub(stdf_path)
    p.register(s)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            p.parse(),
            s.listen(),
        ))


if __name__ == '__main__':
    from stdf_sub import StdfSub
    parse(r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf", StdfSub("StdfSub"))
