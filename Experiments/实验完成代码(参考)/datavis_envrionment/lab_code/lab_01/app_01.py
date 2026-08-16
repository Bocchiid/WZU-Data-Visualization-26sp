import streamlit as st

st.title('我的第一个Streamlit应用')
st.subheader('Hello Streamlit! 互动体验')

st.write('这是一款基于Streamlit开发的基础互动应用, 可以获取用户输入并动态响应!')

st.text_input('请输入你的姓名')

st.write('请输入你的姓名, 体验互动效果!')