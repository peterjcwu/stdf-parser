import asyncio
from stdf_pub import StdfPub


def parse(stdf_path: str, sub_class, sub_class_args: tuple):
    p = StdfPub(stdf_path)
    s = sub_class(*sub_class_args)
    p.register(s)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            p.parse(),
            s.listen(),
        ))


if __name__ == '__main__':
    from stdf_sub import StdfSub
    parse(r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf", StdfSub, ("StdfSub",))
