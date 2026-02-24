# 电脑硬件配置推荐系统

实时参考电商价格、根据预算和应用场景智能推荐电脑硬件配置的网站。

## 功能特性

- **智能推荐**：基于预算、应用场景（办公/游戏/设计/开发等）推荐配置
- **多维度考量**：性价比、性能、外观、使用场所
- **价格管理**：通过后台维护本地价格数据，不直接对接第三方电商 API

## 技术栈

- **后端**: Python + FastAPI
- **数据库**: SQLite (可切换 PostgreSQL)
- **前端**: HTML + Tailwind CSS + Alpine.js

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt
# 或: python -m pip install -r requirements.txt

# 初始化数据库（填充示例硬件数据）
python -m app.init_db

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0
```

访问 http://localhost:8000

## 主要 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/recommend` | POST | 获取配置推荐 |
| `/api/components` | GET | 列出组件及价格 |
| `/api/components` | POST | 添加组件 |
| `/api/prices` | PUT | 更新价格（手动维护） |
