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
        data, addr = self.sock.recvfrom(1024*48) # buffer size is 1024 bytes
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

TCP_IP = "127.0.0.1"
TCP_PORT = 5006

class TCPServer:
  def __init__(self, viz):
    self.sock = socket.socket(socket.AF_INET, # Internet
                          socket.SOCK_STREAM) # TCP
    self.sock.setblocking(False)
    self.sock.bind((TCP_IP, TCP_PORT))
    # self.reader = codecs.getreader('utf-8')
    self.sock.listen()
    self.conn, self.addr = self.sock.accept()
  def Receive(self):
    try:
      with self.conn:
        print("connected by", addr)
        while True:
          data, addr = self.sock.recv(1024) # buffer size is 1024 bytes
          if not data:
            break
          com = json.loads(data.decode('utf-8'))
          print(com)
          # if com['type'] == "loadPickle":
          #   self.viz.load_pickle(com['data']['pkl'])
          # elif com['type'] == "update": 
          #   self.viz.args.update(**com['data'])
    except BlockingIOError as e:
      pass
    except Exception as e:
      print(f"{e.__class__.__name__}: {e}")
      pass