import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import numpy as np

# 0.5 准备实验数据
data = {
    "公司": {
        "技术部": {
            "开发组": 25,
            "测试组": 15,
            "运维组": 10
        },
        "市场部": {
            "销售组": 20,
            "营销组": 12,
            "客服组": 8
        },
        "人事部": {
            "招聘组": 5,
            "培训组": 5,
            "薪酬组": 4
        }
    }
}

# 1. 构建图结构
def create_graph(d, parent=None, G=None):
    if G is None:
        G = nx.DiGraph()  # 有向图
    
    for key, value in d.items():
        # 部门或公司节点
        if isinstance(value, dict):
            G.add_node(key, is_leaf=False, type="internal")
            if parent:
                G.add_edge(parent, key)
            
            # 递归调用自身处理子节点
            create_graph(value, parent=key, G=G)
            
            # 计算当前节点的总人数(所有子节点大小的总和)
            total_size = sum(G.nodes[child]['size'] for child in G.successors(key))
            G.nodes[key]['size'] = total_size
        # 小组节点
        else:
            G.add_node(key, size=value, is_leaf=True, type="leaf")
            if parent:
                G.add_edge(parent, key)
                
    return G

# 初始化图
G = create_graph(data)

# 标记公司顶层节点的类型以便区分颜色
G.nodes["公司"]["type"] = "root"

# 3.1. 页面配置
st.set_page_config(layout="wide", page_title="层次数据可视化")
st.title("层次及网络数据可视化")

# 3.2.
st.sidebar.header("数据概览(JSON)")
st.sidebar.json(data) 

# 3.3.
st.sidebar.markdown("---")
st.sidebar.subheader("配置参数说明")
st.sidebar.write("- **节点大小**：基于人数对数缩放\n- **层级颜色**：金/蓝/绿区分\n- **交互**：支持滚轮缩放与悬停")

# 2.1. 计算节点布局
try:
    # 优先使用dot布局
    pos = nx.drawing.nx_pydot.graphviz_layout(G, prog='dot')
except (ImportError, Exception):
    # 如果未安装graphviz，降级使用spring布局
    pos = nx.spring_layout(G, seed=42)

# 2.2. 准备边数据
edge_x = []
edge_y = []
for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]
    edge_x.extend([x0, x1, None])  
    edge_y.extend([y0, y1, None])

# 2.3. 准备节点数据
node_x = []
node_y = []
node_text = []      
node_hover = []     
node_size = []      
node_color = []     

# 设置层级颜色映射
color_map = {
    "root": "#FFD700",       
    "internal": "#1F77B4",   
    "leaf": "#2CA02C"        
}

# 2.6. 添加交互功能(悬停显示详细信息)
for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)
    
    size_val = G.nodes[node]['size']
    # 对数缩放控制节点大小
    scaled_size = np.log1p(size_val) * 12 + 10
    node_size.append(scaled_size)
    
    # 填充颜色
    node_color.append(color_map[G.nodes[node]['type']])
    
    # 标签内容
    node_text.append(f"{node}<br>{size_val}人")
    # 悬停详细信息
    node_hover.append(f"节点名称: {node}<br>总人数: {size_val}人<br>类型: {G.nodes[node]['type']}")

# 2.4. 绘制边
edge_trace = go.Scatter(
    x=edge_x, y=edge_y,
    line=dict(width=1.5, color='#888'),
    hoverinfo='none',
    mode='lines'
)

# 2.5. 绘制节点
node_trace = go.Scatter(
    x=node_x, y=node_y,
    mode='markers+text', 
    text=node_text,
    textposition="middle center", 
    textfont=dict(color='black', size=10), 
    hoverinfo='text',
    hovertext=node_hover, 
    marker=dict(
        showscale=False,
        color=node_color,
        size=node_size,
        line_width=2,
        line_color='white'
    )
)

# 2.7. 组装Figure并渲染
fig = go.Figure(data=[edge_trace, node_trace])

fig.update_layout(
    title=dict(
        text='<b>公司组织架构层次图</b>',
        font=dict(size=16)
    ),
    showlegend=False,
    hovermode='closest',
    dragmode='pan', # 拖拽模式改成平移
    margin=dict(b=20, l=5, r=5, t=40),
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), 
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    plot_bgcolor='rgba(245,245,245,1)', 
    height=650 
)

# 在Streamlit中展示，并开启鼠标滚轮缩放功能
st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})