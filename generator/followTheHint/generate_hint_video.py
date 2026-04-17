#!/usr/bin/env python3
"""
根据 Markdown 文档和音乐生成团课教学视频
支持：解析 Markdown 中的动作时间表和提示字幕，生成 iPad 横屏视频 (1920x1080)
"""

import re
import os
import sys

from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, TextClip

# ==================== 配置 ====================
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FONT_PATH = "../../fonts/SourceHanSansHWSC-Bold.otf"
MUSIC_DIR = "../../music/muscleGrowth14"
MARKDOWN_DIR = "../../markdown/muscleGrowth"
OUTPUT_DIR = "../../output/muscleGrowth14"

# 背景色循环，用于区分不同动作
ACTION_BG_COLORS = [
    (255, 255, 255),   # 白
    (255, 235, 59),    # 黄
    (255, 152, 0),     # 橙
    (244, 67, 54),     # 红
    (156, 39, 176),    # 紫
    (63, 81, 181),     # 蓝
    (0, 150, 136),     # 青
    (76, 175, 80),     # 绿
]


def get_bg_color(index):
    return ACTION_BG_COLORS[index % len(ACTION_BG_COLORS)]


def get_text_color(bg_color):
    """根据背景色亮度决定黑/白文字"""
    r, g, b = bg_color
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return 'black' if brightness > 180 else 'white'


def time_to_seconds(t):
    """将 mm:ss 格式转换为秒数"""
    t = t.strip()
    parts = t.split(':')
    if len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    else:
        raise ValueError(f"无法解析时间: {t}")


def parse_markdown(md_path):
    """解析 Markdown 文件，返回 (section_name, music_name, music_duration_str, actions)"""
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    section_name = "未知小节"
    music_name = None
    music_duration_str = None
    actions = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('# ') and not line.startswith('## '):
            section_name = line[1:].strip()
        elif '名称：' in line and '音乐' not in line:
            music_name = line.split('：', 1)[1].strip()
        elif '时长：' in line:
            music_duration_str = line.split('：', 1)[1].strip()
        elif line.startswith('### '):
            action_name = line[3:].strip()
            i += 1
            # 跳过空行直到表格
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            # 跳过表头
            if i < len(lines) and '开始时间' in lines[i]:
                i += 1
            # 跳过分隔线
            if i < len(lines) and '---' in lines[i]:
                i += 1
            # 读取时间行
            time_line = lines[i].strip() if i < len(lines) else ''
            i += 1
            time_parts = [p.strip() for p in time_line.strip('|').split('|')]
            start_time = time_parts[0] if len(time_parts) > 0 else ''
            duration = time_parts[1] if len(time_parts) > 1 else ''
            end_time = time_parts[2] if len(time_parts) > 2 else ''

            # 跳过空行直到 hints 列表
            while i < len(lines) and lines[i].strip() == '':
                i += 1

            # 读取 hints
            hints = []
            while i < len(lines) and re.match(r'^\d+\.', lines[i].strip()):
                hint = re.sub(r'^\d+\.\s*', '', lines[i].strip())
                # 最多 25 个字
                if len(hint) > 25:
                    hint = hint[:25]
                hints.append(hint)
                i += 1

            actions.append({
                'name': action_name,
                'start': start_time,
                'duration': duration,
                'end': end_time,
                'hints': hints,
            })
            continue
        i += 1

    return section_name, music_name, music_duration_str, actions


