# 🎵 健身团课视频自动生成器 (Fitness Video Generator)

## 项目概述

基于Python的自动化视频生成工具，根据Excel编排表自动生成带音乐节拍、彩色背景、进度字幕的健身教学视频。

**核心功能：**
- 🎼 自动分析音频BPM和节拍点（使用librosa）
- 📊 Excel驱动课程编排（2×8/4×8/8×8拍自动配色）
- 🎨 白/黄/红/紫多色背景区分动作组
- 📱 多平台输出（竖屏手机/横屏iPad/横屏电视）
- ⚡️ 后台批量生成，无需手动剪辑

---

## 技术栈
- **音频分析**：librosa 0.11.x（节拍检测）
- **视频合成**：moviepy 2.2.x（剪辑、字幕、渲染）
- **数据处理**：pandas 2.0.x（Excel读取）
- **字体渲染**：PIL/Pillow + 思源黑体（中文支持）

---

## 文件结构
```
├── .gitignore                                    # Git忽略配置（忽略音乐/视频文件）
├── excel                                         # 课程配置文件夹
│   ├── butterScaler
│   │   └── butterScaler23.xlsx                   # Excel编排表
│   └── table-template.csv                        # CSV模板示例
├── fonts                                         # 字体文件夹
│   ├── SourceHanSansHWSC-Bold.otf
│   ├── SourceHanSansHWSC-Regular.otf
│   └── SourceHanSansSC-VF.otf                    # 推荐：可变字体
├── generate_video.py                             # 主程序：完整视频生成（竖屏）
├── generate_preview.py                           # 预览版：前1分钟竖屏预览
├── generate_ipad_v2.py                           # iPad版：横屏1920x1080
├── music                                         # 输入音乐文件夹（.gitkeep占位）
│   └── buttScaler23
│       └── .gitkeep
├── output                                        # 生成结果输出（.gitkeep占位）
│   └── buttScaler23
│       └── .gitkeep
├── temp-audio.m4a                                # [可选]临时音乐文件（预览用）
├── temp-excel.xlsx                               # [可选]临时Excel文件（预览用）
├── requirements.txt                              # Python依赖
└── README.md                                     # 本文档
```

---

## 📖 完整使用示例（5分钟上手）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd CreatingMoviesUsingMusicAndScripts

# 2. 安装依赖
pip install -r requirements.txt

# 3. 准备你的音乐文件（放入 music 目录）
cp /path/to/your/music.mp3 music/buttScaler23/

# 4. 准备编排表（参考 excel/table-template.csv 格式）
# 或使用现有 excel/butterScaler/butterScaler23.xlsx

# 5. 修改脚本配置（可选）
# 编辑 generate_video.py 顶部的 MUSIC_PATH 和 EXCEL_PATH

# 6. 后台生成视频（推荐）
nohup python generate_video.py > generate.log 2>&1 &

# 7. 查看进度
tail -f generate.log

