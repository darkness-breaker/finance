# 记账工具

本地个人记账 Web 应用：添加账目、按月份/分类筛选查看、输入 ID 删除、分类统计图表。

技术栈：Python + Streamlit + SQLite3 + Plotly。数据存在本地 `budget.db` 文件，无需安装数据库服务。

## 安装与运行

先安装 Python 3（如已安装可跳过），然后：

```bash
# 1. 安装依赖（首次需要）
pip install -r requirements.txt

# 2. 启动应用
streamlit run app.py
```

浏览器会自动打开 `http://localhost:8501`。没自动打开就手动访问该地址。

停止运行：在终端按 `Ctrl + C`。

## 功能说明

侧边栏有三个页面：

1. **添加账目** — 填金额、分类、日期、备注，点"保存"即可
2. **查看列表** — 按月份、分类筛选，表格展示；下方输入 ID 删除账目
3. **分类统计** — 各分类支出的柱状图和统计表（笔数、金额、占比）

预设 6 个分类：餐饮、交通、购物、娱乐、居住、其他。

## 项目结构

```
├── app.py           # 界面（Streamlit）
├── database.py      # 数据库操作（SQLite）
├── requirements.txt # 依赖列表
└── budget.db        # 数据库文件（首次运行自动生成）
```

## 常见问题

- **端口被占用**：`streamlit run app.py --server.port 8502`
- **想重新开始记账**：删除 `budget.db` 文件，再运行即可（数据会清空）

## 打包成 exe（可选）

把整个应用打包成一个带图标的独立 exe，双击即可运行、自动打开浏览器，不需要装 Python：

```bash
# 1. 生成图标（项目里已有 icon.ico 可跳过）
python build_icon.py

# 2. 安装打包工具
pip install pyinstaller

# 3. 打包（Windows 下 --add-data 用分号分隔）
python -m PyInstaller --noconfirm --clean --onefile --name LedgerApp \
  --icon icon.ico --add-data "app.py;." --add-data "database.py;." \
  --collect-all streamlit --collect-all plotly launcher.py
```

打包产物在 `dist/LedgerApp.exe`。双击运行，记账数据保存在 **exe 同目录**的 `budget.db`（和 exe 一起拷贝即可随身带走数据）。

> 注意：exe 首次启动会慢一些（约 10~20 秒），因为要解压运行环境到临时目录，属正常现象。
