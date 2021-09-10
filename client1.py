from tkinter import *
import socket
import threading
import pickle
import struct
import numpy as np
import cv2 
from PIL import Image, ImageTk, ImageFile
from RTPpacket import Rtppacket
import time
import io
#build GUI
class Client:
    #statu
    #PORT = 8102
    #ADDR = "192.168.1.9"
    #PACKETADDR = 2102
    count = 0
    loss = 0
    
    def __init__(self,frame,address,initPort,packetPort,packetsize,framerate,filename):
        self.frame = frame
        self.ADDR = address
        self.PORT = int(initPort)
        self.PACKETADDR = int(packetPort)
        self.packetsize = int(packetsize)
        self.framerate = int(framerate)/1000
        self.filename = filename
        self.frame.protocol("WM_DELETE_WINDOW",self.close)
        self.status = 0
        self.STOP = 0
        self.framenumber = -1
        self.packetSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.Connection()
       
       

    def GUI(self):

        #Initialize
        self.play = Button(self.frame, text = "Replay/initialize", command = self.setup, width=20, padx=3, pady=3)
        self.play.grid(row=1, column=0, padx=1, pady=1)
        #Play
        self.play = Button(self.frame, text = "Play", command = self.Play, width=20, padx=3, pady=3)
        self.play.grid(row=1, column=1, padx=1, pady=1)
        #Pause
        self.Pause = Button(self.frame, text = "Pause", command = self.Pause, width=20, padx=3, pady=3)
        self.Pause.grid(row=1, column=2, padx=1, pady=1)
        #Stop
        self.stop = Button(self.frame, text = "Stop", command = self.Stop, width=20, padx=3, pady=3)
        self.stop.grid(row=1, column=3, padx=1, pady=1)
        #Dispaly
        self.Display = Label(self.frame, height=50,width = 200)
        self.Display.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5)

    def Initialize(self):
        try:
            #self.recve = threading.Event()
            threading.Thread(target = self.recvResponse).start()
            #self.recvResponse()
            #self.initSocket.send(b'initialize')
            self.packetSocket.bind((self.ADDR,self.PACKETADDR))
            self.status = 1
        except:
            print("failed to bind RTP Socket")
        print("In Initialize: " )
        print(self.status)

    
    def recvResponse(self):

        while True:
            try:
                message = self.initSocket.recv(1024)

                if message == b'pause':
                    self.status = 1
                    self.playthread.set()
            except:
                sys.exit(0)


    def setup(self):
        info = str(self.filename) + "\n" + str(self.packetsize) + "\n" + str(self.framerate)
            
        
        self.initSocket.send(bytes(info,"utf-8"))
    
    def Play(self):
        
        if self.status == 1 and self.STOP == 0:
            self.status = 2
            try:
                self.initSocket.send(b'play')
                self.playthread = threading.Event()
                threading.Thread(target = self.recvPacket).start()
                
                self.playthread.clear()
                #self.recvPacket()
                print("Play" )

                
            except:
                print("failed to play")

        

    def Pause(self):



        if self.status == 2 and self.STOP == 0:
            self.status = 1
            self.playthread.set()
            self.initSocket.send(b'pause')
            print("Pause")
        
    
    def Stop(self):
        #self.recve.set()
        try:
            self.playthread.set()
            
        except:
            print("Have not started playing")
        
        
        self.initSocket.send(b'end')  
        

        self.STOP = 1
        print("Forced ending video")

    def recvPacket(self):
        code2 = b'stop'
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        #print("enter")
        while True:
            try:
                if self.STOP == 1:
                    try:
                        
                        self.packetSocket.close()
                        print("UDP socket closed")
                    except:
                        print("UDP socket is not opened")
                    break

                chunks = bytearray()
                STOP = False
                
                while STOP == False:
                
                    chunk,_ = self.packetSocket.recvfrom(self.packetsize)

                    if chunk.startswith(code2):
                        STOP = True
                    elif chunk:
                    
                        chunks.extend(chunk)
                
                byte_frame = chunks
                
                if byte_frame == b'finish':
                    self.STOP = 1
                    print("finish")
                    print("---------result---------")
                    print(str(self.loss / self.count * 100) + "%")
                    try:
                        self.packetSocket.shutdown(socket.SHUT_RDWR)
                        self.packetSocket.close()
                        print("UDP socket closed")
                    except:
                        print("UDP socket is not opened")
                    try:
                        self.playthread.set()
                    except:
                        print("Have not started playing")
                    break
                
                if self.playthread.isSet():
                    break
                
                #print(frame)
                #cv2.imshow('frame',frame)
                if byte_frame:
                    packet = Rtppacket()
                    packet.decode(byte_frame)
                    
                    if self.framenumber + 1 != packet.get_seqNum():
                        print("try to play",self.framenumber+1)
                        print("receive" , packet.get_seqNum())
                        print("Packet Loss")
                        self.loss += 1
                    if packet.get_seqNum() > self.framenumber:
                        
                        """
                        f4 = open("frame3.jpg","wb")
                        self.count += 1
                        print(self.count)
                        f4.write(packet.get_payload())
                        f4.close()

                        photo = ImageTk.PhotoImage(Image.open("frame3.jpg"))
                        """
                        try:
                            self.framenumber = packet.get_seqNum()
                            photo = ImageTk.PhotoImage(Image.open(io.BytesIO(packet.get_payload())))
                            self.Display.configure(image = photo,height = 720, width = 1280)
                            self.Display.image = photo
                        except:
                            print("failed to print Image")
                        #print("play successfully")
                        #print("----------")
                    
                    self.count += 1
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            except:
                if self.playthread.isSet():
                    break
        print(5)  

    def Connection(self):
        self.initSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #RTSP socket
            self.initSocket.connect((self.ADDR, self.PORT))
            #bind RTP socket for reciving packets
            
        except:
            print("Connection falied")
        
        threading.Thread(target = self.Initialize).start()

    def close(self):
        
        try:
            self.initSocket.send(b'close')
            
        except:
            print("failed to ask server to close")
        try:    
            self.initSocket.shutdown(socket.SHUT_RDWR)
            self.initSocket.close()
        except:
            print("failed to close TCP socket")
        try:
            self.playthread.set()
            
        except:
            print("Have not started playing")
        self.STOP = 1
        #self.Stop()
        self.frame.destroy()
        sys.exit()
"""
    def listen(self):
        while True:
            try:

"""
    #def Connection2(self):

'''
    "Send operation request to server"
    def sendOperation(self, operation):
        #Initialize
        if operation == self.INIT and self.status = self.INIT:

'''

    
        

#_main_

frame = Tk()
address = sys.argv[1]
initPort = sys.argv[2]
packetPort = sys.argv[3]
packetsize = sys.argv[4]
framerate = sys.argv[5]
filename = sys.argv[6]

Client(frame,address,initPort,packetPort,packetsize,framerate,filename).GUI()
frame.mainloop()