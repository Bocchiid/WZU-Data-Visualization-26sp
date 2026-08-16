import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from statsmodels.graphics.mosaicplot import mosaic

# 设置Matplotlib支持中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 1. 数据准备与加载
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, sep=';')
    return data

try:
    df = load_data("data/winequality-red.csv")
except Exception as e:
    st.error(f"数据加载失败: {e}")

st.title("高维非空间数据可视化")
st.markdown("---")

# 2. 数据预处理
st.header("一、数据预处理与探索性分析(EDA)")

# 检查缺失值
missing_values = df.isnull().sum().sum()

if missing_values > 0:
    df = df.fillna(df.mean(numeric_only=True))
else:
    pass

st.subheader("数据集概览(前10行)")
st.dataframe(df.head(10), use_container_width=True)

st.subheader("基本统计信息与缺失值检查")
st.write(f"数据集维度: {df.shape[0]} 行, {df.shape[1]} 列")
st.write(f"数据集中的缺失值总数: **{missing_values}**")

# 简易离散化：为了马赛克图, 将品质分为低、中、高三档
df['quality_level'] = pd.cut(df['quality'], bins=[0, 4, 6, 10], labels=['低品质(<=4)', '中品质(5-6)', '高品质(>=7)'])

# 数据标准化(不含目标变量quality和离散化的quality_level)
features = df.columns[:-2].tolist() # 11个特征维度
scaler = StandardScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
df_scaled['quality'] = df['quality']
df_scaled['quality_level'] = df['quality_level']

# 4. 交互功能控件(Streamlit Sidebar)
st.sidebar.header("交互式控件面板")

# 维度选择器
selected_features = st.sidebar.multiselect(
    "1. 选择参与可视化的特征维度 (至少选2个)", 
    options=features, 
    default=features[:4]
)

# 颜色映射选项
cmap_option = st.sidebar.selectbox(
    "2. 选择热力图/像素图颜色映射 (Colormap)", 
    options=['viridis', 'plasma', 'coolwarm', 'inferno']
)

# 数据过滤滑块(基于酒精含量过滤)
alcohol_min, alcohol_max = float(df['alcohol'].min()), float(df['alcohol'].max())
selected_alcohol_range = st.sidebar.slider(
    "3. 数据过滤：选择酒精含量范围",
    min_value=alcohol_min, max_value=alcohol_max,
    value=(alcohol_min, alcohol_max)
)

# 根据滑块过滤数据
df_filtered = df[(df['alcohol'] >= selected_alcohol_range[0]) & (df['alcohol'] <= selected_alcohol_range[1])]
df_scaled_filtered = df_scaled[(df['alcohol'] >= selected_alcohol_range[0]) & (df['alcohol'] <= selected_alcohol_range[1])]

st.markdown("---")

# 3. 高维非空间数据可视化
st.header("二、高维非空间数据可视化")

tab1, tab2, tab3, tab4 = st.tabs(["散点图矩阵", "平行坐标图", "像素图", "马赛克图"])

with tab1:
    st.subheader("1. 散点图矩阵 (Scatterplot Matrix)")
    st.caption("展示所选属性之间的两两关系，用颜色区分不同的品质等级")
    if len(selected_features) >= 2:
        fig_pair = sns.pairplot(df_filtered[selected_features + ['quality_level']], hue='quality_level', palette='Set2')
        st.pyplot(fig_pair.fig)
    else:
        st.warning("请在左侧侧边栏至少选择2个特征维度")

with tab2:
    st.subheader("2. 平行坐标图 (Parallel Coordinates)")
    st.caption("交互式平行坐标图：展示所有属性在不同品质葡萄酒中的分布支持拖动轴及框选缩放")
    fig_parallel = px.parallel_coordinates(
        df_filtered, 
        dimensions=features, 
        color="quality",
        color_continuous_scale=px.colors.sequential.Viridis,
        title="葡萄酒属性平行坐标图"
    )
    st.plotly_chart(fig_parallel, use_container_width=True)

