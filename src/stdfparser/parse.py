import os
import asyncio
from stdfparser import StdfPub


def parse(project_name: str, stdf_path: str, stdf_sub_class):
    p = StdfPub(stdf_path)
    s = stdf_sub_class(project_name, os.path.basename(stdf_path).split(".")[0])
    p.register(s)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            p.parse(),
            s.listen(),
        ))


if __name__ == '__main__':
    from stdf_sub import StdfSub
    parse("test", r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf", StdfSub)
