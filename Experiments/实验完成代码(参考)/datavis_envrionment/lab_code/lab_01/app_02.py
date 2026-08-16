import streamlit as st
import pandas as pd
import altair as alt

penguins_df = pd.read_csv('data/penguins.csv')
penguins_df = penguins_df.dropna()

st.sidebar.header('筛选条件')

selected_species = st.sidebar.selectbox(
    '选择企鹅物种',
    options=['所有物种'] + list(penguins_df['species'].unique()) # 支持"所有物种"选项
)

feature_options = ['bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g']
selected_x = st.sidebar.selectbox(
    '选择X轴特征',
    options=feature_options,
    index=0 # 默认选择第一个特征
)

selected_y = st.sidebar.selectbox(
    '选择Y轴特征',
    options=feature_options,
    index=0 # 默认选择第一个特征
)

if selected_species != '所有物种':
    filtered_df = penguins_df[penguins_df['species'] == selected_species]
else:
    filtered_df = penguins_df # 选择"所有物种"时不筛选

scatter_chart = (
    alt.Chart(filtered_df, title=f"{selected_species}的{selected_x} vs {selected_y}")
    .mark_circle(size=60, opacity=0.7) # 点大小和透明度
    .encode(
        x=selected_x, # X轴: 用户选择的特征
        y=selected_y, # Y轴: 用户选择的特征
        color='species:N', # 按物种着色(N表示分类变量)
        tooltip=[selected_x, selected_y, 'species'] # hover时显示的信息
    )
    .interactive() # 开启交互(缩放、平移)
    .properties(width=600, height=400) # 图表尺寸
)

st.title('Palmer企鹅数据集探索工具')
st.subheader('交互式散点图分析企鹅特征')
st.write('数据集包含3种企鹅(Adelie、 Gentoo、 Chinstrap)的身体特征数据, 你可以选择要可视化的物种和特征变量, 探索不同企鹅的差异。')

st.altair_chart(scatter_chart, use_container_width=True)