with tab3:
    st.subheader("3. 像素图 (Pixel-oriented Visualization)")
    st.caption("将数据按品质评分从低到高排序，每个标准化后的维度映射为颜色强度")
    
    df_pixel_sort = df_scaled_filtered.sort_values(by='quality')
    
    fig_pixel, ax_pixel = plt.subplots(figsize=(12, 6)) # 稍微加宽画布以适应单列大屏
    im = ax_pixel.imshow(df_pixel_sort[features].T, aspect='auto', cmap=cmap_option)
    ax_pixel.set_yticks(range(len(features)))
    ax_pixel.set_yticklabels(features)
    ax_pixel.set_xlabel("样本点(按品质从低到高排序)")
    fig_pixel.colorbar(im, ax=ax_pixel, orientation='horizontal', label='标准化特征强度')
    st.pyplot(fig_pixel)

with tab4:
    st.subheader("4. 马赛克图(Mosaic Plot)")
    st.caption("展示分类变量(品质等级)与离散化后的酒精含量(高/低酒精)之间的交叉分布关系")
    
    df_mosaic = df_filtered.copy()
    df_mosaic['酒精含量分档'] = pd.qcut(df_mosaic['alcohol'], q=2, labels=['低酒精', '高酒精'])
    
    fig_mosaic, _ = plt.subplots(figsize=(12, 6))
    mosaic(df_mosaic, ['quality_level', '酒精含量分档'], title="品质等级与酒精含量交叉分布马赛克图", ax=fig_mosaic.gca())
    st.pyplot(fig_mosaic)

st.markdown("---")

# 5. 主成分分析(PCA)降维
st.header("三、主成分分析(PCA)降维分析")

# 执行PCA
pca = PCA(n_components=2)
pca_data = pca.fit_transform(df_scaled[features])
df_pca = pd.DataFrame(pca_data, columns=['PC1', 'PC2'])
df_pca['quality'] = df['quality']

# 解释方差比例
explained_variance = pca.explained_variance_ratio_

st.subheader("1. 2D主成分散点图")
fig_pca = px.scatter(
    df_pca, x='PC1', y='PC2', 
    color='quality',
    color_continuous_scale=px.colors.sequential.thermal,
    labels={
        'PC1': f'主成分1(解释方差: {explained_variance[0]:.2%})',
        'PC2': f'主成分2(解释方差: {explained_variance[1]:.2%})'
    },
    title="PCA 降维可视化"
)
st.plotly_chart(fig_pca, use_container_width=True)

st.subheader("2. 主成分载荷分析(Loadings)")
loadings = pd.DataFrame(
    pca.components_.T, 
    columns=['PC1载荷', 'PC2载荷'], 
    index=features
)

st.dataframe(loadings.style.background_gradient(cmap='coolwarm', axis=0), use_container_width=True)

st.markdown(f"""
**方差解释总结：**
* 主成分1(PC1)解释了{explained_variance[0]:.2%}的方差
* 主成分2(PC2)解释了{explained_variance[1]:.2%}的方差
* 两个主成分累计解释了{(explained_variance[0]+explained_variance[1]):.2%}的高维特征信息
""")

st.subheader("3. 主成分实际物理意义解释")
st.markdown("""
根据上方的**主成分载荷矩阵**，我们可以得出以下实际意义：
1. **PC1(主成分1):**在`fixed acidity`(固定酸度)、`citric acid`(柠檬酸)上有较高的**正载荷**，而在`pH`上有极高的**负载荷**这完全符合化学规律(酸度越高, pH越低)因此，**PC1主要代表了葡萄酒的"酸度特征"**
2. **PC2(主成分2):**在`free sulfur dioxide`(游离二氧化硫)和`total sulfur dioxide`(总二氧化硫) 上有极高的**正载荷**因此，**PC2主要代表了葡萄酒的"二氧化硫(防腐剂/抗氧化剂)含量特征"**
""")