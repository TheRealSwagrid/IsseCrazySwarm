#!/usr/bin/env python
import signal
import sys
from time import sleep

from AbstractVirtualCapability import AbstractVirtualCapability, VirtualCapabilityServer, formatPrint


class IsseCrazySwarm(AbstractVirtualCapability):
    def __init__(self, server):
        super().__init__(server)

    def loop(self):
        sleep(.0001)


if __name__ == "__main__":
    try:
        port = None
        if len(sys.argv[1:]) > 0:
            port = int(sys.argv[1])
        server = VirtualCapabilityServer(port)
        cf = IsseCrazySwarm(server)
        cf.start()

        def signal_handler(sig, frame):
            cf.kill()
            server.kill()
        signal.signal(signal.SIGINT, signal_handler)
        cf.join()
        server.join()
        signal.pause()

        # Needed for properly closing, when program is being stopped with a Keyboard Interrupt
    except KeyboardInterrupt:
        print("[Main] Received KeyboardInterrupt")
