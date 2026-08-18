"""记账工具：Streamlit 界面入口。运行 streamlit run app.py 启动。"""

import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date

import database

# 启动时确保数据库表已创建
database.init_db()

st.set_page_config(page_title="记账工具", page_icon="💰")
st.sidebar.title("记账工具")

# 侧边栏导航：三个页面
page = st.sidebar.radio("导航", ["添加账目", "查看列表", "分类统计"])


# ---------- 页面一：添加账目 ----------
if page == "添加账目":
    st.title("添加账目")

    with st.form("add_form", clear_on_submit=True):
        amount = st.number_input("金额（元）", min_value=0.01, step=0.01, format="%.2f")
        category = st.selectbox("分类", database.CATEGORIES)
        picked_date = st.date_input("日期", value=date.today())
        note = st.text_input("备注（选填）")
        submitted = st.form_submit_button("保存")

    if submitted:
        database.add_record(amount, category, picked_date.isoformat(), note)
        st.success(f"已保存：{category} ¥{amount:,.2f}，日期 {picked_date}")


# ---------- 页面二：查看列表 ----------
if page == "查看列表":
    st.title("查看列表")

    # 删除账目成功后会重新加载页面，这里显示当时的提示
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    # 筛选控件：月份 + 分类
    month = st.selectbox("月份", ["全部"] + database.get_months())
    category = st.selectbox("分类", ["全部"] + database.CATEGORIES)

    records = database.get_records(
        month=None if month == "全部" else month,
        category=None if category == "全部" else category,
    )

    total = sum(record[3] for record in records)
    st.metric("筛选结果总支出", f"¥{total:,.2f}")

    if records:
        df = pd.DataFrame(records, columns=["ID", "日期", "分类", "金额", "备注"])
        df["金额"] = df["金额"].apply(lambda x: f"¥{x:,.2f}")
        st.dataframe(df, hide_index=True)
    else:
        st.info("当前筛选条件下没有记录")

    # 删除账目：输入 ID
    st.divider()
    st.subheader("删除账目")
    with st.form("delete_form"):
        delete_id = st.number_input("要删除的账目 ID", min_value=1, step=1, value=1)
        delete_clicked = st.form_submit_button("删除")

    if delete_clicked:
        deleted = database.delete_record(int(delete_id))
        if deleted:
            st.session_state["flash"] = f"已删除 ID {delete_id}"
            st.rerun()
        else:
            st.error(f"ID {delete_id} 不存在，请检查后重试")


# ---------- 页面三：分类统计 ----------
if page == "分类统计":
    st.title("分类统计")

    stats = database.get_category_stats()
    df = pd.DataFrame(stats, columns=["分类", "笔数", "金额合计"])

    total_all = df["金额合计"].sum()
    df["占比"] = df["金额合计"] / total_all * 100 if total_all > 0 else 0.0

    # Plotly 交互式柱状图
    fig = px.bar(
        df,
        x="分类",
        y="金额合计",
        text="金额合计",
        title="各分类支出",
        labels={"金额合计": "金额（元）", "分类": "分类"},
    )
    fig.update_traces(texttemplate="¥%{text:,.2f}", textposition="outside")
    fig.update_layout(yaxis_title="金额（元）", xaxis_title="分类")
    st.plotly_chart(fig)

    # 统计表：分类 / 笔数 / 金额合计 / 占比
    show_df = df.copy()
    show_df["金额合计"] = show_df["金额合计"].apply(lambda x: f"¥{x:,.2f}")
    show_df["占比"] = show_df["占比"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(show_df, hide_index=True)
