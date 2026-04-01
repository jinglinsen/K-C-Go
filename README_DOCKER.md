# K-C-go 社区中心部署指南 (Docker 容器版 - 阿里云服务器)

通过 Docker 容器化部署是目前最推荐的方式。即使你的阿里云服务器由于历史原因处于 **Python 3.6** 环境，通过 Docker 我们依然可以在容器内运行最新的 **Python 3.11**，从而避免旧版本系统的语法与库兼容性问题。

---

## 🏗️ 1. 服务器准备 (Aliyun ECS)

### 1.1 安装 Docker 与 Docker-Compose
登录 ECS，执行以下命令安装：

```bash
# 更新 apt 索引
sudo apt update
sudo apt install -y docker.io docker-compose

# 启动 Docker 并设置自启
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户加入 docker 组 (可选，避免每次加 sudo)
sudo usermod -aG docker $USER
```
*注：对于 CentOS 系统，使用 `yum install -y docker docker-compose`。*

### 1.2 下载代码
```bash
sudo mkdir -p /var/www/K-C-go
sudo chown -R $USER:$USER /var/www/K-C-go
cd /var/www/K-C-go

# 通过 Git Clone 或 SCP 将文件同步至此处
# 确保结构如下:
# /var/www/K-C-go
#├── backend/
#├── frontend/
#└── docker-compose.yml
```

---

## 🚀 2. 一键启动项目

进入项目根目录，直接使用 docker-compose 启动：

```bash
cd /var/www/K-C-go

# 一键编译各容器并后台运行
sudo docker-compose up -d --build
```
此时 Docker 会自动完成以下操作：
1.  **Frontend**: 编译 Vue 3 代码产物，并注入定制的 Nginx 配置。
2.  **Backend**: 在容器内安装最新的 Python 环境与依赖，启动 Gunicorn 进程。
3.  **Reverse Proxy**: 集成前端与后端接口，解决跨域问题。

---

## 🗃️ 3. 数据库与数据持久化

*   **默认配置**: 容器内生成的 `community.db` 会被实时映射到宿主机的 `./backend/data/` 目录下。
*   **迁移 MySQL**: 阿里云用户推荐使用 **RDS (MySQL)**。只需在 `docker-compose.yml` 的 `DATABASE_URL` 中填入 RDS 的内网地址、用户名及密码。
*   **初始化**: 本地开发或新部署时，后端容器启动后会自动检测并初始化数据库表结构。

---

## 🔐 4. 阿里云安全组规则 (必须)

请登录阿里云控制台，在对应 ECS 实例的 **安全组规则** 中添加入方向规则：

| 协议 | 端口范围 | 授权对象 | 描述 |
| :--- | :--- | :--- | :--- |
| TCP | 80/80 | 0.0.0.0/0 | 前端/API 统一入口 |
| TCP | 22/22 | 你的 IP | SSH 管理 |

---

## 💡 常用维护命令

*   **查看运行状态**: `sudo docker-compose ps`
*   **查看后端实时日志**: `sudo docker-compose logs -f backend`
*   **重新构建并更新发布**:
    ```bash
    # 只要改动了代码，执行以下命令自动增量更新
    sudo docker-compose up -d --build
    ```
*   **重启所有容器**: `sudo docker-compose restart`
*   **停止并删除容器**: `sudo docker-compose down` (此操作不会删除映射出的 `./backend/data/` 数据)。

---

## 📦 5. Docker 部署优势
*   **版本隔离**: 宿主机的 Python 3.6 不会影响容器内的 3.11 运行环境。
*   **一键扩容**: 随时可以横向扩展。
*   **环境一致**: “它在我机器上能跑，也一定在云上能跑”。
