import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --------------------------
# 任务1：数据读取与基础探索
# --------------------------
st.title("📊数据基础与交互式可视化实验")
st.subheader("任务1：数据读取与基础探索")
st.subheader("1.1 原始数据预览")

# 1. 读取数据
df = pd.read_csv('data/penguins.csv')
# 2. 展示前 5 行
st.dataframe(df.head())

st.subheader("1.2 数据集基本信息")
# 3. 查看信息
# st.write("数据形状：", df.shape)

shape = df.shape
st.write("数据集行数：", shape[0])
st.write("数据集列数：", shape[1])

# st.write("列名：", list(df.columns))

st.write("列名：[", ", ".join(f"'{col}'" for col in df.columns) + "]")
# 4. 删除缺失值

st.subheader("1.3 缺失值处理")

# 1. 统计处理前各列缺失值数量
missing_counts = df.isnull().sum()
st.write("处理前缺失值数量：")
# 用 dataframe 展示，转成 DataFrame 更美观，和截图格式一致
st.dataframe(missing_counts.rename("0"), use_container_width=True)

df = df.dropna()
st.write("删除缺失值后形状：", df.shape)

# --------------------------
# 任务2：数据类型判定练习
# --------------------------
st.subheader("任务2：数据类型判定练习")

# 定义分类列 & 数值列
cat_cols = ['species', 'island', 'sex']
num_cols = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']

# --------------------------
# 任务3：交互式筛选
# --------------------------
st.subheader("任务3：交互式数据筛选")
st.sidebar.header("🔍 筛选面板")

species_options = ["All"] + list(df['species'].unique())
sex_options = ["All"] + list(df['sex'].unique())

species_choice = st.sidebar.selectbox("选择企鹅种类", species_options)
sex_choice = st.sidebar.selectbox("选择性别", sex_options)

# 筛选逻辑
filtered_df = df.copy()

if species_choice != "All":
    filtered_df = filtered_df[filtered_df['species'] == species_choice]

if sex_choice != "All":
    filtered_df = filtered_df[filtered_df['sex'] == sex_choice]

st.subheader("筛选后的数据")
st.dataframe(filtered_df, use_container_width=True)

# --------------------------
# 任务4：多类型交互式统计图表
# --------------------------

st.subheader("任务4：多类型交互式统计图表")

chart_type = st.selectbox("选择图表类型", [
    "散点图", "柱状图", "直方图", "箱线图"
])
# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))

# 散点图
if chart_type == "散点图":
    x = st.selectbox("X轴（定量）", num_cols, index=2)
    y = st.selectbox("Y轴（定量）", num_cols, index=3)
    sns.scatterplot(data=filtered_df, x=x, y=y, hue='species', s=100, ax=ax)
    ax.set_title(f"Scatterplot: {x} vs {y}")
# 柱状图
elif chart_type == "柱状图":
    x = st.selectbox("分类字段", cat_cols)
    y = st.selectbox("数值字段", num_cols)
    sns.barplot(data=filtered_df, x=x, y=y, ax=ax)
    ax.set_title(f"bar: {x} → {y}")
# 直方图
elif chart_type == "直方图":
    x = st.selectbox("数值变量", num_cols)
    sns.histplot(data=filtered_df, x=x, kde=True, ax=ax)
    ax.set_title(f"histogram: {x} distribution")
# 箱线图
elif chart_type == "箱线图":
    x = st.selectbox("分类字段", cat_cols)
    y = st.selectbox("数值变量", num_cols)
    sns.boxplot(data=filtered_df, x=x, y=y, ax=ax)
    ax.set_title(f"boxplot: {x} group → {y} distribution")
plt.tight_layout()
st.pyplot(fig)

# --------------------------
# 任务5：数据统计面板
# --------------------------
st.subheader("任务5：数据统计指标")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("平均体重(g)", round(filtered_df["body_mass_g"].mean(), 2))
with col2:
    # 请补充代码展示喙长最大值、最小值
    st.metric("喙长最大值", filtered_df["bill_length_mm"].max())
with col3:
    st.metric("喙长最小值", filtered_df["bill_length_mm"].min())
with col4:
    st.metric("样本数量", len(filtered_df))


# col1, col2, col3 = st.columns(3)

# with col1:
#     st.metric("平均体重(g)", round(filtered_df["body_mass_g"].mean(), 2))
# with col2:
#     # 请补充代码展示喙长最大值、最小值
#     st.metric("喙长最大值", filtered_df["bill_length_mm"].max())
#     st.metric("喙长最小值", filtered_df["bill_length_mm"].min())
# with col3:
#     st.metric("样本数量", len(filtered_df))
