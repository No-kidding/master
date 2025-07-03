import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['OMP_NUM_THREADS'] = '1'

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import json
import re
from datetime import datetime
import base64
import io
from openai import OpenAI

# 页面配置
st.set_page_config(
    page_title="游戏战绩统计系统 - 千问版",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'game_data' not in st.session_state:
    st.session_state.game_data = {
        'players': {},  # {player_name: {datetime: score}}
        'dates': [],    # [datetime1, datetime2, ...]
        'payment_status': {},  # {player_name: {datetime: True/False}}
    }

# 初始化已处理文件列表
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()

# 添加实时更新标志
if 'table_update_trigger' not in st.session_state:
    st.session_state.table_update_trigger = 0

def image_to_base64(image):
    """将PIL图像转换为base64字符串"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def call_qianwen_api(image_base64, api_key):
    """调用千问多模态API"""
    try:
        client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        prompt = """请分析这张游戏排行榜截图，提取以下信息并以JSON格式返回：

{
    "game_time": "比赛时间（格式：6-20 20:26 或 类似格式）",
    "players": [
        {
            "name": "玩家昵称",
            "score": 数字分数（正数或负数）
        }
    ]
}

要求：
1. 仔细识别每个玩家的昵称，去除排名数字
2. 准确提取每个玩家的战绩分数，注意正负号
3. 如果分数有逗号分隔符，请去除
4. 只返回JSON格式的数据，不要其他说明文字"""

        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": image_base64}
                        },
                        {
                            "type": "text", 
                            "text": prompt
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        content = completion.choices[0].message.content
        if content is None:
            return None

        if not isinstance(content, str):
            try:
                content = str(content)
            except:
                return None
        
        try:
            json_start = content.find('{')
            json_end_pos = content.rfind('}')
            
            if json_start == -1 or json_end_pos == -1:
                return None
            
            if json_start >= json_end_pos:
                return None
            
            json_str = content[json_start:json_end_pos + 1]
            
            if not json_str.strip():
                return None
            
            parsed_data = json.loads(json_str)
            return parsed_data
        except (json.JSONDecodeError, ValueError):
            return None
            
    except Exception as e:
        st.error(f"API调用错误: {e}")
        return None

def validate_player_data(name, score):
    """验证玩家数据是否完整有效"""
    # 验证昵称
    if not name or len(name.strip()) < 1:
        return False, "昵称为空"
    
    if len(name.strip()) > 20:  # 昵称过长可能是识别错误
        return False, "昵称过长"
    
    # 检查昵称是否包含明显的识别错误（如大量数字、特殊符号）
    if re.match(r'^\d+$', name.strip()):  # 纯数字
        return False, "昵称为纯数字"
    
    if len(re.findall(r'[^\w\u4e00-\u9fff]', name.strip())) > 2:  # 特殊符号过多
        return False, "昵称包含过多特殊符号"
    
    # 验证分数
    try:
        score_num = int(float(score))
        if abs(score_num) > 10000:  # 分数过大可能是识别错误
            return False, "分数超出合理范围"
        return True, ""
    except (ValueError, TypeError):
        return False, "分数格式错误"

def extract_game_info_with_qianwen(image, api_key):
    """使用千问API提取游戏信息 - 增强数据验证"""
    try:
        image_base64 = image_to_base64(image)
        result = call_qianwen_api(image_base64, api_key)
        
        if result and "players" in result:
            cleaned_players = []
            skipped_players = []
            
            for player in result["players"]:
                name = player.get("name", "").strip()
                score = player.get("score", 0)
                
                name = clean_player_name(name)
                
                if isinstance(score, str):
                    score = parse_score_string(score)
                
                # 验证数据完整性
                is_valid, error_msg = validate_player_data(name, score)
                
                if is_valid:
                    cleaned_players.append({
                        "name": name,
                        "score": int(score)
                    })
                else:
                    skipped_players.append({
                        "name": name,
                        "score": score,
                        "error": error_msg
                    })
            
            game_time = result.get("game_time", "")
            if not game_time:
                game_time = datetime.now().strftime("%m-%d %H:%M")
            
            return {
                "game_time": game_time,
                "players": cleaned_players,
                "skipped_players": skipped_players,
                "raw_response": result
            }
        else:
            return None
            
    except Exception as e:
        st.error(f"千问API解析错误: {e}")
        return None

def clean_player_name(name):
    """清理玩家昵称"""
    if not name:
        return ""
    
    # 移除开头的排名数字
    cleaned = re.sub(r'^\d+\s*', '', name)
    # 保留中文、英文、数字，移除大部分特殊符号
    cleaned = re.sub(r'[^\w\u4e00-\u9fff\-_]', '', cleaned)
    return cleaned.strip()

def parse_score_string(score_str):
    """解析分数字符串"""
    if isinstance(score_str, (int, float)):
        return score_str
    
    try:
        score_str = str(score_str).replace(',', '').replace(' ', '')
        return int(float(score_str))
    except (ValueError, TypeError):
        return 0

def normalize_datetime(game_time):
    """标准化日期时间格式 - 保留完整的时间信息"""
    try:
        patterns = [
            r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})',
            r'(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})',
            r'(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})',
            r'(\d{1,2})-(\d{1,2})',
            r'(\d{1,2})/(\d{1,2})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, game_time)
            if match:
                groups = match.groups()
                if len(groups) == 5:
                    year, month, day, hour, minute = groups
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute}"
                elif len(groups) == 4:
                    month, day, hour, minute = groups
                    current_year = datetime.now().year
                    return f"{current_year}-{month.zfill(2)}-{day.zfill(2)} {hour.zfill(2)}:{minute}"
                elif len(groups) == 2:
                    month, day = groups
                    current_year = datetime.now().year
                    current_time = datetime.now().strftime("%H:%M")
                    return f"{current_year}-{month.zfill(2)}-{day.zfill(2)} {current_time}"
        
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

def update_game_data(game_info):
    """更新游戏数据并触发表格刷新"""
    game_datetime = normalize_datetime(game_info['game_time'])
    
    # 添加时间到列表（如果不存在）
    if game_datetime not in st.session_state.game_data['dates']:
        st.session_state.game_data['dates'].append(game_datetime)
        st.session_state.game_data['dates'].sort()
    
    for player in game_info['players']:
        name = player['name']
        score = player['score']
        
        # 初始化玩家数据
        if name not in st.session_state.game_data['players']:
            st.session_state.game_data['players'][name] = {}
        
        # 初始化支付状态
        if name not in st.session_state.game_data['payment_status']:
            st.session_state.game_data['payment_status'][name] = {}
        
        # 只有当该玩家在该时间还没有数据时才添加
        if game_datetime not in st.session_state.game_data['players'][name]:
            st.session_state.game_data['players'][name][game_datetime] = score
            st.session_state.game_data['payment_status'][name][game_datetime] = False
    
    # 触发表格更新
    st.session_state.table_update_trigger += 1

def delete_player(player_name):
    """删除玩家"""
    if player_name in st.session_state.game_data['players']:
        del st.session_state.game_data['players'][player_name]
    if player_name in st.session_state.game_data['payment_status']:
        del st.session_state.game_data['payment_status'][player_name]

def delete_date(date_time):
    """删除日期列"""
    if date_time in st.session_state.game_data['dates']:
        st.session_state.game_data['dates'].remove(date_time)
        for player_name in st.session_state.game_data['players']:
            if date_time in st.session_state.game_data['players'][player_name]:
                del st.session_state.game_data['players'][player_name][date_time]
        for player_name in st.session_state.game_data['payment_status']:
            if date_time in st.session_state.game_data['payment_status'][player_name]:
                del st.session_state.game_data['payment_status'][player_name][date_time]

def create_table_dataframe():
    """创建表格数据框"""
    players = st.session_state.game_data['players']
    dates = st.session_state.game_data['dates']
    payment_status = st.session_state.game_data['payment_status']
    
    if not players or not dates:
        return pd.DataFrame()
    
    data = []
    for player_name in players:
        row = {'玩家昵称': player_name}
        total_score = 0
        for date in dates:
            score = players[player_name].get(date, 0)
            row[date] = score
            total_score += score
        
        row['总计'] = total_score
        row['平均分'] = round(total_score / 20, 2) if total_score != 0 else 0
        
        # 添加支付状态列
        for date in dates:
            payment_key = f"{date}_支付"
            is_paid = payment_status.get(player_name, {}).get(date, False)
            row[payment_key] = is_paid
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # 按总分降序排序
    if not df.empty and '总计' in df.columns:
        df = df.sort_values('总计', ascending=False).reset_index(drop=True)
        
        # 添加总计行
        totals_row = {'玩家昵称': '总计'}
        for col in df.columns[1:]:
            if col.endswith('_支付'):
                totals_row[col] = ""
            elif col in ['总计', '平均分']:
                totals_row[col] = df[col].sum() if col == '总计' else round(df[col].sum(), 2)
            else:
                totals_row[col] = df[col].sum()
        
        totals_df = pd.DataFrame([totals_row])
        df = pd.concat([df, totals_df], ignore_index=True)
    
    return df

def process_single_image(uploaded_file, api_key, container):
    """处理单张图片并实时更新显示"""
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    
    if file_id in st.session_state.processed_files:
        return
    
    with container:
        with st.spinner(f"🔄 正在解析 {uploaded_file.name}..."):
            try:
                image = Image.open(uploaded_file)
                
                # 显示正在解析的图片
                col_img, col_info = st.columns([1, 2])
                
                with col_img:
                    st.image(image, caption=f"解析中: {uploaded_file.name}", width=200)
                
                with col_info:
                    game_info = extract_game_info_with_qianwen(image, api_key)
                    
                    if game_info and game_info['players']:
                        # 更新数据
                        update_game_data(game_info)
                        st.session_state.processed_files.add(file_id)
                        
                        # 显示解析结果
                        st.success(f"✅ 解析成功！")
                        st.write(f"**时间:** {normalize_datetime(game_info['game_time'])}")
                        st.write(f"**有效玩家:** {len(game_info['players'])} 个")
                        
                        # 显示有效玩家
                        for player in game_info['players']:
                            st.write(f"✅ {player['name']}: {player['score']}")
                        
                        # 显示跳过的玩家
                        if game_info.get('skipped_players'):
                            with st.expander("⚠️ 跳过的数据"):
                                for skipped in game_info['skipped_players']:
                                    st.write(f"❌ {skipped['name']} ({skipped['error']}): {skipped['score']}")
                        
                    else:
                        st.error(f"❌ 解析失败或无有效数据")
                        
            except Exception as e:
                st.error(f"处理出错: {e}")

def main():
    st.title("病历本 - 智能游戏战绩统计")
    st.markdown("---")
    
    # 创建主要布局
    left_col, right_col = st.columns([1, 3])
    
    with left_col:
        st.header("📝 操作面板")
        
        # API密钥输入
        st.subheader("🔑 API配置")
        api_key = st.text_input(
            "千问API密钥",
            type="password",
            help="请输入您的阿里云千问API密钥",
            placeholder="sk-xxx"
        )
        
        if not api_key:
            st.warning("⚠️ 请先输入API密钥")
            return
        
        st.markdown("---")
        
        # 文件上传
        st.subheader("📷 上传游戏截图")
        uploaded_files = st.file_uploader(
            "选择图片文件",
            type=['png', 'jpg', 'jpeg', 'gif', 'bmp'],
            accept_multiple_files=True,
            help="支持多张图片，逐个解析"
        )
        
        # 删除功能
        st.markdown("---")
        st.subheader("🗑️ 数据管理")
        
        if st.session_state.game_data['players']:
            player_to_delete = st.selectbox(
                "删除玩家",
                [""] + list(st.session_state.game_data['players'].keys())
            )
            if st.button("删除玩家", disabled=not player_to_delete):
                delete_player(player_to_delete)
                st.rerun()
        
        if st.session_state.game_data['dates']:
            date_to_delete = st.selectbox(
                "删除场次",
                [""] + st.session_state.game_data['dates']
            )
            if st.button("删除场次", disabled=not date_to_delete):
                delete_date(date_to_delete)
                st.rerun()
        
        if st.button("🗑️ 清空所有数据", type="secondary"):
            st.session_state.game_data = {'players': {}, 'dates': [], 'payment_status': {}}
            st.session_state.processed_files = set()
            st.rerun()
        
        # 统计信息
        st.markdown("---")
        st.subheader("📊 数据统计")
        st.metric("已解析场次", len(st.session_state.game_data['dates']))
        st.metric("玩家数量", len(st.session_state.game_data['players']))
    
    with right_col:
        # 创建标签页
        tab1, tab2 = st.tabs(["📈 实时统计表", "🔍 解析进度"])
        
        with tab1:
            st.header("战绩统计表")
            
            # 实时显示表格
            df = create_table_dataframe()
            
            if not df.empty:
                # 动态生成列配置
                column_config = {
                    "玩家昵称": st.column_config.TextColumn("玩家昵称", width="medium"),
                    "总计": st.column_config.NumberColumn("总计", format="%d", disabled=True),
                    "平均分": st.column_config.NumberColumn("平均分", format="%.2f", disabled=True)
                }
                
                # 为每个日期列添加配置
                for date in st.session_state.game_data['dates']:
                    column_config[date] = st.column_config.NumberColumn(date, format="%d")
                    payment_key = f"{date}_支付"
                    column_config[payment_key] = st.column_config.CheckboxColumn(
                        f"{date[:10]} 支付", 
                        help=f"是否支付 {date}"
                    )
                
                # 显示可编辑表格
                edited_df = st.data_editor(
                    df,
                    use_container_width=True,
                    num_rows="fixed",
                    disabled=['玩家昵称', '总计', '平均分'],
                    column_config=column_config,
                    key=f"score_table_{st.session_state.table_update_trigger}"
                )
                
                # 下载功能
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 下载CSV文件",
                    data=csv,
                    file_name=f"游戏战绩_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("📷 请上传游戏截图开始统计")
        
        with tab2:
            st.header("解析进度")
            
            # 解析进度容器
            progress_container = st.container()
            
            # 处理上传的文件
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    process_single_image(uploaded_file, api_key, progress_container)
            
            # 显示已处理文件
            if st.session_state.processed_files:
                st.subheader("✅ 已处理文件")
                for file_id in st.session_state.processed_files:
                    file_name = file_id.split('_')[0]
                    st.write(f"📁 {file_name}")
    
    # 使用说明
    with st.expander("💡 使用说明"):
        st.markdown("""
        **优化功能：**
        - 🎯 **智能过滤**: 自动过滤识别不完整的昵称和战绩
        - 📊 **实时更新**: 每解析一张图片立即更新表格
        - 🔍 **逐步显示**: 解析进度实时展示，表格逐列添加
        - ⚠️ **错误提示**: 显示跳过的数据和原因
        
        **数据验证规则：**
        - 昵称不能为空或过长
        - 不接受纯数字昵称
        - 过滤包含过多特殊符号的昵称
        - 分数必须在合理范围内(-10000 到 10000)
        """)

if __name__ == "__main__":
    main()

