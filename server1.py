import socket
import time
import sys
import threading
import cv2
import numpy as np
import pickle
import struct
import random, math
import time
from RTPpacket import Rtppacket

class Server:

    #ADDR = "192.168.1.9"
    #PACKETPORT = 2102
    count = 0
    status = 0
    framenumber = 1
    #packetsize = 512
    #framerate = 35
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
    def __init__(self,initsocket,address,packetPort):
        self.ADDR = address
        self.initsocket = initsocket
        self.PACKETPORT = packetPort
        #self.packetsize = packetsize
        #self.framerate = framerate /1000
        #print(self.framerate)
        """
        self.file =cv2.VideoCapture("trailer.mp4")
        self.file.set(3,1280)
        self.file.set(4,720)
        self.status = 1
        """
        self.END = 0
    def start(self):
        #threading.Thread(target = self.listen).start()
        self.listen()
        
    def listen(self):
        connectSocket = self.initsocket
        while True:
            message = connectSocket[0].recv(256)
            if message:
                self.messageOption(message)

    def messageOption(self,message):

        

        if message == b'play' and self.END == 0:
            print("play")
            self.packetsocket= socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            self.status = 2
            self.playthread = threading.Event()
            threading.Thread(target=self.sendPacket).start()
            #self.sendPacket()
            
        elif message == b'pause' and self.END == 0:
            print("pause")
            if self.status == 2:
                self.status = 1
                self.playthread.set()
                code2 = ('stop').encode('utf-8')
                self.packetsocket.sendto(code2,(self.ADDR,self.PACKETPORT))
        
        elif message == b'end' and self.END == 0:
            self.END = 1
            try:

                self.playthread.set()
                print("Transmitting ended")
            except:
                print("Have not started transmiting")

        elif message == b'close':
            self.EXIT()
        
        else:
            print("enter")
            info = message.decode("utf-8")
            info = info.split('\n')
            self.filename = info[0]
            print(self.filename)
            self.packetsize = int(info[1])
            print(self.packetsize)
            self.framerate = float(info[2])
            print(self.framerate)
            self.file = cv2.VideoCapture(self.filename)
            self.file.set(3,1280)
            self.file.set(4,720)
            self.status = 1


    def EXIT(self):
        try:
            self.playthread.set()
            print("Transmitting ended")
        except:
            print("Have not started transmiting")

        

        print("System closed")
        sys.exit()             
    
    def sendPacket(self):

        code2 = ('stop').encode('utf-8')
        self.framenumber -= 1
        while self.file.isOpened():
            version = 2
            padding = 0
            extension = 0
            cc = 0
            marker = 0
            pt = 26
            seq = self.framenumber
            ssrc = 0
            
            if self.playthread.isSet():
                break
            
            
            #self.file.set(cv2.CAP_PROP_POS_FRAMES,self.framenumber)
            
            #jit = math.floor(random.uniform(-13,5.99))
            #jit = jit/1000
            #self.playthread.wait(0.05+jit)
            #jit = jit +0.035
            #jit = 0.04
            #print(jit)
            ret,frame = self.file.read()
            
            
            if ret:
                cv2.imwrite("frame2.jpg",frame)
                #cv2.imshow("frame",frame)
                if cv2.waitKey(100) & 0xFF == ord('q'):
                    break
                f3 = open("frame2.jpg",'rb')
                self.count += 1
                #print(self.framenumber)
                data1 = f3.read()
                f3.close()
                packet = Rtppacket()
                #print(seq>>8)
                packet.encode(version,padding,extension,cc,marker,pt,seq,ssrc,data1)
                data1 = packet.get_packet()
                for i in range(0,len(data1),self.packetsize):
                    
                    if self.playthread.isSet():
                        break
                    
                    if i+self.packetsize > len(data1):
                        self.packetsocket.sendto(data1[i:len(data1)],(self.ADDR,self.PACKETPORT))
                    else:
                        self.packetsocket.sendto(data1[i:i+self.packetsize],(self.ADDR,self.PACKETPORT))
                self.packetsocket.sendto(code2,(self.ADDR,self.PACKETPORT))
                self.framenumber += 1
                time.sleep(self.framerate)
            else:
                code_finish = b'finish'
                print("finish")
                self.packetsocket.sendto(code_finish,(self.ADDR,self.PACKETPORT))
                self.packetsocket.sendto(code2,(self.ADDR,self.PACKETPORT))
                break






initSocket = socket.socket()          
print ("Socket successfully created")
  
packetPort = int(sys.argv[2])
port = int(sys.argv[1])

#packetsize = int(sys.argv[3])
#framerate = int(sys.argv[4])
initSocket.bind(('', port))         
print ("socket binded to %s" %(port))
  

initSocket.listen(5)      
print ("socket is listening")            
  

 
while True: 
    clients = {}
    initsocket= initSocket.accept()
    print ('Got connection from',  initsocket[1])
    addr,port = initsocket[1]
    Server(initsocket,addr,packetPort).start()      
   
    
