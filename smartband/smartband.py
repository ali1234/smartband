import asyncio, concurrent, abc, struct

import logging
logger = logging.getLogger(__name__)

from bluepy import btle

class SmartBand(object):
    def __init__(self, deviceAddress, addrType, cmdResponseHandle, loop=None):
        btle.DefaultDelegate.__init__(self)

        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

        self.cmdResponseHandle = cmdResponseHandle

        self.futures = {}

        self.task = self.loop.create_task(self.waitForNotifications())

        self.peripheral = btle.Peripheral(deviceAddress, addrType)
        self.peripheral.setDelegate(self)
        self.peripheral.writeCharacteristic(self.cmdResponseHandle, struct.pack('<BB', 0x01, 0x00), withResponse=True)

    async def waitForNotifications(self):
        try:
            while True:
                self.peripheral.waitForNotifications(0.1)
                await asyncio.sleep(0.1)
        except concurrent.futures.CancelledError:
            pass

    @abc.abstractmethod
    def handleNotification(self, cHandle, data):
        pass

    def cmd(self, cmd, responseCode, timeout=5.0):
        self.futures[responseCode] = self.loop.create_future()
        self.peripheral.writeCharacteristic(0x19, cmd, withResponse=True)
        response = self.loop.run_until_complete(asyncio.wait_for(self.futures[responseCode], timeout))
        del self.futures[responseCode]
        return response

    def disconnect(self):
        self.peripheral.disconnect()
        self.task.cancel()
        self.loop.run_until_complete(self.task)
