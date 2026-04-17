# 🎵 健身团课视频自动生成器

基于 Python 的自动化视频生成工具，支持两种工作流：
1. **节拍驱动** — 根据 Excel 编排表 + 音乐节拍，生成带节奏提示的健身视频
2. **文稿驱动** — 根据 Markdown 教学稿 + 音乐时间轴，生成带逐句提示的团课教学视频

---

## 项目结构

```
├── generator/
│   ├── followTheBeat/           # Excel + 音乐节拍 工作流
│   │   ├── generate_video.py    # 竖屏 1080×1920
│   │   ├── generate_ipad.py     # 横屏 1920×1080
│   └── followTheHint/           # Markdown + 音乐时间轴 工作流
│       └── generate_hint_video.py   # 横屏 1920×1080，支持 preview 参数
├── excel/
│   ├── butterScaler/            # Excel 编排表（节拍驱动）
│   └── Template.xlsx            # Excel 模板
├── markdown/
│   ├── muscleGrowth/            # Markdown 教学稿（文稿驱动）
│   │   ├── T1-热身.md
│   │   └── T2-下肢.md
│   └── Template.md              # Markdown 模板
├── music/
│   ├── buttScaler23/            # 节拍驱动音乐
│   └── muscleGrowth14/          # 文稿驱动音乐
├── output/
│   ├── buttScaler23/            # 节拍驱动输出
│   └── muscleGrowth14/          # 文稿驱动输出
├── fonts/
│   └── SourceHanSansHWSC-Bold.otf
├── requirements.txt
└── README.md
```

---

## 环境准备

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活（macOS/Linux）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**requirements.txt 主要依赖：**
- `librosa>=0.11.0` — 音频节拍分析
- `moviepy>=2.1.0` — 视频合成
- `pandas>=2.0.0` + `openpyxl>=3.1.0` — Excel 读取
- `numpy`, `pillow`

---

## 工作流一：followTheBeat（Excel + 音乐节拍）

适用于课程编排精确到节拍的场景，如 BodyPump、莱美类团课。

### 核心原理
- 使用 `librosa` 自动检测音乐的 **BPM** 和 **节拍点**
- 根据 Excel 中的 `Rhythms`（节奏数）自动计算每行占用的节拍时长
- 不同 `Type` 自动分配不同背景色（白/黄/橙/红/紫/蓝/青/绿）
- 支持倒数显示、节奏预警、NEXT 预告等功能

### 可用脚本

| 脚本 | 分辨率 | 使用场景 |
|------|--------|----------|
| `generator/followTheBeat/generate_video.py` | 1080×1920 竖屏 | 手机/抖音/视频号 |
| `generator/followTheBeat/generate_ipad.py` | 1920×1080 横屏 | iPad / 电视横屏 |

### 快速使用

1. **准备音乐** 放入 `music/buttScaler23/`
2. **准备编排表** 放入 `excel/butterScaler/`，参考 `excel/Template.xlsx`
3. **编辑脚本配置**（`generator/followTheBeat/generate_xxx.py` 顶部的 `BATCH_CONFIGS`）

```python
BATCH_CONFIGS = [
    {
        "music": "../../music/buttScaler23/02 02 ONE MORE TIME.mp3",
        "excel": "../../excel/butterScaler/butterScaler23-Section02.xlsx",
        "output": "butterScaler23_Section02_iPad.mp4"
    },
]
```

4. **生成视频**

```bash
cd generator/followTheBeat

# 完整版
python generate_ipad.py

# 1 分钟预览版
python generate_ipad.py preview
python generate_video.py preview
```

### Excel 字段说明

| 字段 | 说明 |
|------|------|
| `ActionName` | 动作组名称（同名称+Type视为一组） |
| `Type` | 动作组总 8 拍数，决定背景色和进度分母（2=白, 4=黄, 8=红…） |
| `Rhythms` | 当前行占用的节奏数（1 节奏 = 2 拍，标准 8 拍 = 4） |
| `StepActionName` | 每步显示的动作名（可选） |
| `MainHint` | 主提示（屏幕中上部） |
| `SubHint` | 副提示（主提示下方） |
| `IsPreview` | 是否为预告行（显示 NEXT 遮罩） |
| `NextActionName` | 预告的下一个动作名 |
| `RhythmAlert` | 是否在该行动作开始前 4 拍闪烁橙色预警 |

**特殊规则**：当 `MainHint` 为纯数字且位数能被 `Rhythms` 整除时，自动进入倒数模式（如 `4321` + `Rhythms=4` 会依次显示 4→3→2→1）。

---

## 工作流二：followTheHint（Markdown + 音乐时间轴）

适用于教练口述教学、按时间轴提示动作细节的场景。

### 核心原理
- 解析 Markdown 中的时间表和编号提示语
- 每句提示语按 `持续时间 ÷ 行数` 自动分配显示时长
- 大字号字幕居中偏上显示，底部显示动作名
- 每个动作带 **秒数倒计时**
- 动作结束前 4 秒自动预告下一个动作
- 音乐剩余时间自动显示 `Be Happy` + 笑脸

### 快速使用

1. **准备音乐** 放入 `music/muscleGrowth14/`
2. **编写 Markdown** 放入 `markdown/muscleGrowth/`，参考 `markdown/muscleGrowth/Template.md`

```markdown
# T2下肢

## 音乐
名称：T2下肢.mp3
时长：08:01

## 动作

### 预先提示

|开始时间|持续时间|结束时间|
|---|---|---|
|00:00|00:20|00:20|

1. 双手拿片，双脚与髋同宽
2. 肩部下沉，右腿往后一大步
...
```

3. **生成视频**

```bash
cd generator/followTheHint

# 完整版（默认处理 T2-下肢.md）
python generate_hint_video.py

# 指定其他 Markdown 文件
python generate_hint_video.py T1-热身.md
python generate_hint_video.py T3-上肢1.md

# 1 分钟预览版
python generate_hint_video.py preview T2-下肢.md
```

### Markdown 填写规范

- `# 小节名称`：决定输出视频文件名
- `## 音乐`：`名称` 必须和 `music/muscleGrowth14/` 下的文件名完全一致；`时长` 格式为 `mm:ss`
- `### 动作名`：每个动作一个三级标题
- 时间表：紧跟 `|开始时间|持续时间|结束时间|` 表格
- 提示语：用 `1. ` ~ `n. ` 编号列表，每句最多 25 个汉字

---

## 后台运行与日志

视频生成耗时较长（8 分钟视频约 15~20 分钟），推荐后台运行：

```bash
# followTheBeat 后台运行
cd generator/followTheBeat
nohup python generate_ipad.py > generate_ipad.log 2>&1 &

# followTheHint 后台运行
cd generator/followTheHint
nohup python generate_hint_video.py T2-下肢.md > generate_hint.log 2>&1 &

# 查看进度
tail -f generate_hint.log
```

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `RuntimeError: No ffmpeg exe` | macOS 执行 `brew install ffmpeg` 并确保在 PATH 中 |
| 字幕显示方框/乱码 | 使用 `fonts/` 目录下的思源黑体，不要依赖系统默认字体 |
| 音画不同步 | 检查音乐是否为恒定 BPM，变速音乐建议手动切分或换曲 |
| 生成速度很慢 | moviepy 本身较慢，降低分辨率或缩短时长可加速 |
| `ModuleNotFoundError` | 确保激活了 `venv` 并执行了 `pip install -r requirements.txt` |

---

## 许可证

MIT License — 可自由修改用于商业团课视频制作。
