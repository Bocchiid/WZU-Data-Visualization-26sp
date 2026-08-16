import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ======================
# 页面配置
# ======================
st.set_page_config(
    page_title="Tufte可视化迭代改进实验",
    page_icon="📊",
    layout="wide"
)

# ======================
# 构造实验数据
# ======================
years = np.arange(1970, 2012)
np.random.seed(42)

bio = 29 + 33 * (1 - np.exp(-(years - 1970)/12))
cs  = 14 + 23 * np.exp(-((years - 1983)/11)**2)
eng = np.clip(1 + 0.45*(years - 1970), 0, 20)
math= 38 + 10 * np.tanh((years - 1980)/16)
phys= 14 + 27 * (1 - np.exp(-(years - 1970)/20))

df_original = pd.DataFrame({
    'year': years,
    'Biology': np.clip(bio, 0, 85),
    'Computer Science': np.clip(cs, 0, 38),
    'Engineering': np.clip(eng, 0, 20),
    'Math and Statistics': np.clip(math, 0, 50),
    'Physical Sciences': np.clip(phys, 0, 45)
})

# ======================
# 标题
# ======================
st.title("📊 Tufte可视化原则迭代实验")
st.subheader("1970–2011 年美国STEM领域女性学士学位占比")
st.markdown("---")

# ======================
# 侧边栏：Tufte 原则
# ======================
with st.sidebar.expander("📏 Tufte六大可视化原则", expanded=True):
    st.markdown("""
1. **不歪曲数据**：坐标轴真实，不误导
2. **最大化数据墨水比**：少装饰，多信息
3. **清除非数据墨水**：去掉多余框线、网格
4. **多功能图形元素**：一条线同时表示趋势+类别
5. **提高数据密度**：直接标注关键趋势、参考线
6. **清晰完整标注**：标题、单位、来源清晰
""")

