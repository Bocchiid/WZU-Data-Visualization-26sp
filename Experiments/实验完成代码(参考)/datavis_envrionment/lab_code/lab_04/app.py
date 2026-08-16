import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# 设置页面配置
st.set_page_config(page_title="Gapminder数据可视化仪表板", layout="wide")

# 加载内置数据集
df = px.data.gapminder()

# 侧边栏设置
page = st.sidebar.selectbox("选择页面", ["动画分析", "人口数据可视化分析", "人均GDP和预期寿命关系分析"])
st.sidebar.write("数据来源：Gapminder 数据集")
st.sidebar.write("作者：24211835201 韩贤煜")

if page == "动画分析":
    # (1) 用动画散点图分析人均GDP与预期寿命的关系
    st.title("Gapminder 数据可视化仪表板")
    st.subheader("人均GDP与预期寿命关系")
    fig = px.scatter(
        df, 
        x='gdpPercap', 
        y='lifeExp', 
        color='continent',
        size='pop', 
        log_x=True, 
        animation_frame='year', 
        animation_group='country', 
        labels={"gdpPercap": "人均GDP", "lifeExp": "预期寿命", "continent": "大洲", "pop": "人口", "year": "年份"},
    )
    st.plotly_chart(fig, use_container_width=True)
elif page == "人口数据可视化分析":
    opts = ["分组条形图", "堆叠柱状图", "折线图", "面积图", "大洲", "国家和地区"]
    
    if 'chart_type' not in st.session_state:
        st.session_state.chart_type = opts[0]

    if st.session_state.chart_type in ["分组条形图", "堆叠柱状图", "折线图"]:
        st.subheader("各大洲人口随时间变化")
    elif st.session_state.chart_type == "面积图":
        st.subheader("各大洲人口比例随时间的变化")
    else:
        st.subheader("2007年的各大洲人口比例")

    # 显示选择框
    chart_type = st.selectbox("选择图表类型", opts, key="chart_type")

    # (2) 可视化各大洲人口数量随时间的变化
    # 根据指导书，数量分析主要使用分组条形图
    if chart_type == "分组条形图":
        df_pop_continent_over_t = df.groupby(['year', 'continent'], as_index=False).agg({'pop': 'sum'})
        fig = px.bar(df_pop_continent_over_t, 
                    x='year', y='pop', color='continent', 
                    barmode='group', 
                    labels={"year":"", "pop": "人口", "continent": ""})
        st.plotly_chart(fig, use_container_width=True)

    # (3) 可视化人口比例随时间的变化
    elif chart_type in ["堆叠柱状图", "面积图", "折线图"]:
        # 步骤1: 计算每年全球总人口
        global_pop = df.groupby('year')['pop'].sum().reset_index()
        # 步骤2: 计算每个大洲每年总人口
        continent_pop = df.groupby(['year', 'continent'])['pop'].sum().reset_index()
        # 步骤3: 合并数据并计算比例
        pop_with_ratio = pd.merge(continent_pop, global_pop, on='year', suffixes=('_continent', '_global'))
        pop_with_ratio['ratio'] = pop_with_ratio['pop_continent'] / pop_with_ratio['pop_global']
        
        if chart_type == "堆叠柱状图":
            fig = px.bar(pop_with_ratio, x="year", y="ratio", color="continent", 
                         labels={"year":"", "ratio": "人口比例", "continent": ""})
        elif chart_type == "面积图":
            fig = px.area(pop_with_ratio, x="year", y="ratio", color="continent", 
                          labels={"year":"", "ratio": "人口比例", "continent": ""})
        elif chart_type == "折线图":
            fig = px.line(pop_with_ratio, x="year", y="ratio", color="continent", 
                          labels={"year":"", "ratio": "人口比例", "continent": ""})
        st.plotly_chart(fig, use_container_width=True)

    # (4) 利用甜甜圈图和太阳爆炸图可视化2007年人口比例
    else:
        # 筛选2007年数据并计算大洲总和
        continent_2007 = df[df['year'] == 2007].groupby('continent')['pop'].sum().reset_index()
        if chart_type == "大洲":
            fig = px.pie(continent_2007, values='pop', names='continent', hole=0.68,
                         labels={"pop": "人口", "continent": ""})
        elif chart_type == "国家和地区":
            fig = px.sunburst(df[df['year'] == 2007], path=['continent', 'country'], values='pop', 
                              color='lifeExp', color_continuous_scale='RdBu',
                              labels={"pop": "人口", "continent": "", "lifeExp": "预期寿命"})
        st.plotly_chart(fig, use_container_width=True)
elif page == "人均GDP和预期寿命关系分析":
    st.subheader("2007年人均GDP与预期寿命的关系（按大洲分列, 带回归线）")
    
    # (5) 按大洲绘制分面图，并画出回归线
    fig = px.scatter(
        df.query("year == 2007"), 
        x="gdpPercap", 
        y="lifeExp", 
        color="continent", 
        trendline="ols", 
        trendline_options=dict(log_x=True), 
        facet_col="continent", 
        trendline_color_override="black",
        hover_data=['country'],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("2007年人均GDP与预期寿命的关系（带回归线）")

    # (6) 利用散点图可视化特定年份人均GDP与预期寿命的关系（整体趋势线）
    fig = px.scatter(
        df.query("year == 2007"), 
        x="gdpPercap", 
        y="lifeExp", 
        color="continent", 
        trendline="ols", 
        trendline_options=dict(log_x=True), 
        trendline_scope="overall", # 设置回归线范围为全局
        trendline_color_override="black", 
        hover_data=['country'],
    )
    st.plotly_chart(fig, use_container_width=True)