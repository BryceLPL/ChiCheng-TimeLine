import streamlit as st
import pandas as pd
import os
import json
from PIL import Image
import io
from datetime import datetime
import numpy as np
import base64

# 设置页面配置
st.set_page_config(
    page_title="清末历史时间轴 - 赤诚", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 自定义CSS样式
def local_css():
    st.markdown("""
    <style>
    .main {
        padding: 1rem 2rem;
    }
    .stSlider {
        padding-bottom: 1rem;
    }
    .event-box {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .year-display {
        font-size: 30px;
        font-weight: bold;
        text-align: center;
        color: #333;
        padding: 10px;
        background: linear-gradient(90deg, rgba(240,240,240,0) 0%, rgba(240,240,240,1) 50%, rgba(240,240,240,0) 100%);
        margin-bottom: 20px;
    }
    .dynasty-info {
        font-size: 24px;
        color: #555;
        text-align: center;
        margin-bottom: 20px;
    }
    .timeline-title {
        text-align: center;
        margin-bottom: 0;
        font-size: 2rem;
    }
    .timeline-subtitle {
        text-align: center;
        margin-top: 0;
        color: #666;
        font-size: 1rem;
    }
    .reign-label {
        display: inline-block;
        padding: 3px 8px;
        background-color: #e0f7fa;
        border-radius: 15px;
        margin-right: 8px;
        font-size: 14px;
    }
    .timeline-container {
        position: relative;
        padding: 20px 0;
    }
    .timeline-marker {
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: red;
        z-index: 9;
    }
    .image-caption {
        text-align: center;
        font-style: italic;
        color: #666;
        margin-top: 5px;
    }
    .reign-marker {
        text-align: center;
        font-weight: bold;
        margin: 10px 0;
        padding: 5px;
        background-color: #eee;
        border-radius: 5px;
    }
    .reign-divider {
        position: absolute;
        top: -10px;
        bottom: 30px;
        width: 4px;
        background-color: red;
        z-index: 10;
    }
    .reign-zone {
        position: absolute;
        top: 0;
        bottom: 0;
        opacity: 0.1;
        z-index: 7;
    }
    .reign-name {
        position: absolute;
        top: -25px;
        transform: translateX(-50%);
        font-weight: bold;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# 创建图片文件夹
def ensure_image_folder():
    # 确保在本地和Streamlit Cloud环境都能使用
    try:
        os.makedirs("images", exist_ok=True)
    except Exception as e:
        st.warning(f"无法创建图片文件夹: {e}")
        # 在云环境中可能没有写入权限，但可以读取已有图片

# 读取数据文件
@st.cache_data
def load_data():
    # 尝试不同的数据源
    data_sources = [
        {"file": "清末年号大事记.csv", "type": "csv"}
    ]
    
    for source in data_sources:
        try:
            if source["type"] == "csv" and os.path.exists(source["file"]):
                st.info(f"正在加载数据: {source['file']}")
                df = pd.read_csv(source["file"])
                return process_data(df)
        except Exception as e:
            st.warning(f"尝试读取 {source['file']} 时出错: {e}")
    
    # 如果所有数据源都失败，返回空的数据框并显示错误
    st.error("无法读取任何数据文件。请确保'清末年号大事记.csv'文件存在。")
    return pd.DataFrame(columns=["年号", "年份", "干支", "属相", "事件1", "事件2", "事件3"])

# 处理数据
def process_data(df):
    # 检查所有事件列（事件1, 事件2, 事件3, 事件4, 等等）
    event_columns = []
    for col in df.columns:
        if col == '事件' or (col.startswith('事件') and col[2:].isdigit()):
            event_columns.append(col)
    
    # 如果有旧的单一"事件"列但没有新的事件列，则重命名为"事件1"
    if '事件' in event_columns and '事件1' not in event_columns:
        df = df.rename(columns={'事件': '事件1'})
        event_columns = [col for col in event_columns if col != '事件']
        event_columns.append('事件1')
    
    # 确保至少有一个事件列
    if not any(col.startswith('事件') and col[2:].isdigit() for col in df.columns):
        st.warning("数据中没有找到事件列，请确保数据文件包含'事件1'、'事件2'、'事件3'等列")
    
    # 确保干支和生肖列存在
    for col in ['干支', '属相']:
        if col not in df.columns:
            df[col] = ''
    
    # 填充空值为空字符串
    for col in df.columns:
        if df[col].dtype == 'object':  # 只处理字符串类型的列
            df[col] = df[col].fillna('')
            
    # 确保年份是数字
    if "年份" in df.columns:
        df["年份"] = pd.to_numeric(df["年份"], errors="coerce")
    
    return df

# 查找指定年份的图片
def find_images_for_year(year):
    images_path = "images"
    if not os.path.exists(images_path):
        return []
    
    image_files = []
    try:
        for file in os.listdir(images_path):
            if file.startswith(f"{year}_") and file.lower().endswith(('.jpg', '.jpeg', '.png')):
                image_files.append(os.path.join(images_path, file))
    except Exception as e:
        st.warning(f"读取图片目录时出错: {e}")
        return []
    
    return image_files

# 显示事件卡片
def display_event_card(event_text):
    st.markdown(f'<div class="event-box" style="color: black;">{event_text}</div>', unsafe_allow_html=True)

# 显示年份标记
def display_year_marker(year, reign, ganzhi, shengxiao):
    if reign and ganzhi and shengxiao:
        st.markdown(f'<div class="year-display">{year}年，{reign}，{ganzhi}，{shengxiao}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="year-display">{year}年</div>', unsafe_allow_html=True)

# 主应用程序
def main():
    # 应用CSS
    local_css()
    
    # 确保图片文件夹存在
    ensure_image_folder()
    
    # 标题
    st.markdown('<h1 class="timeline-title">清末历史时间轴</h1>', unsafe_allow_html=True)
    st.markdown('<p class="timeline-subtitle">话剧《赤诚》历史背景</p>', unsafe_allow_html=True)
    
    # 加载数据
    df = load_data()
    
    # 如果数据为空，停止
    if df.empty:
        st.stop()
    
    # 侧边栏 - 数据源信息
    st.sidebar.header("关于《赤诚》")
    st.sidebar.write("这个时间轴工具帮助您了解《赤诚》话剧中提及的历史背景和事件。")
    st.sidebar.write("拖动时间轴来查看不同年份的历史事件。")
    
    # 显示数据表格（可折叠）
    with st.sidebar.expander("查看完整历史事件数据", expanded=False):
        st.dataframe(df)
    
    # 年号参考 (顺序和颜色)
    reign_periods = {
        "道光": {"period": "1821-1850", "start": 1821, "end": 1850, "color": "#C8E6C9"},  # 绿色
        "咸丰": {"period": "1851-1861", "start": 1851, "end": 1861, "color": "#BBDEFB"},  # 蓝色
        "同治": {"period": "1862-1874", "start": 1862, "end": 1874, "color": "#FFECB3"},  # 黄色
        "光绪": {"period": "1875-1908", "start": 1875, "end": 1908, "color": "#FFCCBC"},  # 橙色
        "宣统": {"period": "1908-1912", "start": 1909, "end": 1911, "color": "#E1BEE7"}   # 紫色
    }
    
    # 获取时间范围
    if "年份" in df.columns:
        years = df["年份"].dropna().astype(int).tolist()
        min_year, max_year = min(years), max(years)
    else:
        # 默认范围
        min_year, max_year = 1821, 1911
    
    # 创建时间轴滑块
    # 添加年号分隔线标记（直接使用st.markdown创建醒目的标记）
    slider_cols = st.columns([1, 10, 1])
    with slider_cols[1]:
        # 显示提示文字在时间轴上方
        st.markdown('<div style="text-align:center; margin-bottom:30px;">拖动选择年份</div>', unsafe_allow_html=True)
        
        # 先添加年号区域背景
        timeline_html = '<div style="position:relative; height:10px; width:100%; margin:30px 0 0px 0;">'
        
        # 添加各个年号的背景颜色区域
        k=0
        for reign, info in reign_periods.items():
            k=k+1
            start_pct = (info["start"] - min_year) / (max_year - min_year) * 100
            width_pct = (info["end"] - info["start"]) / (max_year - min_year) * 100 +1
            if k==5:
                width_pct = (info["end"] - info["start"]) / (max_year - min_year) * 100
            timeline_html += f'<div style="position:absolute; left:{start_pct}%; width:{width_pct}%; height:100%; background-color:{info["color"]}; opacity:0.3;"></div>'
            
            # 添加分隔线（更宽、更长的红色线条）
            timeline_html += f'<div style="position:absolute; left:{start_pct}%; width:2px; top:-15px; height:40px; background-color:red; z-index:100;"></div>'
            
            # 添加年号名称（确保水平显示，上移位置）
            midpoint = start_pct + width_pct/2
            
            # 特殊处理宣统，确保其水平显示并位置正确
            reign_style = "white-space: nowrap; font-weight:bold;"
            
            # 进一步上移年号名称
            timeline_html += f'<div style="position:absolute; left:{midpoint}%; transform:translateX(-50%); top:-50px; {reign_style}">{reign}</div>'
        
        # 添加最后一个年号结束的分隔线
        end_pct = 100  # 应该在最右侧，即100%位置
        timeline_html += f'<div style="position:absolute; left:{end_pct}%; width:2px; top:-15px; height:40px; background-color:red; z-index:100;"></div>'
        
        timeline_html += '</div>'
        st.markdown(timeline_html, unsafe_allow_html=True)
        
        # 创建时间轴滑块（不显示标题）
        selected_year = st.slider(
            "",  # 空标题，因为我们已经在上方添加了标题
            min_value=min_year,
            max_value=max_year,
            value=(min_year + max_year) // 2,  # 默认选择中间年份
            step=1,
            key="year_slider"
        )
    
    # 计算当前年号
    current_reign = ""
    for reign, info in reign_periods.items():
        if info["start"] <= selected_year and selected_year < info["end"]:
            current_reign = reign
            break
    
    # 筛选当年事件
    has_events = False
    if "年份" in df.columns:
        year_events = df[df["年份"] == selected_year]
        
        if not year_events.empty:
            # 从CSV中获取年份信息
            first_event = year_events.iloc[0]
            reign_info = first_event.get("年号", "")
            ganzhi = first_event.get("干支", "")
            shengxiao = first_event.get("属相", "")
            
            # 显示年份、年号、干支、生肖信息
            display_year_marker(selected_year, reign_info, ganzhi, shengxiao)
            
            # 创建两列布局: 左列显示事件，右列显示图片
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # 收集所有事件
                events_text = []
                for _, event in year_events.iterrows():
                    # 查找所有事件列
                    for col in event.index:
                        if (col.startswith('事件') and col[2:].isdigit()):
                            # 确保事件不是空或NaN
                            event_value = event[col]
                            if pd.notna(event_value) and str(event_value).strip() != "":
                                events_text.append(event_value)
                                has_events = True
                
                # 显示所有事件
                if has_events:
                    st.subheader("历史事件")
                    for event_text in events_text:
                        display_event_card(event_text)
                else:
                    st.info("该年份没有记录具体事件")
            
            with col2:
                # 查找并显示图片
                image_files = find_images_for_year(selected_year)
                if image_files:
                    st.subheader("相关图片")
                    for img_file in image_files:
                        # 从文件名中提取描述 (例如: 1840_opium_war.jpg -> "opium war")
                        img_desc = os.path.basename(img_file).split('_', 1)[1].rsplit('.', 1)[0].replace('_', ' ')
                        
                        try:
                            image = Image.open(img_file)
                            st.image(image, caption=img_desc, use_column_width=True)
                        except Exception as e:
                            st.error(f"无法加载图片 {img_file}: {e}")
        else:
            # 年份在CSV中不存在，显示简单信息
            display_year_marker(selected_year, current_reign, "", "")
            st.info("该年份没有记录具体事件")
    
    # 添加脚注
    st.markdown("---")
    st.markdown("**使用说明**: 拖动上方滑块查看不同年份的历史事件。不同颜色表示不同年号时期，垂直线标记年号的开始年份。可以添加图片文件到'images'文件夹，文件名格式为'年份_描述.jpg'(例如:1840_鸦片战争.jpg)。")
    st.markdown("**注意**: 此时间轴应用程序基于话剧《赤诚》的历史背景创建，主要关注剧中涉及的历史事件，用于教育和参考目的。")

if __name__ == "__main__":
    main() 