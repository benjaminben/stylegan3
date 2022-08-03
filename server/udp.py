import socket
import json
import codecs

UDP_IP = "127.0.0.1"
UDP_PORT = 5005

class UDPServer:
  def __init__(self, viz):
    self.sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_DGRAM) # UDP
    self.sock.setblocking(False)
    self.sock.bind((UDP_IP, UDP_PORT))
    # self.reader = codecs.getreader('utf-8')

    self.viz = viz
  def Receive(self):
    try:
      while True:
        data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
        # print(data)
        # dec = self.reader(data)
        # print(dec)
        com = json.loads(data.decode('utf-8'))
        if com['type'] == "loadPickle":
          self.viz.load_pickle(com['data']['pkl'])
        elif com['type'] == "update": 
          self.viz.args.update(**com['data'])
    except BlockingIOError as e:
      pass
    except Exception as e:
      print(f"{e.__class__.__name__}: {e}")
      pass

class TCPServer:
  def __init__(self, viz):
    self.sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_STREAM) # UDP
    self.sock.setblocking(False)
    self.sock.bind((UDP_IP, UDP_PORT))
    self.reader = codecs.getreader('utf-8')
  def Receive(self):
    try:
      self.sock.listen()
      conn, addr = self.sock.accept()
      with conn:
        while True:
          data, addr = self.sock.recvfrom(1024) # buffer size is 1024 bytes
          print(data)
          dec = self.reader(data)
          print(dec)
          com = json.load(dec)
          print("received com: %s" % com)
    except BlockingIOError as e:
      pass
    # except Exception as e:
    #   print(f"{e.__class__.__name__}: {e}")
    #   pass