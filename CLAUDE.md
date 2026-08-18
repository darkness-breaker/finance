# Finance — 记账工具

本地个人记账 Web 应用。支持添加账目、按月份/分类筛选查看列表、输入 ID 删除、分类统计柱状图 + 统计表。

## 技术栈

Python 3 + Streamlit + SQLite3 + Plotly（无需外部数据库服务，数据存在本地文件）。

## 运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

浏览器访问 http://localhost:8501

## 项目结构

- `app.py` — Streamlit 界面。侧边栏 3 个页面：添加账目 / 查看列表 / 分类统计
- `database.py` — 所有 SQLite 操作（唯一读写数据库的模块）
- `requirements.txt` — 依赖：streamlit、plotly
- `launcher.py` — 打包成 exe 的启动器（进程内启动 Streamlit + 自动开浏览器 + 数据存 exe 同目录）
- `build_icon.py` / `icon.ico` — 生成应用图标
- `budget.db` — SQLite 数据库文件，首次运行自动生成，勿手动编辑
- `README.md` — 安装与运行说明

## 打包成 exe

用 PyInstaller：`python -m PyInstaller --onefile --icon icon.ico --add-data "app.py;." --add-data "database.py;." --collect-all streamlit --collect-all plotly launcher.py`。产物在 `dist/`。完整命令见 README。

**关键坑**：PyInstaller 会把 streamlit 解压到临时目录，路径不含 `site-packages`，导致 streamlit 误判为开发模式去连不存在的 Node 前端。`launcher.py` 里必须 `config.set_option("global.developmentMode", False)` 强制切回正常模式，否则界面空白。

## 数据库

`records` 表：

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | INTEGER | 主键自增 | 删除账目时用 |
| amount | REAL | 非空 | 金额 |
| category | TEXT | 非空 | 分类 |
| date | TEXT | 非空 | 日期，格式 `YYYY-MM-DD` |
| note | TEXT | 默认空 | 备注 |

预设 6 个分类：餐饮、交通、购物、娱乐、居住、其他。

## 页面行为

1. **添加账目**：表单填金额/分类/日期/备注，提交后写入数据库并提示成功
2. **查看列表**：月份 + 分类两个下拉框筛选；`st.dataframe` 展示，金额格式化为 `¥1,234.56`；显示筛选结果总支出；下方输入 ID + 删除按钮
3. **分类统计**：Plotly 交互式柱状图 + 统计表（分类 / 笔数 / 金额合计 / 占比）

## 开发约定

- 数据操作只写在 `database.py`，`app.py` 不直接写 SQL
- 金额展示统一 `¥` 千分位格式
- 分类只能取预设 6 个，不新增分类
- 改完代码跑 `streamlit run app.py` 手动验证
