import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import LineString
import json
from streamlit_folium import st_folium

# 1. 页面配置
st.set_page_config(page_title="地理空间数据可视化应用", layout="wide")
st.title("地理空间数据可视化应用")


# 2. 加载数据
@st.cache_data
def load_data(file_path):
    world = gpd.read_file(file_path)
    return world

file_path = "data/ne_10m_admin_0_countries.shp"
world = load_data(file_path)


# 3. 数据处理
if 'GDP_MD' in world.columns and 'POP_EST' in world.columns:
    world["GDP_MD"] = world["GDP_MD"].fillna(0) # 填充GDP缺失值为0
    world["POP_EST"] = world["POP_EST"].fillna(1) # 填充人口缺失值为1，避免除以0
    world["value"] = world["GDP_MD"] / world["POP_EST"]
else:
    st.error("数据中缺少GDP_MD或POP_EST列, 无法计算人均GDP")


# 4. 地图投影
st.sidebar.header("地图配置面板")
projection = st.sidebar.selectbox("选择地图投影坐标系", ["EPSG:4326", "EPSG:3857", "EPSG:3395"])
if projection == "EPSG:4326":
    world = world.to_crs(epsg=4326)
elif projection == "EPSG:3857":
    world = world.to_crs(epsg=3857)
elif projection == "EPSG:3395":
    world = world.to_crs(epsg=3395)


# 5. 点数据可视化
points = gpd.GeoDataFrame(
    {
        "geometry": gpd.points_from_xy(
            [-122.4194, -74.0060, 116.3873, 126.9780],
            [37.7749, 40.7128, 39.9042, 37.5665]
        ),
        "name": ["San Francisco", "New York", "Beijing", "Seoul"],
        "value": [10, 20, 30, 40]
    },
    crs="EPSG:4326"
)
points = points.to_crs(projection)


# 6. 线数据可视化
lines = gpd.GeoDataFrame(
    {
        "geometry": [
            LineString([(-122.4194, 37.7749), (-74.0060, 40.7128)]),
            LineString([(116.3873, 39.9042), (126.9780, 37.5665)])
        ],
        "name": ["SF to NY", "Beijing to Seoul"],
        "value": [15, 25]
    },
    crs="EPSG:4326"
)
lines = lines.to_crs(projection)


# 6.5 创建Folium地图
# Folium底层渲染通常需要基础的经纬度，这里初始化一个基础地图m
m = folium.Map(location=[20, 0], zoom_start=2, tiles="OpenStreetMap")


# 7. 面数据可视化
folium.Choropleth(
    geo_data=world,
    name="choropleth",
    data=world,
    columns=["ISO_A3", "value"],
    key_on="feature.properties.ISO_A3",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="人均GDP",
    highlight=True
).add_to(m)


# 7.5.1 添加点数据到地图
# 将点作为标记添加进地图
for idx, row in points.to_crs("EPSG:4326").iterrows():
    folium.Marker(
        location=[row['geometry'].y, row['geometry'].x],
        popup=f"{row['name']}: {row['value']}"
    ).add_to(m)


# 7.5.2 添加线数据到地图
# 将线作为PolyLine添加进地图
for idx, row in lines.to_crs("EPSG:4326").iterrows():
    folium.PolyLine(
        locations=[(point[1], point[0]) for point in row['geometry'].coords],
        color="blue",
        weight=2,
        opacity=0.6,
        popup=f"{row['name']}: {row['value']}"
    ).add_to(m)


# 8. 地图显示
st_folium(m, width="100%", height=600)