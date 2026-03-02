# API 使用文档

## 认证机制

### Token认证

所有API请求都需要在Header中包含认证Token：

```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 获取Token

发送POST请求到认证端点：

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

响应示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

## 用户管理API

### 获取用户信息

```bash
GET /api/v1/users/{user_id}
Authorization: Bearer YOUR_ACCESS_TOKEN
```

响应示例：
```json
{
  "id": 123,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2023-01-01T00:00:00Z",
  "last_login": "2023-12-01T10:30:00Z"
}
```

### 创建用户

```bash
POST /api/v1/users
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "username": "new_user",
  "email": "user@example.com",
  "password": "secure_password",
  "role": "user"
}
```

### 更新用户信息

```bash
PUT /api/v1/users/{user_id}
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "email": "newemail@example.com",
  "role": "admin"
}
```

### 删除用户

```bash
DELETE /api/v1/users/{user_id}
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 数据查询API

### 获取列表数据

```bash
GET /api/v1/data?page=1&limit=20&sort=created_at&order=desc
Authorization: Bearer YOUR_ACCESS_TOKEN
```

查询参数说明：
- `page`: 页码，从1开始，默认为1
- `limit`: 每页记录数，默认为20，最大为100
- `sort`: 排序字段，支持created_at、updated_at、name
- `order`: 排序方向，asc或desc，默认为asc
- `search`: 搜索关键词，模糊匹配name和description字段

响应示例：
```json
{
  "data": [
    {
      "id": 1,
      "name": "示例数据1",
      "description": "这是一个示例",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

### 创建数据记录

```bash
POST /api/v1/data
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "name": "新数据记录",
  "description": "数据描述",
  "category": "类别A",
  "tags": ["标签1", "标签2"]
}
```

### 批量操作

```bash
POST /api/v1/data/batch
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: application/json

{
  "action": "delete",
  "ids": [1, 2, 3, 4, 5]
}
```

支持的批量操作：
- `delete`: 删除指定记录
- `update`: 批量更新记录
- `export`: 导出指定记录

## 文件上传API

### 单文件上传

```bash
POST /api/v1/files/upload
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: multipart/form-data

form-data:
- file: [选择文件]
- category: "documents"
- description: "文件描述"
```

### 多文件上传

```bash
POST /api/v1/files/upload/batch
Authorization: Bearer YOUR_ACCESS_TOKEN
Content-Type: multipart/form-data

form-data:
- files[]: [文件1]
- files[]: [文件2]
- category: "images"
```

### 文件下载

```bash
GET /api/v1/files/{file_id}/download
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 监控API

### 系统状态

```bash
GET /api/v1/system/status
Authorization: Bearer YOUR_ACCESS_TOKEN
```

响应示例：
```json
{
  "status": "healthy",
  "version": "1.2.3",
  "uptime": 86400,
  "database": {
    "status": "connected",
    "connection_pool": {
      "active": 5,
      "idle": 15,
      "max": 20
    }
  },
  "cache": {
    "status": "connected",
    "memory_usage": "245MB",
    "hit_rate": 0.95
  }
}
```

### 性能指标

```bash
GET /api/v1/system/metrics?from=2023-12-01&to=2023-12-02
Authorization: Bearer YOUR_ACCESS_TOKEN
```

响应包含以下指标：
- CPU使用率
- 内存使用率
- 磁盘I/O
- 网络流量
- API响应时间
- 错误率

## 错误处理

### 错误响应格式

所有错误都会返回统一的JSON格式：

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数验证失败",
    "details": [
      {
        "field": "email",
        "message": "邮箱格式不正确"
      }
    ]
  },
  "timestamp": "2023-12-01T10:30:00Z",
  "path": "/api/v1/users"
}
```

### 常见错误码

- `400 BAD_REQUEST`: 请求参数错误
- `401 UNAUTHORIZED`: 未认证或Token无效
- `403 FORBIDDEN`: 权限不足
- `404 NOT_FOUND`: 资源不存在
- `429 TOO_MANY_REQUESTS`: 请求频率过高
- `500 INTERNAL_SERVER_ERROR`: 服务器内部错误

## 限流规则

### API限流

- **普通用户**: 每分钟100次请求
- **VIP用户**: 每分钟1000次请求
- **管理员**: 无限制

### 响应头

每个响应都会包含限流信息：

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638360000
```

## SDK使用示例

### Python SDK

```python
from devops_mas_api import DevOpsMASClient

# 初始化客户端
client = DevOpsMASClient(
    base_url="https://api.example.com",
    token="your_access_token"
)

# 获取用户信息
user = client.users.get(user_id=123)
print(f"用户名: {user.username}")

# 创建数据记录
data = client.data.create({
    "name": "新记录",
    "description": "描述信息"
})

# 上传文件
with open("document.pdf", "rb") as f:
    file_info = client.files.upload(
        file=f,
        category="documents"
    )
```

### JavaScript SDK

```javascript
import { DevOpsMASClient } from 'devops-mas-api-js';

// 初始化客户端
const client = new DevOpsMASClient({
  baseURL: 'https://api.example.com',
  token: 'your_access_token'
});

// 获取数据列表
const response = await client.data.list({
  page: 1,
  limit: 20,
  search: '关键词'
});

console.log('数据:', response.data);
console.log('总数:', response.pagination.total);
```

## 最佳实践

### 错误重试

建议实现指数退避重试机制：

```python
import time
import random

def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            if e.status_code >= 500:
                # 服务器错误，重试
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
            else:
                # 客户端错误，不重试
                raise
```

### 缓存策略

- 对于不经常变化的数据，使用客户端缓存
- 设置合适的缓存过期时间
- 利用HTTP ETag进行条件请求

### 安全建议

- 永远不要在客户端代码中硬编码Token
- 使用HTTPS进行所有API通信
- 定期轮换访问Token
- 实施适当的输入验证和清理 