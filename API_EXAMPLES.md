"""API Usage Examples

This document shows real-world examples of using the Retail Intelligence AI V2 API.

## Authentication

### 1. Register a New Account

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acmecorp.com",
    "password": "SecurePassword123!",
    "full_name": "John Smith",
    "organization_name": "Acme Retail Corp"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@acmecorp.com",
    "password": "SecurePassword123!"
  }'
```

### 3. Get Current User

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
{
  "id": "user_123",
  "email": "john@acmecorp.com",
  "full_name": "John Smith",
  "role": "owner",
  "organization_id": "org_456",
  "is_active": true,
  "email_verified": false,
  "created_at": "2024-01-01T10:00:00",
  "last_login": "2024-01-02T14:30:00"
}
```

### 4. Refresh Access Token

```bash
curl -X POST http://localhost:8000/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

### 5. Logout

```bash
curl -X POST http://localhost:8000/auth/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Dataset Management

### 6. Upload Dataset

```bash
curl -X POST http://localhost:8000/datasets/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sales_data.csv"
```

Response:
```json
{
  "id": "dataset_789",
  "name": "sales_data.csv",
  "file_size": 45620,
  "file_type": "csv",
  "processing_status": "pending",
  "created_at": "2024-01-02T15:00:00",
  "updated_at": "2024-01-02T15:00:00"
}
```

### 7. List Datasets

```bash
curl http://localhost:8000/datasets \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
[
  {
    "id": "dataset_789",
    "name": "sales_data.csv",
    "row_count": 5000,
    "column_count": 12,
    "processing_status": "completed",
    "created_at": "2024-01-02T15:00:00"
  }
]
```

### 8. Get Dataset Details

```bash
curl http://localhost:8000/datasets/dataset_789 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 9. Delete Dataset

```bash
curl -X DELETE http://localhost:8000/datasets/dataset_789 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## AI Analytics Assistant

### 10. Send Question to AI

```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_001",
    "content": "What are my top 5 products by revenue?"
  }'
```

Response:
```json
{
  "id": "msg_123",
  "conversation_id": "conv_001",
  "message_type": "user",
  "content": "What are my top 5 products by revenue?",
  "created_at": "2024-01-02T16:00:00"
}
```

### 11. Get Conversation History

```bash
curl http://localhost:8000/ai/conversations/conv_001 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
[
  {
    "id": "msg_123",
    "conversation_id": "conv_001",
    "message_type": "user",
    "content": "What are my top 5 products by revenue?",
    "created_at": "2024-01-02T16:00:00"
  },
  {
    "id": "msg_124",
    "conversation_id": "conv_001",
    "message_type": "assistant",
    "content": "Based on your data, your top 5 products are...",
    "sql_query": "SELECT product, SUM(revenue) FROM sales GROUP BY product ORDER BY SUM(revenue) DESC LIMIT 5",
    "chart_type": "bar",
    "created_at": "2024-01-02T16:00:05"
  }
]
```

## JavaScript/TypeScript Examples

### Register User

```typescript
import { api } from '@/lib/api';
import { useAuthStore } from '@/stores/auth';

async function handleRegister() {
  try {
    const response = await api.post('/auth/register', {
      email: 'user@example.com',
      password: 'SecurePass123!',
      full_name: 'Jane Doe',
      organization_name: 'My Retail'
    });
    
    // Store tokens
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    
    // Update store
    const userStore = useAuthStore();
    await userStore.fetchCurrentUser();
  } catch (error) {
    console.error('Registration failed:', error.response?.data?.detail);
  }
}
```

### Upload Dataset

```typescript
async function uploadDataset(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await api.post('/datasets/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('Dataset uploaded:', response.data);
    return response.data;
  } catch (error) {
    console.error('Upload failed:', error);
  }
}
```

### Send AI Query

```typescript
async function askQuestion(question: string, conversationId: string) {
  try {
    const response = await api.post('/ai/chat', {
      conversation_id: conversationId,
      content: question
    });
    
    return response.data;
  } catch (error) {
    console.error('Query failed:', error);
  }
}
```

## Python Examples

### Login and Get Token

```python
import requests

def login(email: str, password: str) -> str:
    response = requests.post(
        'http://localhost:8000/auth/login',
        json={
            'email': email,
            'password': password
        }
    )
    return response.json()['access_token']

token = login('john@example.com', 'password')
```

### Upload Dataset

```python
def upload_dataset(token: str, file_path: str) -> dict:
    headers = {'Authorization': f'Bearer {token}'}
    
    with open(file_path, 'rb') as f:
        response = requests.post(
            'http://localhost:8000/datasets/upload',
            headers=headers,
            files={'file': f}
        )
    
    return response.json()

dataset = upload_dataset(token, 'sales_data.csv')
```

### Query AI Assistant

```python
def ask_ai(token: str, question: str, conversation_id: str) -> dict:
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        'http://localhost:8000/ai/chat',
        headers=headers,
        json={
            'conversation_id': conversation_id,
            'content': question
        }
    )
    
    return response.json()

result = ask_ai(token, 'Top 10 products by profit', 'conv_123')
```

## Common Use Cases

### Workflow: Complete Analysis

1. **Register**
   ```bash
   POST /auth/register
   ```

2. **Upload Sales Data**
   ```bash
   POST /datasets/upload
   ```

3. **Wait for Processing** (via polling)
   ```bash
   GET /datasets/{id}
   # Check processing_status
   ```

4. **Ask Questions**
   ```bash
   POST /ai/chat
   # "What categories are underperforming?"
   # "Show forecast for next quarter"
   ```

5. **Export Data**
   ```bash
   GET /analytics/sales-by-category
   # Save as CSV
   ```

## Error Handling

### Unauthorized (Missing/Invalid Token)
```json
{
  "detail": "Not authenticated"
}
```
Status: 401

### Forbidden (Insufficient Permissions)
```json
{
  "detail": "User role 'viewer' lacks 'delete_dataset' permission"
}
```
Status: 403

### Not Found
```json
{
  "detail": "Dataset dataset_789 not found"
}
```
Status: 404

### Validation Error
```json
{
  "detail": "Email already registered"
}
```
Status: 409

## Rate Limiting

- Default: 100 requests per minute per user
- Exceeding: Returns 429 Too Many Requests

## Token Expiration

- Access Token: 30 minutes
- Refresh Token: 7 days
- Refresh endpoint: POST /auth/refresh

## CORS Headers

The API accepts requests from:
- http://localhost:3000
- http://localhost:8000
- Production domains

---

For more details, see the full API documentation at:
http://localhost:8000/docs (Swagger UI)
http://localhost:8000/redoc (ReDoc)
"""
