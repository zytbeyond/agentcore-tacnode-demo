# 🔍 **PROTOCOL MISMATCH EXPLANATION**

## 📋 **THE THREE DIFFERENT PROTOCOLS:**

### **1. REST API (Representational State Transfer)**
REST is an architectural style for web services using standard HTTP methods.

**REST Example:**
```http
POST /api/query HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer token123

{
  "sql": "SELECT * FROM users WHERE active = true"
}
```

**REST Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {"id": 1, "name": "John", "active": true},
  {"id": 2, "name": "Jane", "active": true}
]
```

**REST Characteristics:**
- ✅ Uses HTTP methods (GET, POST, PUT, DELETE)
- ✅ Resource-based URLs (/users, /orders, /query)
- ✅ HTTP status codes (200, 404, 500)
- ✅ Stateless
- ✅ Standard web protocol

---

### **2. JSON-RPC 2.0 (Remote Procedure Call)**
JSON-RPC is a protocol for calling remote functions using JSON.

**JSON-RPC Example:**
```http
POST /mcp HTTP/1.1
Host: mcp-server.tacnode.io
Content-Type: application/json
Authorization: Bearer token123

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "query",
    "arguments": {
      "sql": "SELECT * FROM users WHERE active = true"
    }
  }
}
```

**JSON-RPC Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "[{\"id\": 1, \"name\": \"John\"}, {\"id\": 2, \"name\": \"Jane\"}]"
      }
    ],
    "isError": false
  }
}
```

**JSON-RPC Characteristics:**
- ✅ Function/method-based (not resource-based)
- ✅ Always POST requests
- ✅ Structured request/response format
- ✅ Built-in error handling
- ✅ Can batch multiple calls

---

### **3. OpenAPI (formerly Swagger)**
OpenAPI is a specification format for describing REST APIs.

**OpenAPI Example:**
```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /query:
    post:
      summary: Execute SQL Query
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                sql:
                  type: string
              required:
                - sql
      responses:
        '200':
          description: Query results
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
```

**OpenAPI Characteristics:**
- ✅ Documentation format for REST APIs
- ✅ Describes endpoints, parameters, responses
- ✅ Used by tools to generate code/docs
- ✅ Standard for API documentation

---

## 🌐 **WHAT AGENTCORE GATEWAY SUPPORTS:**

### **✅ AgentCore Gateway Capabilities:**
1. **MCP Targets with OpenAPI Schema**
2. **MCP Targets with Smithy Models**
3. **MCP Targets with Lambda Functions**

### **🔍 How AgentCore Gateway Works:**
```
1. User sends MCP call to Gateway
2. Gateway looks up target configuration
3. Gateway translates MCP call to target's expected format
4. Gateway makes HTTP call to target
5. Gateway translates response back to MCP format
```

### **📋 AgentCore Gateway Target Types:**
```json
{
  "mcp": {
    "openApiSchema": {...},     // For REST APIs
    "smithyModel": {...},       // For AWS services
    "lambda": {...}             // For Lambda functions
  }
}
```

### **🎯 What AgentCore Gateway Expects from Targets:**
- **REST endpoints** (when using OpenAPI schema)
- **Standard HTTP responses** (JSON data)
- **HTTP status codes** (200, 400, 500)
- **Not JSON-RPC protocol**

---

## 🌐 **WHAT TACNODE SUPPORTS:**

### **✅ TACNode Capabilities:**
1. **JSON-RPC 2.0 API** at `https://mcp-server.tacnode.io/mcp`
2. **MCP Protocol** (which uses JSON-RPC 2.0)

### **🔍 How TACNode Works:**
```
1. Client sends JSON-RPC 2.0 request to /mcp endpoint
2. TACNode parses JSON-RPC request
3. TACNode executes the requested method
4. TACNode returns JSON-RPC 2.0 response
```

### **📋 TACNode API Format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "query",
    "arguments": {
      "sql": "SELECT * FROM test"
    }
  }
}
```

### **🎯 What TACNode Expects:**
- **JSON-RPC 2.0 format** (not REST)
- **Specific method names** (tools/call)
- **Structured parameters** (name, arguments)
- **Not REST endpoints**

---

## 🚨 **THE FUNDAMENTAL MISMATCH:**

### **🔍 The Problem:**
```
AgentCore Gateway (OpenAPI) → Expects REST API
TACNode → Provides JSON-RPC 2.0 API
```

### **📋 Detailed Mismatch:**

#### **What AgentCore Gateway Sends (REST):**
```http
POST /query HTTP/1.1
Content-Type: application/json

{
  "sql": "SELECT * FROM test"
}
```

#### **What TACNode Expects (JSON-RPC):**
```http
POST /mcp HTTP/1.1
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "query",
    "arguments": {
      "sql": "SELECT * FROM test"
    }
  }
}
```

### **🎯 The Mismatch Points:**
1. **Endpoint**: Gateway calls `/query`, TACNode expects `/mcp`
2. **Format**: Gateway sends `{"sql": "..."}`, TACNode expects JSON-RPC wrapper
3. **Protocol**: Gateway uses REST semantics, TACNode uses RPC semantics
4. **Response**: Gateway expects direct JSON, TACNode returns JSON-RPC response

---

## 💡 **WHY THE MISMATCH EXISTS:**

### **🔍 Different Design Philosophies:**

#### **REST (Resource-Oriented):**
- "Get me the user with ID 123" → `GET /users/123`
- "Create a new order" → `POST /orders`
- "Execute a query" → `POST /query`

#### **JSON-RPC (Function-Oriented):**
- "Call the getUser function with ID 123" → `{"method": "getUser", "params": {"id": 123}}`
- "Call the createOrder function" → `{"method": "createOrder", "params": {...}}`
- "Call the query tool" → `{"method": "tools/call", "params": {"name": "query", ...}}`

---

## 🔧 **POSSIBLE SOLUTIONS:**

### **1. ✅ Lambda Proxy (WORKING):**
```
User → MCP → AgentCore Gateway → Lambda → TACNode JSON-RPC
```
Lambda translates REST to JSON-RPC:
```python
def lambda_handler(event, context):
    # Convert REST request to JSON-RPC
    rest_request = event['body']
    jsonrpc_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "query",
            "arguments": rest_request
        }
    }
    # Call TACNode...
```

### **2. ❌ TACNode REST API (DOESN'T EXIST):**
```
User → MCP → AgentCore Gateway → TACNode REST API
```
Would need TACNode to provide:
```http
POST /query
{
  "sql": "SELECT * FROM test"
}
```

### **3. ❌ AgentCore JSON-RPC Support (DOESN'T EXIST):**
```
User → MCP → AgentCore Gateway → TACNode JSON-RPC
```
Would need AgentCore Gateway to support JSON-RPC targets directly.

---

## 🎯 **SUMMARY:**

### **The Core Issue:**
- **AgentCore Gateway** speaks "REST language" 🗣️
- **TACNode** speaks "JSON-RPC language" 🗣️
- They need a **translator** (Lambda) to communicate 🔄

### **Why My "Direct" Solution Was Simulated:**
I created an OpenAPI spec that **describes** JSON-RPC format, but AgentCore Gateway doesn't know how to **speak** JSON-RPC - it only knows how to make REST calls.

### **The Real Working Solution:**
Use Lambda as a protocol translator - it's the only way to bridge the REST ↔ JSON-RPC gap with current technology.
