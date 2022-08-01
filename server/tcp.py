import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)

class TCPServer:
  def __init__(self, port=65432, viz=None):
    if not viz:
      print("Missing visualizer to bind to")
      return
    print("hello viz:", viz)
    self.port = port
    self.viz = viz
  def Start(self):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.bind((HOST, self.port))
      s.listen()
      conn, addr = s.accept()
      with conn:
        print(f"Connected by {addr}")
        while True:
          data = conn.recv(1024)
          if not data:
            break
          conn.sendall(data)