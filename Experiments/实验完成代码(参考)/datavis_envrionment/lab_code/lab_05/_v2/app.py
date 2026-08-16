import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd

BAIDU_MAP_API_KEY = "VWfMAe0ku1Jc4avSTYhosllU9ZfamZKc" 

# 2. 调用百度地图API获取公共设施数据
def get_poi_data(city, keyword, ak):
    url = "http://api.map.baidu.com/place/v2/search"
    params = {
        "query": keyword,
        "region": city,
        "output": "json",
        "ak": ak,
        "scope": 2,
        "page_size": 20,
        "page_num": 0
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "results" in data:
        return data["results"]
    else:
        print(f"获取数据失败：{data.get('message', '未知错误')}")
        return None

# 3. 使用Folium生成地图
def create_map(poi_data):
    # 默认以北京为中心点
    map_center = [39.9042, 116.4074]  
    zoom_start = 12 
    
    if poi_data and len(poi_data) > 0:
        first_poi = poi_data[0]
        if "location" in first_poi:
            map_center = [first_poi["location"]["lat"], first_poi["location"]["lng"]]
            zoom_start = 13
            
    m = folium.Map(location=map_center, zoom_start=zoom_start)
    
    for poi in poi_data:
        if "location" in poi:
            location = [poi["location"]["lat"], poi["location"]["lng"]]
            
            name = poi.get("name", "未知名称")
            address = poi.get("address", "暂无详细地址")
            
            popup_html = f"""
            <div style="
                font-family: 'Microsoft YaHei', sans-serif; 
                font-size: 13px; 
                min-width: 200px; 
                max-width: 300px;
                line-height: 1.6;
            ">
                <b style="color: #1E88E5; font-size: 14px;">{name}</b><br>
                <span style="color: #555;">📍 <b>地址:</b> {address}</span>
            </div>
            """
            
            popup_obj = folium.Popup(popup_html, max_width=350)
            
            folium.Marker(
                location,
                popup=popup_obj,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
            
    return m

# 1. Streamlit 主界面
def main():
    # 页面配置
    st.set_page_config(page_title="城市公共设施可视化", layout="wide")
    
    st.title("城市公共设施分布可视化系统")
    st.markdown("通过结合**百度地图Web服务API**和**Folium**，实时检索并可视化城市基础设施。")
    st.sidebar.header("🔍 查询条件设置")
    
    if "poi_data" not in st.session_state:
        st.session_state.poi_data = None
    if "current_city" not in st.session_state:
        st.session_state.current_city = ""
    if "current_keyword" not in st.session_state:
        st.session_state.current_keyword = ""

    city = st.sidebar.text_input("请输入城市名称", "北京")
    keyword = st.sidebar.selectbox("请选择公共设施类型", ["学校", "医院", "公园", "餐厅", "酒店", "景点", "购物"])
    
    submit_button = st.sidebar.button("获取并可视化数据")
    
    if submit_button:
        with st.spinner("正在从百度地图开放平台抓取数据..."):
            st.session_state.poi_data = get_poi_data(city, keyword, BAIDU_MAP_API_KEY)
            st.session_state.current_city = city
            st.session_state.current_keyword = keyword

    if st.session_state.poi_data:
        st.success(f"当前展示: {st.session_state.current_city}的{len(st.session_state.poi_data)}个{st.session_state.current_keyword}相关数据点！")
        
        st.subheader("🗺️ 地图可视化展示")
        m = create_map(st.session_state.poi_data)
        st_folium(m, width="100%", height=500, key="my_folium_map")
        
        st.markdown("---")
        
        st.subheader("📊 详细数据列表")
        parsed_list = []
        for item in st.session_state.poi_data:
            parsed_list.append({
                "名称": item.get("name"),
                "地址": item.get("address", "N/A"),
                "纬度": item.get("location", {}).get("lat"),
                "经度": item.get("location", {}).get("lng"),
            })
        df = pd.DataFrame(parsed_list)
        st.dataframe(df, height=350, use_container_width=True)
            
    elif submit_button and not st.session_state.poi_data:
        st.warning("未找到相关兴趣点数据，请检查城市名称输入或更换关键词。")

if __name__ == "__main__":
    main()