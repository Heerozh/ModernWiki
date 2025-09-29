# ModernWiki

一个用 Git 仓库充当数据库，Markdown 作为格式化语言的极简 Wiki 系统。

Wiki 的本质是版本控制和开源协作，使用成熟的 Git 可更好的管理恶意破坏问题，而 Markdown 也更易于编辑。

## 快速开始

## 1. 建内容仓库

内容仓库就是 Wiki 的页面仓库，提供给用户任意修改，请使用 [ModernWikiTemplate](https://github.com/Heerozh/ModernWikiTemplate.git) 仓库为模板。仓库为 Hugo 项目格式，你可以在其中任意修改网站样式。

### **GitHub:**

直接 Fork [ModernWikiTemplate](https://github.com/Heerozh/ModernWikiTemplate.git)
另支持 码云、GitLab。

### **（推荐）私有 Git 仓库：**

先跳过，启动完系统后，回来设置：

访问 http://localhost/git ，直接点Install Gitea(立即安装)，注册一个 Admin 账号，点右上角 ➕，选 migrate（迁移外部仓库），
克隆 https://github.com/Heerozh/ModernWikiTemplate.git
，改名为Wiki。

> 注意仓库权限需打开所有人可 Push，否则要通过 RP 审核。如果只希望 Content 目录可 Push，而站点配置和样式文件需 PR，可以使用 Git 子模块，用 2 个不同的仓库完成。

## 2. 配置环境变量

复制环境变量模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置你的 Git 仓库：

```bash
GIT_REPO=https:/domain.com/your-username/your-wiki-content.git
GIT_BRANCH=master
DOMAIN=:80 # 本地测试只能使用:80，不然会无法访问
```

> [!NOTE] 
> 每次修改 `.env` 后，需重新构建镜像：`docker compose build`

## 3. 启动系统

先安装 Docker Engine 和 docker-compose-plugin，然后：


```bash
# 启动服务（第三方Git托管）
docker compose up -d

# 启动服务（本地自建Gitea托管)
docker compose --profile with-gitea up -d
```

## 4. 访问 Wiki

- 主站点：http://localhost
- Webhook 端点：http://localhost/webhook
- Gitea本地仓库（如果启用）：http://localhost/git/

## 5. 设置自动更新

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

ModernWiki 由多个 Docker 容器合并组成，选用轻量级系统，仅130M内存：

### 1. 站点刷新容器 (hugo-builder)

- 拉取公共 Git 仓库并使用 Hugo 生成静态网页
- 输出到共享的 `site` 目录
- 一次性容器，执行完退出。

### 2. 静态站点容器 (static-site)

- 持续服务 `site` 目录中的静态文件

### 3. Webhook 控制器容器 (webhook)

- 持续接收 git push 时的 webhook 请求
- 收到后通过 Docker API，重启 hugo-builder

### 4. 评论服务器

- artalk


### 5. 可选：Gitea 容器 (gitea)

- 可选容器，用于自建 Git 网页托管
- Gitea 的数据储存在 `data/gitea` 目录下，需要备份

### 6. 入口反代容器 (proxy)

- 监听 80 端口作为入口
- 路由规则：
  - `/` → 静态站点容器
  - `/webhook` → Webhook 容器
  - 支持导入额外的 Caddyfile 站点配置

## 开发和调试

### 升级

首先更新本仓库，然后执行 docker 重建，所有镜像和软件即会升级到最新版。

```bash
git pull
docker compose build --pull
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

本 Wiki 系统只在仓库更新时进行构建，平时为静态文件服务，性能开销极低。所以突发性能实例就足够（**价格-50%**）。

### 1. 使用域名

修改 `.evn`，将 `DOMAIN=` 设置为你的域名。


### 2. HTTPS 支持

无需配置，系统会自动且定期为你的域名申请 Let's Encrypt 或 ZeroSSL 免费证书。确保：

- 域名 DNS 指向你的服务器
- 防火墙端口 80 和 443 对外开放

## Serverless 部署方式 （TODO）

这是一种价格最低的部署方式，只需购买带宽和存储，但部署麻烦，功能少，不推荐仅供参考。

- 使用第三方托管仓库
- 利用函数计算FC，通过Http触发器接收Webhook，启动hugo-builder容器，输出到OSS储存
- 对OSS开启静态网站托管，设置域名
- 再设一个函数计算FC，每个月定时触发，更新并上传SSL证书到OSS


## 许可证

MIT License
