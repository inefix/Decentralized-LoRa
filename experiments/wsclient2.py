from websocket import create_connection
ws = create_connection("ws://163.172.130.246:8765")
print("Sending 'Hello, World'...")
ws.send("Hello, World")
print("Sent")
print("Receiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()