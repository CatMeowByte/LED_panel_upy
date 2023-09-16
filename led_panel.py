# SPDX-License-Identifier: GPL-3.0-or-later

import asyncio as aio
from machine import PWM, SoftSPI

class LEDPanel():
    def __init__(self, pa, pb, pclk, pdr, pe, plat, freq=1000, duty=10):
        # Pin
        self.pa = pa
        self.pb = pb
        self.pclk = pclk
        self.pdr = pdr
        self.pe = pe
        self.plat = plat
        
        # PWM
        self.freq = freq
        self.duty = duty
        self._pwm = PWM(pe, freq=self.freq, duty=self.duty)
        
        # SPI
        self._spi = SoftSPI(sck=self.pclk, mosi=self.pdr, miso=self.pe) # MISO is dummy
        
        # Cache
        self._cache = [bytearray(16) for k in range(4)]
    
    def _scanline(self, data):
        o = 0
        while 1:
            # Disable PWM
            self._pwm.deinit()
            self.pe(0)
            
            # Write cache
            self._spi.write(self._cache[o])
            
            # Latch
            self.plat(1)
            self.plat(0)
            
            # Row
            self.pa(o & 1)
            self.pb(o & 2)
            
            # Cache data
            for i in range(16): self._cache[o][i] = ~data[((3-i)%4)*16+o*4+(i//4)]
            
            # Reenable PWM
            self._pwm.init(freq=self.freq, duty=self.duty)
            
            o = (o+1) % 4
            
            await aio.sleep(0)

    # Execute
    def run(self, data, func):
        aio.run(aio.gather(self._scanline(data), func()))

    # Convenience without importing asyncio in main code
    def hold(self, t=0):
        return aio.sleep(t)