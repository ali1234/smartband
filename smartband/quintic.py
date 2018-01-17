import struct
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from bluepy import btle

from smartband.smartband import SmartBand

class Quintic(SmartBand):
    def __init__(self, deviceAddress, loop=None):
        super().__init__(deviceAddress, btle.ADDR_TYPE_PUBLIC, 0x1d, loop)

    def cmd(self, cmd, timeout=5.0):
        logger.debug('-> {}'.format(' '.join('{:02x}'.format(d) for d in cmd)))
        return super().cmd(cmd, cmd[1], timeout)

    def handleNotification(self, cHandle, data):
        logger.debug('<- {}'.format(' '.join('{:02x}'.format(d) for d in data)))
        if cHandle == 0x1c:
            if data[0] == 0x5b and data[1] in self.futures:
                self.futures[data[1]].set_result(data)

    def set_time(self, dt, antilost=False, metric=True):
        result = self.cmd(struct.pack('<BBBBBBBBBBBBBBBBBBBB',  0x5a, 0x01,
                            dt.year % 100, dt.year / 100, dt.month, dt.day,
                              dt.hour, dt.minute, dt.second,
                              0x00, 0x64, # target steps / 100, hi then lo
                              0x00, # wear position
                              0x01, # motion mode
                              0x00, # sex
                              0x00, 0x02, # fixed
                              0xa4, # "i"
                              0x46, # weight
                              0xb7, # height
                              0x80 | (0x40 if metric else 0x00) | (0x20 if antilost else 0x00)
                                    # options:
                                    # 0x01 - always off?
                                    # 0x02 - always off?
                                    # 0x04 - always off?
                                    # 0x08 - always off?
                                    # 0x10 - always off?
                                    # 0x20 - anti-lost
                                    # 0x40 - 1: metric, 0: imperial
                                    # 0x80 - always on?
                             ))
        return True

    def get_addr(self):
        return self.cmd(struct.pack('<BB18x', 0x5a, 0x10))[7:13]

    def alert(self, icon=0, msg=b''):
        # icon: 0 = none, 1 = ringing phone, 2 = email, 3 = penguin, 4 = phone, 5 = phone
        self.cmd(struct.pack('<BBBBB15s', 0x5a, 0x15, 0x00, icon, min(len(msg), 15), msg))

if __name__=='__main__':
    q = Quintic('08:7C:BE:8F:3C:FB')

    print('BLE address:', '{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}'.format(*q.get_addr()))
    #print('Old Time:', q.get_time())
    #print('Set time:', q.set_time(datetime.now()))
    #print('New time:', q.get_time())

    q.alert(3)

    # Must manually disconnect or you won't be able to reconnect.
    q.disconnect()