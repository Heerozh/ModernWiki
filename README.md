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
- Webhook 端点：http://localhost/webhook

### 4. 设置自动更新

当你的 Git 仓库内容更新时，配置 Git 仓库的 webhook 指向 `http://your-domain/webhook`

## 系统架构解析

ModernWiki 由四个 Docker 容器合并组成：

### 1. 站点刷新容器 (hugo-builder)

- 拉取 Git 仓库并使用 Hugo 生成静态网页
- 输出到共享的 `site` 目录
- 一次性容器，执行完退出。

### 2. 静态站点容器 (static-site)

- 持续服务 `site` 目录中的静态文件

### 3. Webhook 控制器容器 (webhook)

- 持续接收 git push 时的 webhook 请求
- 收到后 restart hugo-builder

### 4. 入口反代容器 (proxy)

- 监听 80 端口作为入口
- 路由规则：
  - `/` → 静态网页容器
  - `/webhook` → webhook 容器
  - 支持导入额外的 Caddyfile 站点配置

## 开发和调试

### 升级

首先更新本仓库
```bash
git pull
```
然后执行 docker 重建，所有镜像和软件即会升级到最新版。

```bash
docker compose build
```

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
docker compose restart hugo-builder

```

## 生产部署

### 1. 使用域名

修改 `.evn`，将 `DOMAIN=` 设置为你的域名。


### 2. HTTPS 支持

Caddy 会自动为你的域名申请 Let's Encrypt 证书。确保：

- 域名 DNS 指向你的服务器
- 防火墙端口 80 和 443 对外开放


### 性能优化

本 Wiki 系统为静态站点，服务器只在内容更新时进行构建，平时仅提供静态文件服务，性能开销极低。因此可以放心使用 Docker.

## 许可证

MIT License
