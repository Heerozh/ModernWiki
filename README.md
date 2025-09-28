# ModernWiki

一个用 Git 仓库充当数据库，Markdown 作为格式化语言的极简 Wiki 系统。

Wiki 的本质是版本控制和开源协作，使用成熟的 Git 可更好的管理恶意破坏问题，而 Markdown 也更易于编辑。

## 使用方式

## 1. 内容仓库

内容仓库就是 Wiki 的页面仓库，提供给用户任意修改，请使用 [ModernWikiTemplate](https://github.com/Heerozh/ModernWikiTemplate.git) 仓库为模板。仓库为 Hugo 项目格式，你可以在其中任意修改网站样式。


## 2. 网站服务器

本 Wiki 系统只在仓库更新时进行构建，平时为静态文件服务，性能开销极低。因此只需通过 Docker 就能轻松高性能运行。

前往某云，购买轻量应用服务器，开 docker，clone 本 repo，修改.env 文件，docker-compose up -d

## 快速开始

### 1. 设置 Git 仓库

**GitHub:**

直接 Fork [ModernWikiTemplate](https://github.com/Heerozh/ModernWikiTemplate.git)
另支持 码云、GitLab。

**（推荐）私有 Git 仓库：**

访问 http://localhost/git ，直接点Install Gitea，注册一个本地 Admin 账号，创建仓库时选 migrate，
克隆 https://github.com/Heerozh/ModernWikiTemplate.git

Gitea 的数据储存在 `data/gitea` 目录下。

> 注意仓库权限需打开所有人可 Push，否则要通过 RP 审核。如果只希望 Content 目录可 Push，而站点配置和样式文件需 PR，可以使用 Git 子模块，用 2 个不同的仓库完成。

### 2. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 Git 仓库：

```bash
GIT_REPO=https://github.com/your-username/your-wiki-content.git
GIT_BRANCH=main
DOMAIN=:80 # 本地测试只能使用:80，不然会无法访问
```
> [!NOTE] 每次修改 `.env` 后，需重新构建镜像：`docker compose build`

### 3. 启动系统

启动所有容器：

```bash
# 启动服务（日常使用）
docker compose up -d
```

### 4. 访问 Wiki

- 主站点：http://localhost
- Webhook 端点：http://localhost/webhook


### 5. 设置自动更新

以GitHub为例，设置 Push 时触发 Webhook：

1. 进入你的 GitHub 仓库设置
2. 点击 "Webhooks" 选项
3. 点击 "Add Webhook"
4. 填写配置：
   - **Payload URL**: `http://your-domain.com/webhook`
   - **Content type**: `application/json`
   - **Secret**: 输入你的随机密码
   - **Which events**: 选择 "Just the push event" 

当你的 Git 仓库内容更新时，此 Webhook 会触发 Hugo 重新构建网站。

另支持 Gitea， 码云（仅WebHook 密码模式） 和 GitLab，配置类似。

## 系统架构解析

ModernWiki 由四个 Docker 容器合并组成：

### 1. 站点刷新容器 (hugo-builder)

- 拉取公共 Git 仓库并使用 Hugo 生成静态网页
- 输出到共享的 `site` 目录
- 一次性容器，执行完退出。

### 2. 静态站点容器 (static-site)

- 持续服务 `site` 目录中的静态文件

### 3. Webhook 控制器容器 (webhook)

- 持续接收 git push 时的 webhook 请求
- 收到后通过 Docker API，重启 hugo-builder

### 4. 入口反代容器 (proxy)

- 监听 80 端口作为入口
- 路由规则：
  - `/` → 静态站点容器
  - `/webhook` → Webhook 容器
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

无需配置，系统会自动且定期为你的域名申请 Let's Encrypt 或 ZeroSSL 免费证书。确保：

- 域名 DNS 指向你的服务器
- 防火墙端口 80 和 443 对外开放


## 许可证

MIT License
