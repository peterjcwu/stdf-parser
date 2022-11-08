import asyncio
from typing import Set, Optional


class Subscriber:
    def __init__(self, _id: str = ""):
        self._id: str = _id
        self.queue = asyncio.Queue()

    async def listen(self):
        while True:
            msg = await self.queue.get()
            if msg is None:
                break
            self._process(msg)
        self.on_listen_end()

    def _process(self, msg):
        print(f"{self._id} is processing {msg}")

    def on_listen_end(self):
        print(f"{self._id} ends listening...")


class Publisher:
    def __init__(self):
        self.subscribers: Set[Subscriber] = set()

    def register(self, who: Subscriber):
        self.subscribers.add(who)

    def unregister(self, who: Subscriber):
        self.subscribers.discard(who)

    async def dispatch(self, msg: Optional[tuple]):
        for subscriber in self.subscribers:
            subscriber.queue.put_nowait(msg)


if __name__ == '__main__':
    p = Publisher()
    s = Subscriber("a")
    p.register(s)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        asyncio.gather(
            s.listen(),
            p.dispatch((1, 2)),
            p.dispatch((3, 4)),
            p.dispatch(None)
        ))
