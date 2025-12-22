import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = s.connect_ex(("192.168.2.59", 5432))
if result == 0:
    print("✅ Port 5432 is reachable")
else:
    print(f"❌ Port 5432 is NOT reachable (error code: {result})")
s.close()