# ======================
# 任务2 新增交互筛选功能
# ======================
# 1. 年份范围筛选
min_year, max_year = int(df_original['year'].min()), int(df_original['year'].max())
year_range = st.sidebar.slider(
    "📅 选择年份范围",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# 2. 学科多选框筛选
all_fields = ['Biology','Computer Science','Engineering','Math and Statistics','Physical Sciences']
selected_fields = st.sidebar.multiselect(
    "📚 选择要展示的学科",
    options=all_fields,
    default=all_fields
)

# 筛选后数据
df = df_original[(df_original['year'] >= year_range[0]) & (df_original['year'] <= year_range[1])]


st.sidebar.markdown("---")
st.sidebar.markdown("## 🔧 自主优化控制面板")

# ----------------------
# 样式开关
# ----------------------
show_grid      = st.sidebar.checkbox("显示背景网格", value=True)
show_frame     = st.sidebar.checkbox("显示完整四周边框", value=True)
show_legend    = st.sidebar.checkbox("显示传统图例", value=True)
direct_label   = st.sidebar.checkbox("线条末端直接标注学科名", value=False)
add_50line     = st.sidebar.checkbox("添加50%性别平等参考线", value=False)
add_key_annotations = st.sidebar.checkbox("添加关键趋势标注", value=False)
simplify_colors= st.sidebar.checkbox("使用简约专业配色", value=False)

# ----------------------
# 专业配色方案（ColorBrewer）
# ----------------------
palette = None
if simplify_colors:
    palette = st.sidebar.radio(
        "🎨 选择 ColorBrewer 配色方案",
        options=[
            "Set2 (柔和清爽)",
            "Dark2 (高对比专业)",
            "Paired (成对区分)",
            "Greys (黑白灰度)"
        ],
        index=0
    )

clean_ticks    = st.sidebar.checkbox("精简坐标轴刻度", value=False)
add_title_note = st.sidebar.checkbox("添加完整标题与说明", value=False)

# ----------------------
# 标题对齐：主标题 + 副标题 独立控制
# ----------------------
st.sidebar.markdown("### 🎯 标题位置")
title_align = st.sidebar.radio(
    "主标题对齐",
    options=["左上", "居中", "右上"],
    index=1
)

subtitle_align = st.sidebar.radio(
    "副标题对齐",
    options=["左上", "居中", "右上"],
    index=1
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🎯 标注位置微调（避免遮挡）")

text_bio_y    = st.sidebar.slider("Biology标注Y位置", 50, 75, 65)
text_cs_xy    = st.sidebar.slider("CS标注X偏移（年）", 1975, 2000, 1990)
text_cs_y     = st.sidebar.slider("CS标注Y位置", 35, 55, 45)
text_50pct_y  = st.sidebar.slider("50%文字Y位置", 48, 52, 50)

# ======================
# 配色逻辑
# ======================
def get_palette(palette_name):
    if palette_name == "Set2 (柔和清爽)":
        return ["#66c2a5","#fc8d62","#8da0cb","#e78ac3","#a6d854"]
    elif palette_name == "Dark2 (高对比专业)":
        return ["#1b9e77","#d95f02","#7570b3","#e7298a","#66a61e"]
    elif palette_name == "Paired (成对区分)":
        return ["#a6cee3","#1f78b4","#b2df8a","#33a02c","#fb9a99"]
    elif palette_name == "Greys (黑白灰度)":
        return ["#252525","#525252","#737373","#969696","#bdbdbd"]
    else:
        return ['#9467bd','#1f77b4','#ff7f0e','#2ca02c','#d62728']

if simplify_colors and palette:
    colors_list = get_palette(palette)
    colors = dict(zip(all_fields, colors_list))
else:
    colors = {
        'Biology': '#9467bd',
        'Computer Science': '#1f77b4',
        'Engineering': '#ff7f0e',
        'Math and Statistics': '#2ca02c',
        'Physical Sciences': '#d62728'
    }

# ======================
# 任务2：统计面板
# ======================
st.markdown("## 📊 筛选后数据统计面板")
if selected_fields and not df.empty:
    stat_df = pd.DataFrame({
        "学科": selected_fields,
        "均值(%)": [round(df[col].mean(),2) for col in selected_fields],
        "最大值(%)": [df[col].max() for col in selected_fields],
        "最小值(%)": [df[col].min() for col in selected_fields]
    })
    st.dataframe(stat_df, use_container_width=True)
else:
    st.info("请至少选择一个学科 + 有效年份范围")


# ======================
# 绘图
# ======================
st.markdown("## 🎨 你的迭代优化图表")
fig, ax = plt.subplots(figsize=(12, 7))

for field in selected_fields:
    ax.plot(df.year, df[field], label=field, color=colors[field], linewidth=2.5)

# 样式优化
if not show_grid:
    ax.grid(False)
if not show_frame:
    ax.spines[['top', 'right']].set_visible(False)
if clean_ticks:
    ax.tick_params(axis='both', length=0)

# 50% 参考线
if add_50line:
    ax.axhline(50, color='lightgray', linestyle='--', linewidth=1.5, alpha=0.8)
    ax.text(1970, text_50pct_y, ' 50% Equality', va='center', fontsize=10, color='gray')

# ======================
# 显示图例
# ======================
if direct_label:
    last_year = df['year'].iloc[-1]
    for field in selected_fields:
        y_val = df[field].iloc[-1]
        ax.text(last_year + 0.5, y_val, field, fontsize=12, va='center', 
                color=colors[field], fontweight='bold')
    # show_legend = False

# ======================
# 关键标注（安全版，不崩溃）
# ======================
if add_key_annotations:
    if 1987 in df['year'].values and 'Biology' in selected_fields:
        bio_1987 = df[df['year'] == 1987]['Biology'].values[0]
        ax.annotate(
            'Biology crosses 50% in 1987',
            xy=(1987, bio_1987),
            xytext=(1982, text_bio_y),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
            fontsize=11
        )

    if 1983 in df['year'].values and 'Computer Science' in selected_fields:
        cs_1983 = df[df['year'] == 1983]['Computer Science'].values[0]
        ax.annotate(
            'Computer Science peaks in 1983\nand then declines',
            xy=(1983, cs_1983),
            xytext=(text_cs_xy, text_cs_y),
            arrowprops=dict(arrowstyle='->', lw=1.5, color='black'),
            fontsize=11
        )

ax.set_ylim(0, 100)
ax.set_xlim(1970, 2015)

# ======================
# 标题：主标题 + 副标题 分别对齐
# ======================
if add_title_note:
    main_title = "Percentage of Degrees Awarded to Women (1970–2011)"
    subtitle = "Biology Surpasses 50% While CS and Engineering Lag"

    if title_align == "左上":
        ax.text(1972, 99, main_title, fontsize=16, fontweight='bold', ha='left')
    elif title_align == "居中":
        ax.text(1992, 99, main_title, fontsize=16, fontweight='bold', ha='center')
    else:
        ax.text(2011, 99, main_title, fontsize=16, fontweight='bold', ha='right')

    if subtitle_align == "左上":
        ax.text(1972, 93, subtitle, fontsize=12, color="#444", ha='left')
    elif subtitle_align == "居中":
        ax.text(1992, 93, subtitle, fontsize=12, color="#444", ha='center')
    else:
        ax.text(2011, 93, subtitle, fontsize=12, color="#444", ha='right')

    ax.set_ylabel("Percentage of Degrees (%)", fontsize=12)

else:
    default_title = "Women's Bachelor's Degrees in STEM (1970-2011)"
    if title_align == "左上":
        ax.text(1972, 99, default_title, fontsize=14, fontweight='bold', ha='left')
    elif title_align == "居中":
        ax.text(1992, 99, default_title, fontsize=14, fontweight='bold', ha='center')
    else:
        ax.text(2011, 99, default_title, fontsize=14, fontweight='bold', ha='right')
    ax.set_ylabel("Percentage (%)", fontsize=12)

ax.set_xlabel("Year", fontsize=12, labelpad=15)

if show_legend:
    ax.legend(loc='upper left', fontsize=11)

st.pyplot(fig)

# ======================
# Tufte 原则评价
# ======================
st.markdown("---")
st.markdown("## 📝 当前设计符合Tufte原则评价")
with st.expander("点击查看评价", expanded=True):
    rule1 = "✅ 不歪曲数据"
    rule2 = "✅ 数据墨水比最大化" if not show_grid and not show_frame else "❌ 数据墨水比偏低"
    rule3 = "✅ 已清除非数据墨水" if not show_frame else "❌ 仍有多余边框等非数据墨水"
    rule4 = "✅ 多功能图形元素" if direct_label else "❌ 图例分离，信息效率低"
    rule5 = "✅ 数据密度高（含关键标注）" if (direct_label and add_50line and add_key_annotations) else "❌ 数据密度不足"
    rule6 = "✅ 标注完整清晰" if add_title_note else "❌ 标题与说明不够完整"

    st.markdown(rule1)
    st.markdown(rule2)
    st.markdown(rule3)
    st.markdown(rule4)
    st.markdown(rule5)
    st.markdown(rule6)

st.caption("基于Edward Tufte可视化原则设计 | 数据：1970–2011美国STEM女性学位占比 | 配色来自 ColorBrewer")