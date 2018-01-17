import struct
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from bluepy import btle

from smartband.smartband import SmartBand

class Nordic(SmartBand):
    def __init__(self, deviceAddress, loop=None):
        super().__init__(deviceAddress, btle.ADDR_TYPE_RANDOM, 0x1c, loop)

    def cmd(self, cmd, timeout=5.0):
        logger.debug('-> {}'.format(' '.join('{:02x}'.format(d) for d in cmd)))
        return super().cmd(cmd, cmd[0]|0x80, timeout)

    def handleNotification(self, cHandle, data):
        logger.debug('<- {}'.format(' '.join('{:02x}'.format(d) for d in data)))
        if cHandle == 0x1b:
            if data[0] in self.futures:
                self.futures[data[0]].set_result(data)

    def get_time(self):
        data = self.cmd(struct.pack('<B19x', 0x05))
        return datetime((data[1]*100)+data[2], data[3], data[4], data[5], data[6], data[7])

    def set_time(self, dt):
        result = self.cmd(struct.pack('<8B12x', 0x01, dt.year//100, dt.year%100, dt.month, dt.day, dt.hour, dt.minute, dt.second))
        return result[1] == 0

    def get_addr(self):
        return self.cmd(struct.pack('<B19x', 0x08))[1:7]

    def alert(self, icon=0, msg=''):
        # icon: 0 = none, 1 = ringing phone, 2 = email, 3 = penguin, 4 = phone, 5 = phone
        if icon == 2:
            result = self.cmd(struct.pack('<B19x', 0x21))
        else:
            result = self.cmd(struct.pack('<B19x', 0x20))
        return result[1] == 0

if __name__=='__main__':
    q = Nordic('C9:78:AA:0D:3F:87')

    print('BLE address:', '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(*q.get_addr()))
    #print('Old Time:', q.get_time())
    #print('Set time:', q.set_time(datetime.now()))
    #print('New time:', q.get_time())

    q.alert()

    # Must manually disconnect or you won't be able to reconnect.
    q.disconnect()