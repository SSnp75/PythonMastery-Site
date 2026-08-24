---
title: Socket Programming
description: TCP/UDP from scratch, client/server patterns and low-level networking
---

# Socket Programming <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Networking · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## TCP server and client

```python
import socket

# ─── TCP Server ───────────────────────────────────
def tcp_server(host="127.0.0.1", port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(5)
        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    # Echo back uppercase
                    conn.sendall(data.upper())
                print(f"Disconnected {addr}")

# ─── TCP Client ───────────────────────────────────
def tcp_client(host="127.0.0.1", port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        client.sendall(b"Hello, Server!")
        response = client.recv(1024)
        print(f"Received: {response.decode()}")   # HELLO, SERVER!
```

---

## Multi-threaded server

```python
import socket
import threading

def handle_client(conn, addr):
    print(f"  [{addr}] Connected")
    with conn:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            conn.sendall(data)   # echo
    print(f"  [{addr}] Disconnected")

def threaded_server(host="0.0.0.0", port=9999):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(100)
        print(f"Server on {host}:{port}")

        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            thread.start()
```

---

## Async TCP server (production-grade)

```python
import asyncio

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info("peername")
    print(f"  [{addr}] Connected")

    while True:
        data = await reader.read(4096)
        if not data:
            break
        writer.write(data.upper())
        await writer.drain()

    writer.close()
    await writer.wait_closed()
    print(f"  [{addr}] Disconnected")

async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 9999)
    print(f"Serving on {server.sockets[0].getsockname()}")
    async with server:
        await server.serve_forever()

asyncio.run(main())
```

---

## UDP (connectionless)

```python
import socket

# Server
def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", 9999))
        print("UDP server listening...")
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"  From {addr}: {data.decode()}")
            sock.sendto(data.upper(), addr)

# Client
def udp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(b"Hello UDP", ("127.0.0.1", 9999))
        data, _ = sock.recvfrom(1024)
        print(f"Response: {data.decode()}")   # HELLO UDP
```

---

## Building a simple HTTP server from scratch

```python
import socket

def http_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", 8080))
        server.listen(5)
        print("HTTP server on :8080")

        while True:
            conn, addr = server.accept()
            with conn:
                request = conn.recv(4096).decode()
                method, path, _ = request.split("\r\n")[0].split(" ")
                print(f"  {method} {path}")

                # Build response
                body = f"<h1>Hello!</h1><p>You requested: {path}</p>"
                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/html\r\n"
                    f"Content-Length: {len(body)}\r\n"
                    f"\r\n"
                    f"{body}"
                )
                conn.sendall(response.encode())

# Now open http://localhost:8080/any-path in browser!
```

---

## Practice Exercises

1. **Build a chat server** — multiple clients connect, messages broadcast to all.
2. **Build a file transfer** — client sends a file over TCP, server saves it.
3. **Implement HTTP/1.1** from scratch — handle GET, POST, headers and response codes.
4. **Build a port scanner** — scan a range of ports and report which are open.
5. **Build a DNS resolver** — send UDP packets to a DNS server and parse responses.
