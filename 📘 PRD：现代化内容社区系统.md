📘 PRD（重构版 V2.0）

## 现代化内容社区系统（Content Community Platform）

------

# 1️⃣ 项目概述（升级）

## 1.1 项目名称

现代化内容社区系统（Community Hub）

------

## 1.2 产品定位（重写重点）

本产品是一个：

> 面向开发者的“内容生产 + 分发 + 互动”轻量社区系统

对标：

- Linux 社区（结构）
- 掘金（内容流）
- 知乎（互动）
- Reddit（轻社区逻辑）

------

## 1.3 核心目标（从功能变产品）

### 🎯 V1目标不是“博客系统”，而是：

- 内容可持续生产
- 用户可互动形成社区
- 内容可被分发（热榜/推荐）
- 系统可扩展为社区平台

------

# 2️⃣ 用户角色体系（新增🔥）

## 2.1 用户分层

| 角色                      | 权限               |
| ------------------------- | ------------------ |
| guest（游客）             | 浏览内容           |
| user（普通用户）          | 发帖 / 评论 / 点赞 |
| admin（管理员）           | 内容管理           |
| super_admin（超级管理员） | 全局管理           |

------

## 2.2 权限原则

- 最小权限原则（Least Privilege）
- 管理权限不可自赋
- super_admin 只能由初始化创建

------

# 3️⃣ 产品核心逻辑（新增🔥）

## 3.1 内容生命周期

```text
创建 → 发布 → 浏览 → 互动（点赞/评论） → 热度计算 → 推荐流
```

------

## 3.2 内容分发逻辑

内容流分三类：

- 最新流（时间排序）
- 热门流（热度排序）
- 标签流（兴趣过滤）

------

## 3.3 热度衰减机制（优化）

```text
heat = (like * 2 + comment * 3 + view * 1) / (1 + hours_since_publish)
```

------

# 4️⃣ 系统架构（优化版）

## 4.1 技术架构

- 前端：Vue.js
- 后端：FastAPI
- DB：PostgreSQL
- Cache：Redis
- 部署：Docker + Nginx

------

## 4.2 架构演进（新增）

### V1（单体）

- FastAPI 单体服务

### V2（预留）

- 用户服务拆分
- 内容服务拆分
- 推荐服务独立

------

# 5️⃣ 功能模块（重构）

------

# 5.1 用户系统（增强）

## 功能

- 注册 / 登录
- JWT认证
- 个人主页
- 角色绑定

## 新增能力

- 登录设备识别（可扩展）
- Token刷新机制

------

# 5.2 内容系统（核心重构）

## 功能

- Markdown发帖
- 编辑 / 删除
- 标签系统
- 浏览量统计

## 新增规则

- 未登录只能浏览
- 删除需权限校验
- 编辑只能本人或admin

------

# 5.3 评论系统（升级）

## 功能

- 评论文章
- 回复评论（树结构）
- 删除评论

## 约束

- 最大嵌套深度：3层
- 防刷评论（Redis限流）

------

# 5.4 点赞系统（优化）

## 规则

- 用户对同一文章只能点赞一次
- Redis记录状态

## 数据一致性策略

- Redis（实时）
- DB（最终一致）

------

# 5.5 热榜系统（重写）

## 目标

构建“可运营的内容排序系统”

## 排序策略

```text
score = engagement_score * decay_factor
```

## Redis结构

```text
ZSET: hot:posts
```

------

# 5.6 搜索系统（升级）

## V1

- LIKE 模糊查询

## V2（预留）

- PostgreSQL全文索引（tsvector）

------

# 6️⃣ 数据模型（优化版）

------

## 6.1 user（升级）

```sql
id BIGINT PK
username VARCHAR UNIQUE
password_hash TEXT
role VARCHAR DEFAULT 'user'
avatar TEXT
bio TEXT
created_at TIMESTAMP
```

------

## 6.2 post（优化）

```sql
id BIGINT PK
user_id BIGINT
title VARCHAR
content TEXT
tags TEXT[]
status VARCHAR  -- draft/published/deleted
view_count INT
like_count INT
comment_count INT
created_at TIMESTAMP
```

------

## 6.3 comment（增强）

```sql
id BIGINT PK
post_id BIGINT
user_id BIGINT
parent_id BIGINT NULL
content TEXT
level INT
created_at TIMESTAMP
```

------

## 6.4 like（优化）

```sql
id BIGINT PK
user_id BIGINT
post_id BIGINT
created_at TIMESTAMP
UNIQUE(user_id, post_id)
```

------

# 7️⃣ API设计（规范化）

------

## 7.1 Auth

```
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
```

------

## 7.2 User

```
GET /api/v1/user/me
GET /api/v1/user/{id}
```

------

## 7.3 Post

```
GET    /api/v1/posts
GET    /api/v1/posts/{id}
POST   /api/v1/posts
PUT    /api/v1/posts/{id}
DELETE /api/v1/posts/{id}
```

------

## 7.4 Social

```
POST /api/v1/posts/{id}/like
POST /api/v1/comments
GET  /api/v1/posts/{id}/comments
```

------

## 7.5 Admin（新增🔥）

```
DELETE /api/v1/admin/post/{id}
DELETE /api/v1/admin/comment/{id}
PUT    /api/v1/admin/user/{id}/role
```

------

# 8️⃣ 前端设计（升级）

------

## 8.1 页面结构

- Home（推荐流）
- Trending（热榜）
- Post Detail
- Editor（Markdown）
- User Profile
- Admin Dashboard（新增🔥）

------

## 8.2 UI风格升级

参考：

- Linux 社区结构
- GitHub Feed 风格
- 掘金卡片流

------

# 9️⃣ 非功能需求（强化）

------

## 9.1 性能

- 首页 < 200ms（Redis缓存）
- API < 300ms
- 支持 1000+ 并发（V1）

------

## 9.2 安全

- JWT认证
- RBAC权限控制
- Redis限流
- SQLAlchemy防注入

------

## 9.3 可用性

- Docker一键部署
- Nginx反向代理
- 断线不影响核心功能

------

# 🔟 风险控制（新增🔥）

| 风险       | 方案           |
| ---------- | -------------- |
| 内容刷屏   | Redis限流      |
| SQL注入    | ORM            |
| 热榜作弊   | 权重衰减       |
| 数据不一致 | Redis + DB双写 |

------

# 1️⃣1️⃣ 项目里程碑（优化）

------

## Phase 1（MVP）

- 用户系统
- 发帖系统
- 评论系统

------

## Phase 2（社区化）

- 点赞
- 热榜
- 标签系统

------

## Phase 3（产品化）

- 搜索
- 管理后台
- 权限系统

------

## Phase 4（工程化）

- Docker
- CI/CD
- 性能优化



------

