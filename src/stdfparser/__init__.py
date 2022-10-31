from .stdf_pub import StdfPub
from .stdf_sub import StdfSub
from .db import DBConn
from .stdf_sub_wlan_sweep import StdfSubWlanSweep
import asyncio

# nest asyncio for jupyter
import nest_asyncio
nest_asyncio.apply()


def parse(pub: StdfPub, sub: StdfSub):
    pub.register(sub)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            pub.parse(),
            sub.listen(),
        ))


if __name__ == '__main__':
    p = StdfPub(r"C:\log\w224_wlan_sweep\wlan_sweep\stdf\sweep.stdf")
    s = StdfSub("")
    parse(p, s)
