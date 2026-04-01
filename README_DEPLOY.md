# K-C-go 社区中心部署指南 (阿里云服务器)

本指南详细说明了如何将 **K-C-go 现代化内容社区中心** 部署到阿里云服务器（ECS）上，包括环境准备、后端 Systemd 服务配置、前端 Nginx 托管。

---

## 🏗️ 1. 环境准备 (Aliyun ECS)

### 1.1 推荐系统
*   **Ubuntu 22.04 LTS** (推荐) 或 CentOS 7.9+
*   至少 **2GB 内存** (编译前端所需)

### 1.2 基础工具安装
```bash
# 更新并安装基础依赖
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip nginx git curl

# 安装 Node.js 18+ (使用 NodeSource)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

---

## 🚀 2. 后端部署 (FastAPI)

### 2.1 路径与环境
```bash
sudo mkdir -p /var/www/K-C-go
sudo chown -R $USER:$USER /var/www/K-C-go
cd /var/www/K-C-go/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.2 数据库初始化
本项目使用 **SQLite** (默认) 或 **MySQL**。
*   **默认配置**: 只需运行程序一次，`community.db` 将自动在 `backend/` 下生成。
*   **MySQL 配置**: 在环境变量中设置 `DATABASE_URL=mysql+pymysql://user:pass@localhost/dbname`。

### 2.3 Systemd 后台服务配置
创建服务文件 `/etc/systemd/system/k-c-go-backend.service`:

```ini
[Unit]
Description=K-C-go Backend Production API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/K-C-go/backend
# 路径根据实际情况调整
Environment="PATH=/var/www/K-C-go/backend/venv/bin"
# 后台使用 Gunicorn 多进程管理
ExecStart=/var/www/K-C-go/backend/venv/bin/gunicorn main:app \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8000 \
    --access-log /var/log/nginx/api_access.log

[Install]
WantedBy=multi-user.target
```

启动并自启：
```bash
sudo systemctl daemon-reload
sudo systemctl enable k-c-go-backend
sudo systemctl start k-c-go-backend
```

---

## 🎨 3. 前端部署 (Vue 3 + Vite)

### 3.1 构建静态资源
```bash
cd /var/www/K-C-go/frontend
npm install
npm run build
```
输出目录位于 `/var/www/K-C-go/frontend/dist`。

### 3.2 Nginx 虚拟主机配置
创建 `/etc/nginx/sites-available/k-c-go`:

```nginx
server {
    listen 80;
    server_name your_server_ip; # 修改为阿里云公网 IP 或 域名

    # 前端入口
    location / {
        root /var/www/K-C-go/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 反向代理后端 API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # 视频上传支持: 解除限制
        client_max_body_size 100M;
    }
}
```

启用并重启：
```bash
sudo ln -s /etc/nginx/sites-available/k-c-go /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 🔐 4. 阿里云防火墙 (安全组)

务必在阿里云控制台 -> ECS 实例 -> **安全组规则** 中开放以下端口：

1.  **80 (TCP)**: 前端/API 网络访问 (必需)
2.  **443 (TCP)**: SSL/HTTPS (如有)
3.  **22 (TCP)**: SSH 管理

---

## 💡 维护 tips
*   **日志**: `journalctl -u k-c-go-backend -f`
*   **权限**: `sudo chown -R www-data:www-data /var/www/K-C-go` 以防静态资源 403。
