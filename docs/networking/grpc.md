---
title: gRPC & Protocol Buffers
description: High-performance RPC with protobuf, streaming and service definitions
---

# gRPC & Protocol Buffers <span class="pm-badge pm-badge-proficient">Proficient</span>

<div class="pm-topic-header">
  <strong>🌐 Networking · Level 4</strong>
  <div class="pm-topic-meta">
    <span>⏱️ ~4 days</span>
  </div>
</div>

---

## What is gRPC?

gRPC is a high-performance RPC framework using Protocol Buffers for serialization — 10x faster than JSON REST for inter-service communication.

---

## Define service with .proto

```protobuf
// user_service.proto
syntax = "proto3";

package userservice;

service UserService {
    rpc GetUser (GetUserRequest) returns (User);
    rpc ListUsers (ListUsersRequest) returns (stream User);  // server streaming
    rpc CreateUser (User) returns (User);
}

message User {
    int32 id = 1;
    string name = 2;
    string email = 3;
    int32 age = 4;
}

message GetUserRequest {
    int32 id = 1;
}

message ListUsersRequest {
    int32 page_size = 1;
}
```

```bash
# Generate Python code
pip install grpcio grpcio-tools
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user_service.proto
```

---

## Server implementation

```python
import grpc
from concurrent import futures
import user_service_pb2 as pb2
import user_service_pb2_grpc as pb2_grpc

class UserServicer(pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.users = {
            1: pb2.User(id=1, name="Alice", email="alice@example.com", age=30),
            2: pb2.User(id=2, name="Bob", email="bob@example.com", age=25),
        }

    def GetUser(self, request, context):
        user = self.users.get(request.id)
        if not user:
            context.abort(grpc.StatusCode.NOT_FOUND, f"User {request.id} not found")
        return user

    def ListUsers(self, request, context):
        """Server streaming — yields users one by one."""
        for user in self.users.values():
            yield user

    def CreateUser(self, request, context):
        new_id = max(self.users.keys()) + 1
        user = pb2.User(id=new_id, name=request.name, email=request.email, age=request.age)
        self.users[new_id] = user
        return user

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server on :50051")
    server.wait_for_termination()

serve()
```

---

## Client

```python
import grpc
import user_service_pb2 as pb2
import user_service_pb2_grpc as pb2_grpc

channel = grpc.insecure_channel("localhost:50051")
stub = pb2_grpc.UserServiceStub(channel)

# Unary call
user = stub.GetUser(pb2.GetUserRequest(id=1))
print(f"Got: {user.name} ({user.email})")   # Alice (alice@example.com)

# Server streaming
for user in stub.ListUsers(pb2.ListUsersRequest(page_size=10)):
    print(f"  {user.id}: {user.name}")

# Create
new_user = stub.CreateUser(pb2.User(name="Charlie", email="c@d.com", age=35))
print(f"Created: {new_user.id}")
```

---

## Practice Exercises

1. **Define a proto** for an order service with CRUD operations.
2. **Implement server streaming** — stream real-time price updates to clients.
3. **Add error handling** — return proper gRPC status codes for validation errors.
4. **Benchmark** gRPC vs REST for 1000 requests — compare latency and throughput.
5. **Add authentication** with gRPC interceptors (like middleware).