class HintVideoGenerator:
    def __init__(self, music_path, actions, output_path, expected_duration=None, preview=False):
        self.music_path = music_path
        self.actions = actions
        self.output_path = output_path
        self.expected_duration = expected_duration  # 秒
        self.preview = preview
        self.max_duration = 60.0 if preview else float('inf')
        self.clips = []
        self.audio_duration = 0

    def analyze_music(self):
        print(f"🎵 分析音频: {self.music_path}")
        with AudioFileClip(self.music_path) as audio:
            self.audio_duration = audio.duration
        if self.preview:
            self.audio_duration = min(self.audio_duration, self.max_duration)
            print(f"✅ 预览模式，音频时长限制为: {self.audio_duration:.1f}s")
        else:
            print(f"✅ 音频时长: {self.audio_duration:.1f}s")
        if self.expected_duration and not self.preview and abs(self.audio_duration - self.expected_duration) > 5:
            print(f"⚠️ 警告: 标注时长 {self.expected_duration:.1f}s 与实际时长 {self.audio_duration:.1f}s 偏差超过 5 秒")

    def create_text_clip(self, text, fontsize, color, duration, start, pos_y, max_chars=25):
        if len(text) > max_chars:
            text = text[:max_chars]
        lines = text.count('\n') + 1
        return TextClip(
            text=text, font_size=fontsize, color=color, font=FONT_PATH,
            method='caption', size=(int(VIDEO_WIDTH * 0.95), int(fontsize * lines * 2.6)),
            text_align='center', horizontal_align='center', vertical_align='center'
        ).with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * pos_y))

    def create_next_preview_clip(self, next_action_name, duration, start):
        """创建下一个动作预告"""
        overlay = ColorClip(
            size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration
        ).with_start(start).with_opacity(0.5)

        text = f"NEXT\n{next_action_name}"
        lines = text.count('\n') + 1
        txt = TextClip(
            text=text, font_size=120, color='#FFD700', font=FONT_PATH,
            method='caption', size=(int(VIDEO_WIDTH * 0.95), int(120 * lines * 2.0)),
            text_align='center', horizontal_align='center', vertical_align='center',
            stroke_color='black', stroke_width=4
        ).with_duration(duration).with_start(start).with_position('center')

        countdown = TextClip(
            text="▶▶▶ 准备切换 ▶▶▶", font_size=60, color='yellow', font=FONT_PATH,
            bg_color='black', method='caption',
            size=(int(VIDEO_WIDTH * 0.95), int(60 * 1.6)),
            text_align='center', horizontal_align='center', vertical_align='center'
        ).with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * 0.82))

        return [overlay, txt, countdown]

    def generate(self):
        self.analyze_music()
        print(f"📋 共 {len(self.actions)} 个动作")
        if self.preview:
            print("👁️ 预览模式: 只生成前 60 秒")

        last_end_time = 0

        for i, action in enumerate(self.actions):
            start_sec = time_to_seconds(action['start'])
            duration_sec = time_to_seconds(action['duration'])
            end_sec = start_sec + duration_sec

            # 预览模式：跳过 60 秒之后的动作
            if self.preview and start_sec >= self.max_duration:
                print(f"  跳过: {action['name']} (开始时间 {start_sec:.1f}s 已超出预览范围)")
                continue

            # 截断超出音频时长或预览时长的部分
            if end_sec > self.audio_duration:
                end_sec = self.audio_duration
                duration_sec = end_sec - start_sec
                print(f"  截断: {action['name']} 部分超出音频时长，已截断至 {end_sec:.1f}s")

            # 预览模式：如果动作跨 60 秒边界，截断
            if self.preview and end_sec > self.max_duration:
                end_sec = self.max_duration
                duration_sec = end_sec - start_sec
                print(f"  截断: {action['name']} 部分超出预览范围，已截断至 {end_sec:.1f}s")

            last_end_time = end_sec
            bg_color = get_bg_color(i)
            text_color = get_text_color(bg_color)

            print(f"  处理: {action['name']} [{start_sec:.1f}s - {end_sec:.1f}s], {len(action['hints'])} 条字幕")

            # 背景
            bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=bg_color, duration=duration_sec).with_start(start_sec)
            self.clips.append(bg)

            # 字幕：平均分配时间
            hints = action['hints']
            if hints:
                hint_duration = duration_sec / len(hints)
                for idx, hint in enumerate(hints):
                    hint_start = start_sec + idx * hint_duration
                    # 最后一条字幕持续到动作结束，避免浮点误差
                    if idx == len(hints) - 1:
                        hint_duration_actual = end_sec - hint_start
                    else:
                        hint_duration_actual = hint_duration

                    # 字幕居中偏上（占满原来 mainhint + subhint 的区域）
                    clip = self.create_text_clip(
                        hint, fontsize=100, color=text_color,
                        duration=hint_duration_actual, start=hint_start, pos_y=0.25
                    )
                    self.clips.append(clip)

            # 动作名称显示在底部
            action_name_clip = self.create_text_clip(
                action['name'], fontsize=60, color='black',
                duration=duration_sec, start=start_sec, pos_y=0.78
            )
            self.clips.append(action_name_clip)

            # 预告下一个动作（结束前 4 秒）
            if i < len(self.actions) - 1:
                next_action = self.actions[i + 1]['name']
                preview_start = max(start_sec, end_sec - 4)
                preview_duration = end_sec - preview_start
                if preview_duration > 0:
                    preview_clips = self.create_next_preview_clip(next_action, preview_duration, preview_start)
                    self.clips.extend(preview_clips)

        # 音乐剩余时间显示 Be Happy
        if last_end_time < self.audio_duration:
            remaining = self.audio_duration - last_end_time
            print(f"  剩余 {remaining:.1f}s，显示 Be Happy")
            bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(255, 193, 7), duration=remaining).with_start(last_end_time)
            self.clips.append(bg)

            text = "Be Happy\n( ˶ˊᵕˋ)੭♡"
            happy_clip = TextClip(
                text=text, font_size=160, color='black', font=FONT_PATH,
                method='caption', size=(int(VIDEO_WIDTH * 0.95), int(160 * 3)),
                text_align='center', horizontal_align='center', vertical_align='center'
            ).with_duration(remaining).with_start(last_end_time).with_position('center')
            self.clips.append(happy_clip)

        print("🎞️ 合成视频...")
        final = CompositeVideoClip(self.clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        audio = AudioFileClip(self.music_path).subclipped(0, final.duration)
        final = final.with_audio(audio)

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        final.write_videofile(
            self.output_path, fps=30, codec='libx264', audio_codec='aac',
            temp_audiofile='temp-audio.m4a', remove_temp=True, threads=4
        )
        print(f"✅ 完成: {self.output_path}")
        return self.output_path


def main():
    preview = 'preview' in sys.argv[1:]
    md_file = "T2-下肢.md"
    md_path = os.path.join(MARKDOWN_DIR, md_file)

    if not os.path.exists(md_path):
        print(f"❌ Markdown 文件不存在: {md_path}")
        return

    section_name, music_name, music_duration_str, actions = parse_markdown(md_path)
    print(f"📖 小节: {section_name}")
    print(f"🎵 音乐: {music_name} (标注时长: {music_duration_str})")

    if not music_name:
        print("❌ 未能从 Markdown 中解析音乐名称")
        return

    music_path = os.path.join(MUSIC_DIR, music_name)
    if not os.path.exists(music_path):
        print(f"❌ 音乐文件不存在: {music_path}")
        return

    expected_duration = time_to_seconds(music_duration_str) if music_duration_str else None

    suffix = "_preview.mp4" if preview else "_hint.mp4"
    output_name = f"{section_name}{suffix}"
    output_path = os.path.join(OUTPUT_DIR, output_name)

    gen = HintVideoGenerator(music_path, actions, output_path, expected_duration, preview=preview)
    gen.generate()


if __name__ == "__main__":
    main()
