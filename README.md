# ModernWiki

一个用 Git 仓库充当数据库，Markdown 作为格式化语言的极简 Wiki 系统。

Wiki 的本质是版本控制和开源协作，使用成熟的 Git 可更好的管理恶意破坏问题，而 Markdown 也更易于编辑。

## 使用方式

## 1. 内容仓库

内容仓库就是 Wiki 的数据仓库，请使用 [ModernWikiTemplate](https://github.com/Heerozh/ModernWikiTemplate.git) 仓库为模板。仓库为 Hugo 项目格式，你可以在其中任意修改网站样式。

可以直接在 GitHub Fork，或用其他 Git 托管，也可通过 Gitea 搭建私有 Git 托管。

> 注意仓库权限可打开 Write 让用户可直接 Push，否则需要通过 RP 审核。如果希望 Content 目录可任意 Push，而其他配置和样式文件不可 Push，可以使用 Git 子模块，用 2 个不同的仓库完成。

## 2. 网站服务器

前往某云，购买轻量应用服务器，开 docker，clone 本 repo，修改.env 文件，docker-compose up -d

## 系统流程

## 系统架构

ModernWiki 由四个 Docker 容器组成：

### 1. 站点刷新容器 (hugo-builder)

- 基于 `klakegg/hugo:latest` 镜像
- 从环境变量获取 Git 仓库地址和分支
- 拉取 Git 仓库并使用 Hugo 生成静态网页
- 输出到共享 volume 的 `site` 目录

### 2. 静态站点容器 (static-site)

- 基于 `caddy:latest` 镜像
- 监听 3000 端口
- 服务 `site` 目录中的静态文件

### 3. Webhook 控制器容器 (webhook)

- 基于 Python Flask 框架
- 监听 5000 端口
- 接收 webhook 请求并触发站点重新构建

### 4. 入口反代容器 (proxy)

- 基于 `caddy:latest` 镜像
- 监听 80 端口作为入口
- 路由规则：
  - `/` → 静态网页容器
  - `/webhook` → webhook 容器
  - 支持导入额外的 Caddyfile 配置

## 快速开始

### 1. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 Git 仓库：

```bash
GIT_REPO=https://github.com/your-username/your-wiki-content.git
GIT_BRANCH=main
```

### 2. 启动系统

构建并启动所有容器：

```bash
# 构建站点（首次运行或内容更新时）
docker compose --profile build up -d

# 启动服务（日常使用）
docker compose up -d
```

### 3. 访问 Wiki

- 主站点：http://localhost
- 静态站点（直接访问）：http://localhost:3000
- Webhook 端点：http://localhost/webhook
- 健康检查：http://localhost/health

## 内容管理

### Git 仓库结构

你的 Git 仓库应该包含 Hugo 站点内容：

```
your-wiki-repo/
├── config.yaml          # Hugo 配置文件（可选）
├── content/             # Markdown 内容文件
│   ├── _index.md        # 首页
│   ├── page1.md         # 页面 1
│   └── folder/          # 文件夹
│       └── page2.md     # 页面 2
├── static/              # 静态资源（图片等）
└── layouts/             # 自定义模板（可选）
```

### 基本 Markdown 示例

在 `content/_index.md` 中：

```markdown
---
title: "欢迎使用 ModernWiki"
---

# 欢迎使用 ModernWiki

这是一个基于 Git + Hugo 的现代 Wiki 系统。

## 特性

- Git 版本控制
- 静态站点生成
- 自动构建部署
- 容器化部署
```

### 自动更新

当你的 Git 仓库内容更新时，可以通过以下方式触发站点重新构建：

1. **Webhook 方式**：配置 Git 仓库的 webhook 指向 `http://your-domain/webhook`
2. **手动触发**：发送 POST 请求到 `http://your-domain/webhook`
3. **重启容器**：`docker-compose restart hugo-builder`

## 自定义配置

### 添加自定义路由

在 `proxy-config/custom.caddyfile` 中添加自定义路由规则：

```caddyfile
# API 服务路由
handle /api* {
    reverse_proxy api-server:8080
}

# 管理面板路由
handle /admin* {
    reverse_proxy admin-panel:3001
}
```

### Hugo 主题和样式

如果你的 Git 仓库没有 Hugo 配置，系统会自动创建一个基本的配置和样式。你可以：

1. 在 Git 仓库中添加 `config.yaml` 配置文件
2. 在 `layouts/` 目录中自定义模板
3. 在 `static/` 目录中添加自定义 CSS/JS

## 开发和调试

### 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f hugo-builder
docker compose logs -f static-site
docker compose logs -f webhook
docker compose logs -f proxy
```

### 手动重建站点

```bash
# 方法 1：重启构建容器
docker compose restart hugo-builder

# 方法 2：通过 API
curl -X POST http://localhost/webhook

# 方法 3：手动触发
curl -X POST http://localhost:5000/rebuild
```

### 调试模式

启用调试模式以查看更详细的日志：

```bash
# 前台运行查看实时日志
docker compose --profile build up

# 或者单独启动某个服务进行调试
docker compose up hugo-builder
```

## 生产部署

### 1. 使用域名

修改 `containers/proxy/Caddyfile`，将 `:80` 替换为你的域名：

```caddyfile
yourdomain.com {
    # ... 其他配置保持不变
}
```

### 2. HTTPS 支持

Caddy 会自动为你的域名申请 Let's Encrypt 证书。确保：

- 域名 DNS 指向你的服务器
- 端口 80 和 443 对外开放

### 3. 数据持久化

系统使用 Docker volumes 来持久化数据：

- `site_data`：存储生成的静态网站文件

### 性能优化

本 Wiki 系统为静态站点，服务器只在内容更新时进行构建，平时仅提供静态文件服务，性能开销极低。

## 许可证

MIT License
