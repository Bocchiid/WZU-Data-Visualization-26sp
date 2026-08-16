import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 设置matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(page_title="跨媒体数据可视化", layout="wide")
st.title("跨媒体数据可视化")
st.markdown("---")

# 1. 数据预处理
@st.cache_data
def load_data():
    df = pd.read_csv("data/system_logs.csv")
    
    # 数据清洗(去除无关字段和空值)
    df = df.dropna(subset=['timestamp', 'level', 'message'])
    
    # 将时间戳转换为datetime格式
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 提取日期与小时特征方便后续分析
    df['date'] = df['timestamp'].dt.date
    df['hour'] = df['timestamp'].dt.hour
    
    return df

# 加载数据
df_raw = load_data()

# 3.3. 交互式面板
st.sidebar.header("交互式筛选面板")

# 1. 时间范围筛选
min_date, max_date = df_raw['date'].min(), df_raw['date'].max()
start_date, end_date = st.sidebar.date_input("选择时间范围:", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# 2. 日志级别筛选
all_levels = df_raw['level'].unique().tolist()
selected_levels = st.sidebar.multiselect("选择日志级别:", options=all_levels, default=all_levels)

# 3. 用户筛选
all_users = df_raw['user'].unique().tolist()
selected_users = st.sidebar.multiselect("选择用户:", options=all_users, default=all_users)

# 执行过滤
mask = (
    (df_raw['date'] >= start_date) & 
    (df_raw['date'] <= end_date) & 
    (df_raw['level'].isin(selected_levels)) & 
    (df_raw['user'].isin(selected_users))
)
df_filtered = df_raw[mask]

# 统计整体信息
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric("日志总数", f"{len(df_filtered)}条")
with kpi2:
    err_cnt = len(df_filtered[df_filtered['level'] == 'ERROR'])
    st.metric("ERROR数量", f"{err_cnt}条")
with kpi3:
    st.metric("活跃用户数", f"{df_filtered['user'].nunique()}个")

st.markdown("---")

# 2.1. 3.2. 统计不同日志级别的事件数量和统计图表展示
col1, col2 = st.columns(2)

with col1:
    st.write("### 日志级别分布(饼图)")
    level_counts = df_filtered['level'].value_counts()
    if not level_counts.empty:
        sub_col1, sub_col2 = st.columns([2, 3])
        
        with sub_col1:
            st.write("#### 事件数量统计")
            df_counts = level_counts.reset_index()
            df_counts.columns = ['日志级别', '事件数量']
            st.dataframe(df_counts, use_container_width=True, hide_index=True)
            
            st.caption(f"共计{level_counts.sum()}个级别事件")
            
        with sub_col2:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.pie(level_counts, labels=level_counts.index, autopct='%1.1f%%', startangle=90, explode=[0.02]*len(level_counts))
            ax.axis('equal')
            st.pyplot(fig)
    else:
        st.info("暂无数据")

# 2.2. 分析日志事件的时间分布
with col2:
    st.write("### 24小时日志时间分布(柱状图)")
    hour_counts = df_filtered['hour'].value_counts().reindex(range(0, 24), fill_value=0)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(hour_counts.index, hour_counts.values, color='#4682B4')
    ax.set_xlabel("小时(24H)")
    ax.set_ylabel("事件数量")
    ax.set_xticks(range(0, 24, 4))
    st.pyplot(fig)

st.markdown("---")

# 2.3. 提取常见错误和警告信息
st.write("### 常见错误与警告排行(Top 5)")
err_df = df_filtered[df_filtered['level'].isin(['ERROR', 'WARNING'])]
if not err_df.empty:
    top_err = err_df['message'].value_counts().head(5).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10, 3.5))
    top_err.plot(kind='barh', color='#E15759', ax=ax)
    ax.set_xlabel("出现频次")
    st.pyplot(fig)
else:
    st.info("当前筛选范围内无错误或警告日志")

st.markdown("---")

# 3.4. 详细数据明细表格
st.write("### 详细日志明细数据")
st.dataframe(df_filtered[['timestamp', 'level', 'source', 'user', 'message']].sort_values(by='timestamp', ascending=False), use_container_width=True)