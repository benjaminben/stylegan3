import asyncio
import websockets

class WSServer:
  def __init__(self, port=65432, viz=None):
    if not viz:
      print("Missing visualizer to bind to")
      return
    print("hello viz:", viz)
    self.port = port
    self.viz = viz
  async def onMessage(self, websocket, path):
    message = await websocket.recv()
    print(f"We got the message from the client: {message}")
    await websocket.send("I can confirm I got your message!")
  def Start(self):
    start_server = websockets.serve(self.onMessage, 'localhost', self.port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()