# 8. 查看生成的视频
ls output/buttScaler23/*.mp4
```

**Excel编排表示例**（参考 `excel/table-template.csv`）：

| ActionName | Type | Rhythms | MainHint | SubHint |
|-----------|------|---------|---------|---------|
| 深蹲 | 4 | 4 | 双脚开立 | 与肩同宽 |
| 深蹲 | 4 | 4 | 臀部后坐 | 膝盖对准脚尖 |

**字段说明**：
- `ActionName`: 动作名称（相同名称+Type视为一组）
- `Type`: 动作组总8拍数（2=白, 4=黄, 8=红，决定背景色）
- `Rhythms`: 当前行占用节奏数（1节奏=2拍，标准8拍=4）
- `MainHint`: 主标题（显示在屏幕上方）
- `SubHint`: 副标题（显示在主标题下方）

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

**requirements.txt 内容：**
```
librosa>=0.11.0
moviepy>=2.2.0
pandas>=2.0.0
openpyxl>=3.1.0
pillow>=11.0.0
numpy>=2.0.0
```

### 2. 准备数据

将音乐文件放入 `music/` 目录，Excel编排表放入 `excel/` 目录。

### 3. 生成视频（后台运行 + 日志记录）

**推荐方式：后台运行，进度写入日志**

```bash
# 创建虚拟环境（如果不存在）
  python3 -m venv venv

# 激活并安装依赖
source venv/bin/activate
pip install -r requirements.txt

# 方式1：基础后台运行（输出到日志文件）
nohup python generate_video.py > generate_video.log 2>&1 &

nohup python generate_ipad_v2.py > generate_ipad_v2.log 2>&1 &

# 方式2：使用虚拟环境的后台运行（推荐）
source venv/bin/activate && nohup python generate_video.py > generate_video.log 2>&1 &

# 查看实时进度
tail -f generate_video.log

# 查看是否还在运行
ps aux | grep generate_video | grep -v grep

# 停止运行
pkill -f generate_video.py
```

### 4. 批量处理多个视频

编辑 `generate_video.py` 或 `generate_ipad_v2.py` 顶部的 `BATCH_CONFIGS` 列表：

```python
BATCH_CONFIGS = [
    {"music": "music/section1.mp3", "excel": "excel/config.xlsx", "output": "video1.mp4"},
    {"music": "music/section2.mp3", "excel": "excel/config.xlsx", "output": "video2.mp4"},
    {"music": "music/section3.mp3", "excel": "excel/config.xlsx", "output": "video3.mp4"},
]
```

脚本会按顺序依次处理每个配置，一次处理一个。

### 5. 使用临时文件快速预览

将音乐命名为 `temp-audio.m4a`，Excel命名为 `temp-excel.xlsx` 放在项目根目录：

```bash
# 使用临时文件（无需修改代码）
python generate_preview.py

# 或手动指定
cp your-music.mp3 temp-audio.m4a
cp your-config.xlsx temp-excel.xlsx
python generate_preview.py
```

**生成不同版本：**

```bash
# 生成完整竖屏视频（约6-7分钟，完整课程）
python generate_video.py

# 生成1分钟预览版（竖屏，快速测试）
python generate_preview.py

# 生成iPad横屏版（1920x1080，大字体）
python generate_ipad_v2.py
```

---

## 📱 可用生成脚本

| 脚本 | 用途 | 分辨率 | 时长 | 字体大小 | 使用场景 |
|------|------|--------|------|----------|----------|
| `generate_video.py` | 完整课程 | 1080×1920竖屏 | 完整音乐 | 主80px/副50px | 手机/抖音/视频号 |
| `generate_preview.py` | 快速预览 | 1080×1920竖屏 | 前1分钟(16个8拍) | 主60px/副40px | 快速测试效果 |
| `generate_ipad_v2.py` | iPad横屏 | 1920×1080横屏 | 前1分钟(16个8拍) | 主80px/副50px | iPad横屏全屏播放 |

**自定义修改：**
编辑脚本顶部的配置区域：
```python
MUSIC_PATH = "music/buttScaler23/06 06 Lose Control.mp3"
EXCEL_PATH = "excel/butterScaler/butterScaler23.xlsx"
FONT_PATH = "fonts/SourceHanSansHWSC-Bold.otf"
MAX_8BEATS = 16  # 只生成前N个8拍（预览用）
```

---

## 📝 Excel字段说明

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| **ActionName** | 字符串 | ✅ | 动作名称（同名称+Type视为一组） |
| **Type** | 整数 | ✅ | 动作组总8拍数（2=白,4=黄,8=红,决定背景色） |
| **Rhythms** | 整数 | ✅ | 当前行占用节奏数（1节奏=2拍，标准8拍=4） |
| **MainHint** | 字符串 | 可选 | 主标题/口令 |
| **SubHint** | 字符串 | 可选 | 副标题/细节提示 |
| **IsPreview** | 布尔 | 可选 | 是否为预告行（显示NEXT字样） |
| **NextActionName** | 字符串 | 条件 | IsPreview=TRUE时必填，下一个动作名 |
| **RhythmAlert** | 布尔 | 可选 | 是否在该行开始前4拍闪烁橙色预警 |

**详细文档**：参见 README.md 后半部分的完整字段规范。

---

## 🛠️ 故障排除

| 问题 | 解决方案 |
|-----|---------|
| `RuntimeError: No ffmpeg exe` | 安装ffmpeg: `brew install ffmpeg` (Mac) 或加入系统PATH |
| `OSError: cannot open resource` | 字体文件路径错误，检查FONT_PATH是否指向存在的文件 |
| 字幕显示为方框/乱码 | 字体不支持中文，使用fonts目录下的思源黑体 |
| 汉字只显示一半 | 字体渲染问题，尝试使用 `SourceHanSansSC-VF.otf` 字体 |
| 生成视频音画不同步 | 检查音乐是否恒定BPM，librosa对变速音乐支持不佳 |
| 后台运行后看不到进度 | 使用 `tail -f generate_video.log` 查看实时日志 |

---

## 📊 Excel编排表字段规范（详细版）

### 核心字段详解

#### 1. Type（动作组总8拍数）

**作用**：
- 🎨 **决定背景色**：2=白, 4=黄, 6=橙, 8=红, 10=紫...
- 📊 **决定进度分母**：显示"当前/Type"（如"2/4"）

**示例**：
```excel
Type=4  →  进度显示 1/4, 2/4, 3/4, 4/4  →  金黄色背景
Type=8  →  进度显示 1/8...8/8  →  大红色背景
```

#### 2. Rhythms（当前行节奏数）

**计算关系**：
- **标准8拍**：Rhythms=4（4×2拍=8拍）
- **半个8拍**：Rhythms=2（4拍）

**与Type的关系**：
> 同组内所有行的 **Rhythms累加 ÷ 4** 应等于 **Type**

**示例**：
```excel
ActionName=深蹲组合, Type=4
├─ 第1行: Rhythms=4  (8拍)  →  1/4
├─ 第2行: Rhythms=4  (8拍)  →  2/4  
├─ 第3行: Rhythms=2  (4拍)  →  3/4
└─ 第4行: Rhythms=6  (12拍) →  4/4

验证: (4+4+2+6)/4 = 4 = Type ✅
```

#### 3. 提示文字字段

| 字段 | 显示位置 | 字体大小 | 用途 |
|------|----------|----------|------|
| **MainHint** | 屏幕中上部 | 主标题大小 | 主口令/节拍计数 |
| **SubHint** | 主标题下方 | 副标题大小 | 动作细节/安全提示 |

#### 4. 预告与预警字段

**IsPreview + NextActionName**：
- 触发：该行显示半透明遮罩层，提示下一个动作
- 显示：背景变黑（40%透明度）+ "NEXT" + 下一个动作名

**RhythmAlert**：
- 触发：在该行开始前4拍，全屏闪烁橙色警告
- 用途：动作组切换时提醒节奏变化

---

## 完整填写示例

| ActionName | Type | Rhythms | MainHint | SubHint | IsPreview | NextActionName | RhythmAlert |
|-----------|------|---------|---------|---------|-----------|---------------|-------------|
| 预先提示 | 4 | 4 | 双脚与肩同宽 | 脚尖向前 | FALSE | | TRUE |
| 单次深蹲+弓步蹲 | 4 | 4 | 右腿往后一大步 | 回到深蹲 | FALSE | | TRUE |
| 4次半程深蹲+弓步蹲 | 8 | 4 | 深蹲4｡ 3｡ 2｡ 1｡ | 右腿向后 | FALSE | | TRUE |

**颜色对应**：
- 白色背景 (Type=2)：黑色文字
- 黄色背景 (Type=4)：黑色文字  
- 红色背景 (Type=8)：白色文字

---

## 💡 高级用法

### 批量生成多个视频

```bash
#!/bin/bash
# batch_generate.sh

for music in music/buttScaler23/*.mp3; do
    filename=$(basename "$music" .mp3)
    echo "生成: $filename"
    nohup python -c "
import sys
sys.path.insert(0, '.')
import generate_video as gv
gv.MUSIC_PATH = '$music'
gv.OUTPUT_DIR = 'output/buttScaler23'
gen = gv.FitnessVideoGenerator(gv.MUSIC_PATH, gv.EXCEL_PATH)
gen.generate()
" > "logs/${filename}.log" 2>&1 &
done
```

### 自定义分辨率

编辑脚本中的配置：
```python
VIDEO_WIDTH = 1920   # 修改宽度
VIDEO_HEIGHT = 1080  # 修改高度
```

### 调整字幕大小

编辑脚本中的配置：
```python
MAIN_FONT_SIZE = 100  # 主标题字体大小
SUB_FONT_SIZE = 60    # 副标题字体大小
```

---

## 📋 后台运行教程（详细版）

### 为什么需要后台运行？

视频生成耗时较长（1分钟视频约需1-2分钟生成），后台运行可以：
- ✅ 关闭终端后继续生成
- ✅ 同时生成多个视频
- ✅ 记录完整日志便于排查问题

### 后台运行命令详解

```bash
# 1. 基础命令结构
nohup [命令] > [日志文件] 2>&1 &

# 2. 各部分的含义
nohup      # no hang up，终端关闭后继续运行
> file.log # 标准输出（正常信息）写入日志文件
2>&1       # 标准错误（报错信息）也写入日志文件
&          # 后台运行

# 3. 完整示例
nohup python generate_video.py > generate_video.log 2>&1 &
```

### 管理后台任务

```bash
# 查看所有后台运行的Python进程
ps aux | grep python | grep -v grep

# 只查看视频生成进程
ps aux | grep generate_video | grep -v grep

# 查看日志（实时更新）
tail -f generate_video.log

# 查看日志（最后20行）
tail -20 generate_video.log

# 停止特定进程（通过PID）
kill 12345  # 将12345替换为实际的进程ID

# 停止所有视频生成进程
pkill -f generate_video.py

# 查看日志文件大小（判断是否还在写入）
ls -lh *.log
```

### 典型工作流

```bash
# 1. 激活虚拟环境（如果使用）
cd /path/to/project
source venv/bin/activate

# 2. 启动后台生成
nohup python generate_preview.py > preview.log 2>&1 &

# 3. 记录进程ID
# 输出类似: [1] 12345

# 4. 查看实时进度
tail -f preview.log

# 5. 按 Ctrl+C 退出日志查看（不会停止生成）

# 6. 过一会儿检查是否完成
ps aux | grep generate_preview | grep -v grep
# 如果没有输出，说明已完成

# 7. 查看生成的视频
ls -lh output/buttScaler23/*.mp4
```

---

## 🔧 当前限制与待优化

1. **节拍精度**：依赖librosa的鼓点检测，对纯音乐或变速音乐可能不准
2. **内存占用**：长视频（>10分钟）可能占用大量RAM（moviepy限制）
3. **字体依赖**：必须手动指定字体文件路径，跨平台兼容性待改进
4. **无音频可视化**：目前只有静态背景，没有波形或频谱可视化

---

## 📄 许可证

MIT License - 可自由修改用于商业团课视频制作。

---

**文档版本**: v2.0  
**更新日期**: 2026-03-24  
**适用代码版本**: moviepy 2.2.x + librosa 0.11.x
