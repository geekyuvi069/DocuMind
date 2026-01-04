# API Usage Examples

## Authentication

### 1. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Get Current User
```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "username": "admin",
  "email": "admin@docflow.com",
  "is_active": true
}
```

## Documents

### 1. Upload PDF Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@/path/to/invoice.pdf"
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "filename": "invoice.pdf",
  "document_type": "invoice",
  "extracted_fields": {
    "invoice_no": "INV-2024-001",
    "vendor": "ABC Corporation",
    "amount": 1500.00,
    "due_date": "2024-12-31",
    "date": "2024-11-01",
    "currency": "USD"
  },
  "uploaded_by": "admin",
  "uploaded_at": "2024-01-15T10:30:00",
  "status": "processed"
}
```

### 2. List All Documents
```bash
curl -X GET "http://localhost:8000/documents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Filter Documents by Type
```bash
curl -X GET "http://localhost:8000/documents?type=invoice" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Filter Resumes by Skill
```bash
curl -X GET "http://localhost:8000/documents?skill=Python" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 5. Get Specific Document
```bash
curl -X GET "http://localhost:8000/documents/507f1f77bcf86cd799439011" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Tasks

### 1. List All Tasks
```bash
curl -X GET "http://localhost:8000/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
[
  {
    "id": "507f1f77bcf86cd799439012",
    "document_id": "507f1f77bcf86cd799439011",
    "task_type": "verify_invoice",
    "status": "pending",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "assigned_to": null,
    "metadata": {}
  }
]
```

### 2. Filter Tasks by Status
```bash
curl -X GET "http://localhost:8000/tasks?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Filter Tasks by Type
```bash
curl -X GET "http://localhost:8000/tasks?task_type=verify_invoice" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Get Specific Task
```bash
curl -X GET "http://localhost:8000/tasks/507f1f77bcf86cd799439012" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Python Requests Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Upload Document
with open("invoice.pdf", "rb") as f:
    upload_response = requests.post(
        f"{BASE_URL}/documents/upload",
        headers=headers,
        files={"file": f}
    )
document = upload_response.json()
print(f"Document ID: {document['id']}")
print(f"Type: {document['document_type']}")
print(f"Extracted Fields: {document['extracted_fields']}")

# 3. List Documents
documents_response = requests.get(
    f"{BASE_URL}/documents?type=invoice",
    headers=headers
)
documents = documents_response.json()
print(f"Found {len(documents)} invoices")

# 4. List Tasks
tasks_response = requests.get(
    f"{BASE_URL}/tasks?status=pending",
    headers=headers
)
tasks = tasks_response.json()
print(f"Found {len(tasks)} pending tasks")
```

## JavaScript/Fetch Example

```javascript
const BASE_URL = 'http://localhost:8000';

// 1. Login
async function login() {
  const formData = new FormData();
  formData.append('username', 'admin');
  formData.append('password', 'admin123');
  
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.access_token;
}

// 2. Upload Document
async function uploadDocument(token, file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  return await response.json();
}

// Usage
const token = await login();
const fileInput = document.querySelector('input[type="file"]');
const document = await uploadDocument(token, fileInput.files[0]);
console.log(document);
```

## Postman Collection

You can import these endpoints into Postman:

1. Create a new collection: "DocFlow Intelligence API"
2. Set collection variable: `base_url` = `http://localhost:8000`
3. Set collection variable: `token` = (will be set after login)
4. Add Pre-request Script to auth endpoints to set token:
   ```javascript
   pm.environment.set("token", pm.response.json().access_token);
   ```
5. Use `{{base_url}}` and `{{token}}` in requests

## Common Error Responses

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Document not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Only PDF files are allowed"
}
```

