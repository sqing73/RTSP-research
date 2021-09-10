import sys
from time import time
#packet header size(12 * 8 = 96 bytes in total)
HEADER = 12

class Rtppacket:
    def __init__(self):
        self.h = bytearray(HEADER)
    def encode(self, version, p, x, cc, m, pt, seqNum, ssrc, payload):
        t = int(time())
        
        #version 0-1
        self.h[0] = version << 6
        #p 2
        self.h[0] = self.h[0] | p << 5
        #x 3
        self.h[0] = self.h[0] | x << 4
        #cc 4-7
        self.h[0] = self.h[0] | cc
        #m 8
        self.h[1] = m << 7
        #pt 9-15
        self.h[1] = self.h[1] | pt
        #seqNum 16-23-
        self.h[2] = seqNum >> 8
        #seqNum 24-31
        if(seqNum>>8 > 0):
            self.h[3] = seqNum - (seqNum>>8)*256
        else:
            self.h[3] = seqNum
        #timestamp 32-39
        self.h[4] = (t >> 24) & 0xff
        #timestamp 40-47
        self.h[5] = (t >> 16) & 0xff
        #timestamp 48-55
        self.h[6] = (t >> 8) & 0xff
        #timestamp 56-63
        self.h[7] = t & 0xff
        #ssrc 64-95
        self.h[8] = ssrc >> 24
        self.h[9] = ssrc >> 16
        self.h[10] = ssrc >> 8
        self.h[11] = ssrc

        self.payload = payload

    def decode(self, packet):
        self.h = bytearray(packet[0:HEADER])
        self.payload = packet[HEADER:]

    def get_version(self):
        return int(self.h[0]>>6)

    def get_seqNum(self):
        return int(self.h[2]<<8 | self.h[3])

    def get_timestamp(self):
        return int(self.h[4]<<24 | self.h[5]<<16 | self.h[6]<<8 | self.h[7])

    def get_PT(self):
        return int(self.h[1]&127)

    def get_payload(self):
        return self.payload

    def get_packet(self):
        return self.h + self.payload





