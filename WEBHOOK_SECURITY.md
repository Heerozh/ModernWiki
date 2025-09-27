# GitHub Webhook 安全配置指南

## 概述

ModernWiki 的 webhook 服务现在支持 GitHub 标准的 HMAC-SHA256 签名验证，确保只有来自 GitHub 的合法请求才能触发站点重建。

## 配置步骤

### 1. 生成 Webhook Secret

首先生成一个安全的随机密钥：

```bash
# 使用 Python 生成 64 位十六进制字符串
python -c "import secrets; print(secrets.token_hex(32))"

# 或者使用 OpenSSL
openssl rand -hex 32
```

### 2. 配置环境变量

将生成的密钥添加到你的 `.env` 文件中：

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件，设置 WEBHOOK_SECRET
WEBHOOK_SECRET=your_generated_secret_here
```

### 3. 在 GitHub 中配置 Webhook

1. 进入你的 GitHub 仓库设置
2. 点击 "Webhooks" 选项
3. 点击 "Add webhook"
4. 填写配置：
   - **Payload URL**: `http://your-domain.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: 输入你在步骤1中生成的密钥
   - **Which events**: 选择 "Just the push event" 或根据需要选择其他事件

### 4. 重启服务

```bash
docker compose down
docker compose up --build
```

## 安全特性

- **HMAC-SHA256 签名验证**: 验证请求确实来自 GitHub
- **事件类型记录**: 记录 GitHub 事件类型和操作
- **安全密钥比较**: 使用 `hmac.compare_digest()` 防止时序攻击
- **详细日志记录**: 记录验证过程和结果

## 故障排除

### 如果没有配置密钥

如果 `WEBHOOK_SECRET` 环境变量为空，webhook 会：
- 记录警告信息
- 跳过签名验证
- 继续处理请求（向后兼容）

### 签名验证失败

如果签名验证失败，webhook 会：
- 返回 401 Unauthorized 状态码
- 记录详细的错误信息
- 拒绝处理请求

### 检查日志

查看 webhook 容器的日志：

```bash
docker compose logs webhook
```

常见日志信息：
- `GitHub signature verification successful` - 验证成功
- `GitHub signature verification failed` - 签名不匹配
- `No signature header found` - 缺少签名头
- `WEBHOOK_SECRET not configured` - 未配置密钥

## 最佳实践

1. **定期更新密钥**: 定期更换 webhook 密钥以提高安全性
2. **安全存储**: 确保 `.env` 文件不被提交到版本控制系统
3. **监控日志**: 定期检查 webhook 日志以发现可疑活动
4. **HTTPS**: 在生产环境中使用 HTTPS 确保传输安全

## 兼容性

此实现完全兼容 GitHub 的 webhook 签名标准，支持：
- GitHub Enterprise
- GitHub.com
- 其他实现 GitHub webhook 标准的服务