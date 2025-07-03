import streamlit as st
import random
import time
from datetime import datetime
import json

# 页面配置
st.set_page_config(
    page_title="💕 Love Bubble Enhanced",
    page_icon="🫧",
    layout="wide"
)

# 增强版CSS - 优化锚点定位和视角保持
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;400;600&display=swap');
    
    * {
        font-family: 'Quicksand', sans-serif;
    }
    
    /* 添加平滑滚动 */
    html {
        scroll-behavior: smooth;
    }
    
    .main-header {
        text-align: center;
        background: linear-gradient(45deg, #ff9a9e, #fecfef, #ffa5d8);
        padding: 25px;
        border-radius: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(255, 154, 158, 0.3);
        animation: headerPulse 3s ease-in-out infinite;
    }
    
    @keyframes headerPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .score-board {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(118, 75, 162, 0.3);
    }
    
    .score-board:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(118, 75, 162, 0.4);
    }
    
    /* 游戏区域锚点定位 */
    .game-area {
        scroll-margin-top: 20px;
        position: relative;
    }
    
    .bubble-grid {
        background: linear-gradient(45deg, #f093fb, #f5576c);
        padding: 20px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
        position: relative;
    }
    
    .stButton > button {
        font-size: 28px !important;
        border: 3px solid #fff !important;
        border-radius: 50% !important;
        width: 55px !important;
        height: 55px !important;
        margin: 3px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.2) !important;
    }
    
    /* 选中状态样式 */
    .selected-bubble {
        border: 4px solid #FFD700 !important;
        background-color: rgba(255, 215, 0, 0.3) !important;
        transform: scale(1.1) !important;
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6) !important;
        animation: selectedPulse 1s ease-in-out infinite !important;
    }
    
    @keyframes selectedPulse {
        0%, 100% { 
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
        }
        50% { 
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.9);
        }
    }
    
    .easter-egg {
        background: linear-gradient(45deg, #ffeaa7, #fab1a0);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        animation: eggBounce 1s ease-in-out infinite;
        box-shadow: 0 10px 30px rgba(251, 177, 160, 0.4);
        border: 3px solid #fff;
        margin: 20px 0;
    }
    
    /* 特殊的第一次消除彩蛋样式 */
    .first-clear-egg {
        background: linear-gradient(45deg, #ff9a9e, #fecfef, #ffa5d8, #ff6b9d) !important;
        padding: 30px !important;
        border-radius: 25px !important;
        text-align: center !important;
        animation: firstClearPulse 2s ease-in-out infinite !important;
        box-shadow: 0 15px 40px rgba(255, 154, 158, 0.6) !important;
        border: 4px solid #fff !important;
        margin: 25px 0 !important;
        transform: scale(1.05) !important;
    }
    
    @keyframes firstClearPulse {
        0%, 100% { 
            transform: scale(1.05);
            box-shadow: 0 15px 40px rgba(255, 154, 158, 0.6);
        }
        50% { 
            transform: scale(1.08);
            box-shadow: 0 20px 50px rgba(255, 154, 158, 0.8);
        }
    }
    
    @keyframes eggBounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .combo-indicator {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 48px;
        color: #ff6b6b;
        animation: comboZoom 1s ease-out;
        z-index: 1000;
        pointer-events: none;
    }
    
    @keyframes comboZoom {
        0% { 
            transform: translate(-50%, -50%) scale(0);
            opacity: 0;
        }
        50% { 
            transform: translate(-50%, -50%) scale(1.2);
            opacity: 1;
        }
        100% { 
            transform: translate(-50%, -50%) scale(1);
            opacity: 0;
        }
    }
    
    .swap-instruction {
        background: linear-gradient(45deg, #74b9ff, #0984e3);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        animation: instructionGlow 2s ease-in-out infinite;
    }
    
    @keyframes instructionGlow {
        0%, 100% { box-shadow: 0 4px 15px rgba(116, 185, 255, 0.3); }
        50% { box-shadow: 0 6px 25px rgba(116, 185, 255, 0.6); }
    }
    
    .level-up {
        background: linear-gradient(45deg, #ffd89b, #19547b);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        animation: levelPulse 0.6s ease-in-out;
        margin: 10px 0;
    }
    
    @keyframes levelPulse {
        0% { transform: scale(0.8); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .floating-hearts {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 1000;
    }
    
    .heart {
        position: absolute;
        font-size: 20px;
        animation: floatUp 3s ease-out forwards;
    }
    
    @keyframes floatUp {
        0% {
            opacity: 1;
            transform: translateY(100vh) rotate(0deg);
        }
        100% {
            opacity: 0;
            transform: translateY(-100px) rotate(360deg);
        }
    }
    
    /* 成功反馈动画 */
    .success-feedback {
        position: fixed;
        top: 20%;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(45deg, #00b894, #00cec9);
        color: white;
        padding: 15px 30px;
        border-radius: 20px;
        font-size: 18px;
        font-weight: bold;
        z-index: 1001;
        animation: successPop 2s ease-out forwards;
        box-shadow: 0 10px 30px rgba(0, 184, 148, 0.4);
    }
    
    @keyframes successPop {
        0% {
            opacity: 0;
            transform: translateX(-50%) scale(0.5);
        }
        20% {
            opacity: 1;
            transform: translateX(-50%) scale(1.1);
        }
        80% {
            opacity: 1;
            transform: translateX(-50%) scale(1);
        }
        100% {
            opacity: 0;
            transform: translateX(-50%) scale(0.8);
        }
    }
</style>

<script>
// 自动滚动到游戏区域的JavaScript函数
function scrollToGameArea() {
    setTimeout(function() {
        const gameArea = document.getElementById('game-area');
        if (gameArea) {
            gameArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }, 100);
}

// 监听页面加载完成事件
window.addEventListener('load', function() {
    // 检查URL参数，如果有scroll=game，则滚动到游戏区域
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('scroll') === 'game' || sessionStorage.getItem('scrollToGame') === 'true') {
        scrollToGameArea();
        sessionStorage.removeItem('scrollToGame');
    }
});

// 成功反馈函数
function showSuccessFeedback(message) {
    const feedback = document.createElement('div');
    feedback.className = 'success-feedback';
    feedback.innerHTML = message;
    document.body.appendChild(feedback);
    
    setTimeout(function() {
        if (feedback.parentNode) {
            feedback.parentNode.removeChild(feedback);
        }
    }, 2000);
}
</script>
""", unsafe_allow_html=True)

# 初始化交换式游戏状态
def init_enhanced_game():
    defaults = {
        'game_grid': generate_enhanced_grid(7, 6),
        'score': 0,
        'level': 1,
        'combo': 0,
        'max_combo': 0,
        'moves': 0,
        'selected_bubble': None,
        'swap_mode': True,
        'special_bubbles_collected': {'💖': 0, '⭐': 0, '🌈': 0, '💎': 0, '🌸': 0},
        'easter_eggs_unlocked': [],
        'show_easter_egg': None,
        'last_action': None,
        'game_time': 0,
        'daily_played': False,
        'achievements': [],
        'floating_hearts': False,
        'show_combo_effect': False,
        'level_up_animation': False,
        'auto_clear_happening': False,
        'first_clear_done': False,
        'need_refresh': False,
        'last_success_message': None,  # 新增：存储成功消息
        'should_scroll_to_game': False  # 新增：是否需要滚动到游戏区域
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# 生成网格（保持不变）
def generate_enhanced_grid(rows, cols):
    ENHANCED_BUBBLES = {
        'normal': ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣'],
        'special': ['💖', '⭐', '🌈', '💎', '🌸']
    }
    
    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            if random.random() < 0.15:
                bubble = random.choice(ENHANCED_BUBBLES['special'])
            else:
                bubble = random.choice(ENHANCED_BUBBLES['normal'])
            row.append(bubble)
        grid.append(row)
    return grid

# 检查两个位置是否相邻
def are_adjacent(pos1, pos2):
    """检查两个位置是否相邻（上下左右）"""
    row1, col1 = pos1
    row2, col2 = pos2
    
    return (abs(row1 - row2) == 1 and col1 == col2) or (abs(col1 - col2) == 1 and row1 == row2)

# 交换两个位置的泡泡
def swap_bubbles(grid, pos1, pos2):
    """交换两个位置的泡泡"""
    row1, col1 = pos1
    row2, col2 = pos2
    
    grid[row1][col1], grid[row2][col2] = grid[row2][col2], grid[row1][col1]

# 查找连接泡泡（保持不变）
def find_connected_bubbles(grid, start_row, start_col):
    """查找连接的相同颜色泡泡"""
    if not grid or start_row < 0 or start_row >= len(grid) or start_col < 0 or start_col >= len(grid[0]):
        return []
    
    target_bubble = grid[start_row][start_col]
    if not target_bubble:
        return []
    
    visited = set()
    connected = []
    
    def dfs(row, col):
        if (row, col) in visited:
            return
        if row < 0 or row >= len(grid) or col < 0 or col >= len(grid[0]):
            return
        if grid[row][col] != target_bubble:
            return
        
        visited.add((row, col))
        connected.append((row, col))
        
        dfs(row-1, col)
        dfs(row+1, col)
        dfs(row, col-1)
        dfs(row, col+1)
    
    dfs(start_row, start_col)
    return connected

# 查找所有可消除的连接组合
def find_all_clearable_groups(grid):
    """查找所有可消除的连接组合"""
    visited_global = set()
    clearable_groups = []
    
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if (i, j) not in visited_global:
                connected = find_connected_bubbles(grid, i, j)
                if len(connected) >= 3:
                    clearable_groups.append(connected)
                visited_global.update(connected)
                
    return clearable_groups

# 移除泡泡（保持不变）
def remove_bubbles(grid, positions):
    """移除指定位置的泡泡并让上方泡泡下落"""
    for row, col in positions:
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            grid[row][col] = None
    
    rows, cols = len(grid), len(grid[0])
    for col in range(cols):
        bubbles = []
        for row in range(rows):
            if grid[row][col] is not None:
                bubbles.append(grid[row][col])
        
        for row in range(rows):
            grid[row][col] = None
        
        for i, bubble in enumerate(reversed(bubbles)):
            grid[rows - 1 - i][col] = bubble
    
    normal_bubbles = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣']
    special_bubbles = ['💖', '⭐', '🌈', '💎', '🌸']
    
    for col in range(cols):
        for row in range(rows):
            if grid[row][col] is None:
                if random.random() < 0.1:
                    grid[row][col] = random.choice(special_bubbles)
                else:
                    grid[row][col] = random.choice(normal_bubbles)

# 自动消除所有可消除的组合
def auto_clear_bubbles():
    """自动消除所有可消除的泡泡组合"""
    total_cleared = 0
    combo_count = 0
    
    while True:
        clearable_groups = find_all_clearable_groups(st.session_state.game_grid)
        
        if not clearable_groups:
            break
            
        # 消除所有可消除组合
        all_positions = []
        for group in clearable_groups:
            all_positions.extend(group)
        
        # 计算分数
        cleared_count = len(all_positions)
        base_score = cleared_count * 20
        combo_bonus = combo_count * 15
        level_bonus = st.session_state.level * 10
        total_score = base_score + combo_bonus + level_bonus
        
        st.session_state.score += total_score
        total_cleared += cleared_count
        combo_count += 1
        
        # 统计特殊泡泡
        for pos in all_positions:
            row, col = pos
            bubble_type = st.session_state.game_grid[row][col]
            if bubble_type in st.session_state.special_bubbles_collected:
                st.session_state.special_bubbles_collected[bubble_type] += 1
        
        # 移除泡泡
        remove_bubbles(st.session_state.game_grid, all_positions)
    
    # 更新连击
    st.session_state.combo += combo_count
    if st.session_state.combo > st.session_state.max_combo:
        st.session_state.max_combo = st.session_state.combo
    
    return total_cleared, combo_count

# 检查交换后是否能产生消除
def can_create_match(grid, pos1, pos2):
    """检查交换后是否能产生可消除的组合"""
    # 临时交换
    swap_bubbles(grid, pos1, pos2)
    
    # 检查两个位置是否能产生消除
    connected1 = find_connected_bubbles(grid, pos1[0], pos1[1])
    connected2 = find_connected_bubbles(grid, pos2[0], pos2[1])
    
    can_clear = len(connected1) >= 3 or len(connected2) >= 3
    
    # 交换回来
    swap_bubbles(grid, pos1, pos2)
    
    return can_clear

# 彩蛋系统（保持不变）
ENHANCED_EASTER_EGGS = {
    'love_quotes': [
        "今天的你也是最美的泡泡 💕",
        "和你在一起的每一天都很甜",
        "你就是我生命中最美的彩虹",
        "想把所有的小星星都送给你",
        "你比游戏里的钻石还要珍贵",
        "每一次交换都是我对你的思念",
        "樱花飘落的时候，我想到了你的笑容",
        "就像交换泡泡一样，我想和你交换心意",
        "连击越高，我对你的爱越深",
        "这个游戏是我用代码编织的爱意"
    ],
    'special_messages': [
        "🎀 你发现了隐藏的小惊喜！",
        "🌟 哇！你的运气真好！",
        "🦄 独角兽为你送来了祝福！",
        "🍀 四叶草说你今天会很幸运！",
        "🎈 气球们为你庆祝！"
    ],
    'achievements': {
        50: "🌱 萌新玩家",
        200: "🎯 交换高手", 
        500: "💝 泡泡达人",
        1000: "👑 消除女王",
        2000: "💫 钻石恋人",
        5000: "🌈 彩虹大师",
        10000: "💖 爱情至尊"
    },
    'first_clear_message': "你好呀甜甜，这是给你的专属小游戏 🥰✨💕🌸🎀"
}

# 其他功能函数（保持不变但增加优化）
def create_floating_hearts():
    if st.session_state.floating_hearts:
        hearts_html = '<div class="floating-hearts">'
        for i in range(8):
            left_pos = random.randint(10, 90)
            delay = random.uniform(0, 2)
            hearts_html += f'''
            <div class="heart" style="left: {left_pos}%; animation-delay: {delay}s;">💕</div>
            '''
        hearts_html += '</div>'
        st.markdown(hearts_html, unsafe_allow_html=True)
        st.session_state.floating_hearts = False

def show_combo_effect(combo_count):
    if combo_count >= 3:
        combo_text = f"🔥 COMBO x{combo_count} 🔥"
        st.markdown(f'''
        <div class="combo-indicator">
            {combo_text}
        </div>
        ''', unsafe_allow_html=True)

def enhanced_easter_egg_check(cleared_count, combo):
    triggers = []
    
    # 检查是否是第一次消除
    if not st.session_state.first_clear_done:
        triggers.append('first_clear')
        st.session_state.first_clear_done = True
    elif cleared_count >= 6:
        triggers.append('love_quote')
    elif combo >= 3:
        triggers.append('mega_combo')
    
    if st.session_state.score in ENHANCED_EASTER_EGGS['achievements']:
        triggers.append('achievement')
    
    if st.session_state.moves == 77:
        triggers.append('lucky_number')
    
    return triggers

def display_enhanced_easter_egg(egg_types):
    for egg_type in egg_types:
        if egg_type == 'first_clear':
            st.markdown(f"""
            <div class="easter-egg first-clear-egg">
                <h1>🎉✨ 第一次消除成功！ ✨🎉</h1>
                <h2 style="color: #ff6b9d; font-size: 24px; margin: 20px 0;">
                    {ENHANCED_EASTER_EGGS['first_clear_message']}
                </h2>
                <p style="font-size: 18px; color: #2d3436; margin: 15px 0;">
                    🌟 希望这个小游戏能给你带来快乐哦~ 🌟
                </p>
                <p style="font-size: 16px; color: #636e72; margin: 10px 0;">
                    🎮 继续努力，会有更多惊喜等着你！ 🎮
                </p>
                <p style="font-size: 14px; color: #81ecec; margin-top: 20px;">
                    💝 用心制作，满满都是爱意 💝
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.floating_hearts = True
        elif egg_type == 'love_quote':
            quote = random.choice(ENHANCED_EASTER_EGGS['love_quotes'])
            st.markdown(f"""
            <div class="easter-egg">
                <h2>💕 爱的悄悄话 💕</h2>
                <p style="font-size: 20px; font-style: italic; color: #2d3436;">"{quote}"</p>
                <p style="font-size: 14px; color: #636e72;">❤️ 来自最可爱的人 ❤️</p>
            </div>
            """, unsafe_allow_html=True)
        elif egg_type == 'mega_combo':
            st.session_state.floating_hearts = True

def show_live_stats():
    st.markdown("### 📊 实时统计")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔄 交换次数", st.session_state.moves)
    with col2:
        st.metric("🔥 最高连击", st.session_state.max_combo)
    with col3:
        total_special = sum(st.session_state.special_bubbles_collected.values())
        st.metric("✨ 特殊泡泡", total_special)
    with col4:
        if st.session_state.moves > 0:
            efficiency = round(st.session_state.score / st.session_state.moves, 1)
            st.metric("📈 效率", f"{efficiency}")

# 优化的泡泡点击处理逻辑 - 减少刷新
def handle_bubble_click(current_pos):
    """处理泡泡点击逻辑，避免不必要的页面刷新"""
    if st.session_state.selected_bubble is None:
        # 第一次选择
        st.session_state.selected_bubble = current_pos
        return "selected"
        
    elif st.session_state.selected_bubble == current_pos:
        # 取消选择
        st.session_state.selected_bubble = None
        return "deselected"
        
    else:
        # 尝试交换
        selected_pos = st.session_state.selected_bubble
        
        if are_adjacent(selected_pos, current_pos):
            # 检查交换后是否能产生消除
            if can_create_match(st.session_state.game_grid, selected_pos, current_pos):
                # 执行交换
                swap_bubbles(st.session_state.game_grid, selected_pos, current_pos)
                st.session_state.moves += 1
                st.session_state.selected_bubble = None
                
                # 自动消除
                cleared_count, combo_rounds = auto_clear_bubbles()
                
                if cleared_count > 0:
                    # 检查彩蛋
                    easter_eggs = enhanced_easter_egg_check(cleared_count, combo_rounds)
                    if easter_eggs:
                        st.session_state.show_easter_egg = easter_eggs
                    
                    # 升级检查
                    new_level = st.session_state.score // 500 + 1
                    if new_level > st.session_state.level:
                        st.session_state.level = new_level
                        st.session_state.level_up_animation = True
                        st.balloons()
                    
                    # 显示连击效果
                    if combo_rounds >= 2:
                        show_combo_effect(combo_rounds)
                    
                    # 设置成功消息，但先不刷新
                    st.session_state.last_success_message = f"🎉 成功交换！消除了 {cleared_count} 个泡泡，{combo_rounds} 轮连击！"
                    st.session_state.should_scroll_to_game = True
                    
                    return f"success:{cleared_count}:{combo_rounds}"
                else:
                    return "no_match"
            else:
                st.session_state.selected_bubble = None
                return "invalid_match"
        else:
            st.session_state.selected_bubble = None
            return "not_adjacent"

# 主游戏函数增强版 - 减少不必要刷新
def enhanced_main():
    init_enhanced_game()
    
    # 如果需要滚动到游戏区域，添加JavaScript
    if st.session_state.should_scroll_to_game:
        st.markdown("""
        <script>
        sessionStorage.setItem('scrollToGame', 'true');
        setTimeout(function() {
            const gameArea = document.getElementById('game-area');
            if (gameArea) {
                gameArea.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 300);
        </script>
        """, unsafe_allow_html=True)
        st.session_state.should_scroll_to_game = False
    
    # 显示成功消息（如果有）
    if st.session_state.last_success_message:
        st.markdown(f"""
        <script>
        showSuccessFeedback('{st.session_state.last_success_message}');
        </script>
        """, unsafe_allow_html=True)
        st.session_state.last_success_message = None
    
    # 标题动画
    st.markdown("""
    <div class="main-header">
        <h1>💕 Love Bubble Enhanced (交换版) 💕</h1>
        <p style="font-size: 18px;">为你特制的甜蜜交换游戏</p>
        <p style="font-size: 14px; opacity: 0.8;">✨ 选择相邻泡泡进行交换 ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 游戏说明
    st.markdown("""
    <div class="swap-instruction">
        <h3>🎮 游戏玩法</h3>
        <p><strong>1️⃣ 选择泡泡</strong> → <strong>2️⃣ 选择相邻泡泡交换</strong> → <strong>3️⃣ 自动消除连接组合</strong></p>
        <p>💡 <strong>策略提示</strong>：交换后必须能产生3个或以上连接才能成功交换！</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 分数板
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="score-board">
            <h3>💯 分数</h3>
            <h1>{st.session_state.score}</h1>
            <p>下一级还需: {500 - (st.session_state.score % 500)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="score-board">
            <h3>⚡ 等级</h3>
            <h1>{st.session_state.level}</h1>
            <p>连击: {st.session_state.combo}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        selected_text = "已选择" if st.session_state.selected_bubble else "未选择"
        st.markdown(f"""
        <div class="score-board">
            <h3>🎯 选择状态</h3>
            <h1>{selected_text}</h1>
            <p>交换: {st.session_state.moves}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 创建飘浮爱心
    create_floating_hearts()
    
    # 游戏区域 - 添加锚点ID
    st.markdown('<div id="game-area" class="game-area">', unsafe_allow_html=True)
    st.markdown('<div class="bubble-grid">', unsafe_allow_html=True)
    
    # 显示当前选中状态
    if st.session_state.selected_bubble:
        row, col = st.session_state.selected_bubble
        bubble = st.session_state.game_grid[row][col]
        st.info(f"🎯 已选择: 位置({row},{col}) {bubble} - 请选择相邻的泡泡进行交换")
    else:
        st.info("👆 请选择第一个泡泡开始交换")
    
    # 创建消息容器
    message_container = st.empty()
    
    # 使用会话状态来跟踪需要刷新的情况
    need_full_refresh = False
    
    # 显示游戏网格
    for i, row in enumerate(st.session_state.game_grid):
        cols = st.columns(len(row))
        for j, bubble in enumerate(row):
            with cols[j]:
                # 检查是否为选中状态
                is_selected = st.session_state.selected_bubble == (i, j)
                
                # 显示按钮
                if st.button(bubble, key=f"bubble_{i}_{j}"):
                    current_pos = (i, j)
                    result = handle_bubble_click(current_pos)
                    
                    # 根据结果显示相应消息
                    if result == "selected":
                        message_container.info(f"🎯 已选择位置 ({i},{j})")
                    elif result == "deselected":
                        message_container.info("❌ 取消选择")
                    elif result.startswith("success"):
                        parts = result.split(":")
                        cleared_count = parts[1]
                        combo_rounds = parts[2]
                        message_container.success(f"🎉 成功交换！消除了 {cleared_count} 个泡泡，{combo_rounds} 轮连击！")
                        # 只有在交换成功时才标记需要刷新
                        need_full_refresh = True
                    elif result == "no_match":
                        message_container.warning("⚠️ 交换失败：没有产生可消除的组合")
                    elif result == "invalid_match":
                        message_container.error("❌ 无法交换：交换后不会产生3个以上的连接！")
                    elif result == "not_adjacent":
                        message_container.error("❌ 只能与相邻的泡泡交换（上下左右）！")
    
    st.markdown('</div>', unsafe_allow_html=True)  # 关闭bubble-grid
    st.markdown('</div>', unsafe_allow_html=True)  # 关闭game-area
    
    # 只在必要时才刷新页面
    if need_full_refresh:
        time.sleep(0.5)  # 短暂延迟让用户看到消息
        st.rerun()
    
    # 升级动画
    if st.session_state.level_up_animation:
        st.markdown(f"""
        <div class="level-up">
            <h2>🎊 恭喜升级到 Level {st.session_state.level}! 🎊</h2>
            <p>你的交换技巧越来越厉害了！</p>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.level_up_animation = False
    
    # 显示彩蛋
    if st.session_state.show_easter_egg:
        display_enhanced_easter_egg(st.session_state.show_easter_egg)
        if st.button("继续游戏 💕", key="continue_game"):
            st.session_state.show_easter_egg = None
            st.rerun()
    
    # 实时统计
    show_live_stats()
    
    # 游戏控制
    st.markdown("### 🎮 游戏控制")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 重新开始", key="restart"):
            for key in list(st.session_state.keys()):
                if key not in ['start_time']:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("🎲 重新排列", key="shuffle"):
            st.session_state.game_grid = generate_enhanced_grid(7, 6)
            st.session_state.selected_bubble = None
            st.rerun()
    
    with col3:
        if st.button("❌ 取消选择", key="cancel_selection"):
            st.session_state.selected_bubble = None
            message_container.info("❌ 已取消选择")
    
    with col4:
        if st.button("📱 分享成绩", key="share"):
            st.success(f"🎉 我在Love Bubble交换版中得了{st.session_state.score}分！进行了{st.session_state.moves}次交换！")

if __name__ == "__main__":
    enhanced_main()