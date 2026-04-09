#!/usr/bin/env python3
"""
iPad 横屏视频生成器 - 完整版 (1920x1080)
支持批量处理多个音乐+Excel组合
"""
import librosa
import pandas as pd
import numpy as np
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, TextClip
from moviepy.video.fx import FadeIn
import os
from datetime import datetime
from typing import List, Tuple, Dict

# ==================== 批量处理配置 ====================
# 配置列表：每个元素包含 music_path, excel_path, output_name
# 按顺序依次处理，一次处理一个
BATCH_CONFIGS = [
    # {
    #     "music": "music/buttScaler23/01 I Just Might.mp3",
    #     "excel": "excel/butterScaler/butterScaler23.xlsx",
    #     "output": "butterScaler23_Section01_iPad.mp4"
    # },
    # {
    #     "music": "music/buttScaler23/05 05 I WANT IT.mp3",
    #     "excel": "excel/butterScaler/butterScaler23-Section05.xlsx",
    #     "output": "butterScaler23_Section05_iPad.mp4"
    # },
    {
        "music": "music/buttScaler23/06 06 Lose Control.mp3",
        "excel": "excel/butterScaler/butterScaler23-Section06.xlsx",
        "output": "butterScaler23_Section06_iPad.mp4"
    },
]

DEFAULT_MUSIC_PATH = "music/buttScaler23/06 06 Lose Control.mp3"
DEFAULT_EXCEL_PATH = "excel/butterScaler/butterScaler23-Section06.xlsx"
OUTPUT_DIR = "output/buttScaler23"
FONT_PATH = "fonts/SourceHanSansHWSC-Bold.otf"

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BEATS_PER_RHYTHM = 2
ALERT_BEATS = 4

def get_type_color(type_num):
    color_map = {
        2: (255, 255, 255), 4: (255, 235, 59), 6: (255, 152, 0),
        8: (244, 67, 54), 10: (156, 39, 176), 12: (63, 81, 181),
        14: (0, 150, 136), 16: (76, 175, 80),
    }
    return color_map.get(type_num, (128, 128, 128))

def get_text_color(type_num):
    return 'black' if type_num in [2, 4, 6] else 'white'

class iPadVideoGenerator:
    def __init__(self, music_path, excel_path, output_path):
        self.music_path = music_path
        self.excel_path = excel_path
        self.output_path = output_path
        self.beat_times = None
        self.bpm = None
        self.clips = []
        self.audio_duration = 0
        
    def analyze_music(self):
        print(f"🎵 分析音频: {self.music_path}")
        y, sr = librosa.load(self.music_path, sr=None)
        self.audio_duration = len(y) / sr
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=128)
        self.bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        max_beats = int(self.audio_duration / 60 * self.bpm)
        print(f"✅ BPM: {self.bpm:.1f}, 音频时长: {self.audio_duration:.1f}s, 最大节拍数: {max_beats}")
        
    def get_beat_time(self, beat_idx):
        if beat_idx < 0:
            first_beat = self.beat_times[0] if len(self.beat_times) > 0 else 0
            beat_duration = 60 / self.bpm if self.bpm > 0 else 0.5
            return first_beat + beat_idx * beat_duration
        if beat_idx < len(self.beat_times):
            return self.beat_times[beat_idx]
        last_time = self.beat_times[-1] if len(self.beat_times) > 0 else 0
        beat_duration = 60 / self.bpm if self.bpm > 0 else 0.5
        return last_time + (beat_idx - len(self.beat_times) + 1) * beat_duration
        
    def create_text_clip(self, text, fontsize, color, duration, start, pos_y, max_chars=15, min_lines=1):
        # 限制最多显示15个字
        if len(text) > max_chars:
            text = text[:max_chars]
        lines = max(min_lines, text.count('\n') + 1)
        return TextClip(
            text=text, font_size=fontsize, color=color, font=FONT_PATH,
            method='caption', size=(int(VIDEO_WIDTH * 0.95), int(fontsize * lines * 1.6)),
            text_align='center', horizontal_align='center', vertical_align='center'
        ).with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * pos_y))
    
    def create_alert_clip(self, next_action, duration, start):
        bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(255, 87, 34), duration=duration).with_start(start)
        bg = FadeIn(0.1).apply(bg)
        bg = bg.with_opacity(0.9)
        text_content = "节奏变化！\n" + (f"即将: {next_action}" if next_action else "")
        # 智能估算实际行数：节奏变化！占1行，动作名称按每8个字符一行估算（iPad横屏更宽）
        action_text = next_action if next_action else ""
        action_lines = max(1, (len(action_text) + 7) // 8) if action_text else 0
        estimated_lines = 1 + action_lines  # 节奏变化！+ 动作名称的实际行数
        txt = TextClip(
            text=text_content, font_size=100, color='white', font=FONT_PATH, method='caption',
            size=(int(VIDEO_WIDTH * 0.95), int(100 * estimated_lines * 2.2)), text_align='center',
            horizontal_align='center', vertical_align='center',
            stroke_color='black', stroke_width=3
        ).with_duration(duration).with_start(start).with_position('center')
        return [bg, txt]
    
    def create_preview_overlay(self, next_action, duration, start):
        overlay = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration).with_start(start).with_opacity(0.4)
        # 限制动作名称长度，防止文本过长
        max_chars = 16  # iPad横屏可以显示更多字符
        display_action = next_action if len(next_action) <= max_chars else next_action[:max_chars-2] + "..."
        preview_text = f"NEXT\n{display_action}"
        # 估算实际行数：NEXT占1行，动作名称按每8个字符一行估算（iPad横屏更宽）
        action_lines = max(1, (len(display_action) + 7) // 8)  # 向上取整
        estimated_lines = 1 + action_lines  # NEXT + 动作名称的实际行数
        # 高度倍数增加到2.2，确保3-4行文本都能完整显示
        preview_txt = TextClip(
            text=preview_text, font_size=120, color='#FFD700', font=FONT_PATH,
            method='caption', size=(int(VIDEO_WIDTH * 0.95), int(120 * estimated_lines * 2.2)), text_align='center',
            horizontal_align='center', vertical_align='center',
            stroke_color='black', stroke_width=4
        ).with_duration(duration).with_start(start).with_position('center')
        countdown_text = "▶▶▶ 准备切换 ▶▶▶"
        countdown_lines = countdown_text.count('\n') + 1
        countdown = TextClip(
            text=countdown_text, font_size=60, color='yellow', font=FONT_PATH,
            bg_color='black', method='caption', 
            size=(int(VIDEO_WIDTH * 0.95), int(60 * countdown_lines * 1.6)),
            text_align='center', horizontal_align='center', vertical_align='center'
        ).with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * 0.82))
        return [overlay, preview_txt, countdown]

    def generate(self):
        """生成完整版视频（随音乐时长）"""
        self.analyze_music()
        df = pd.read_excel(self.excel_path)
        print(f"📊 读取到 {len(df)} 行编排数据")
        
        group_counters = {}
        current_group_id = None
        timeline = []
        current_beat = 0
        
        for idx, row in df.iterrows():
            action_name = str(row['ActionName'])
            rhythms = int(row['Rhythms'])
            type_num = int(row['Type'])
            group_key = f"{action_name}_{type_num}"
            
            if group_key != current_group_id:
                current_group_id = group_key
                group_counters[current_group_id] = 0
            group_counters[current_group_id] += 1
            idx_in_group = group_counters[current_group_id]
            
            beats = rhythms * BEATS_PER_RHYTHM
            start_beat = current_beat
            end_beat = start_beat + beats
            
            timeline.append({
                'row': row, 'start_beat': start_beat, 'end_beat': end_beat,
                'idx_in_group': idx_in_group, 'group_key': group_key, 'row_index': idx
            })
            current_beat = end_beat
        
        print(f"🎬 预计总时长: {self.get_beat_time(current_beat):.1f}秒")
        
        # 计算音频能支持的最大beat数，超出部分自动截断
        audio_max_beats = int(self.audio_duration / 60 * self.bpm)
        if current_beat > audio_max_beats:
            print(f"⚠️ 警告: Excel需要{current_beat}beats，音频只支持{audio_max_beats}beats，将自动截断")
        
        actual_end_time = 0
        for i, item in enumerate(timeline):
            row = item['row']
            start_beat = item['start_beat']
            end_beat = item['end_beat']
            idx_in_group = item['idx_in_group']
            start_time = self.get_beat_time(start_beat)
            end_time = self.get_beat_time(end_beat)
            duration = end_time - start_time
            
            # 检查是否超出音频时长，超出则跳过
            if start_time >= self.audio_duration:
                continue
            
            # 如果部分超出，截断duration
            if end_time > self.audio_duration:
                end_time = self.audio_duration
                duration = end_time - start_time
                print(f"  截断: 第{i+1}行部分超出音频时长，已截断")
            
            actual_end_time = end_time
            
            action_name = str(row['ActionName'])
            type_num = int(row['Type'])
            # 支持 StepActionName 列：每一步可以显示不同的动作名，不影响 Type 计数
            step_action_name = str(row.get('StepActionName', '')) if pd.notna(row.get('StepActionName', '')) else ''
            display_action_name = step_action_name if step_action_name else action_name
            main_hint = str(row['MainHint']) if pd.notna(row['MainHint']) else display_action_name
            sub_hint = str(row['SubHint']) if pd.notna(row['SubHint']) else ""
            is_preview = bool(row.get('IsPreview', False))
            next_action = str(row.get('NextActionName', '')) if pd.notna(row.get('NextActionName', '')) else ''
            rhythm_alert = bool(row.get('RhythmAlert', False))
            
            bg_color = get_type_color(type_num)
            text_color = get_text_color(type_num)
            
            print(f"  处理: {display_action_name} [{idx_in_group}/{type_num}] ({duration:.1f}s)")
            
            if rhythm_alert and i > 0:
                alert_start = self.get_beat_time(start_beat - ALERT_BEATS)
                alert_duration = start_time - alert_start
                if alert_duration > 0 and alert_start < self.audio_duration:
                    if alert_start + alert_duration > self.audio_duration:
                        alert_duration = self.audio_duration - alert_start
                    alert_clips = self.create_alert_clip(action_name, alert_duration, alert_start)
                    self.clips.extend(alert_clips)
            
            bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=bg_color, duration=duration).with_start(start_time)
            self.clips.append(bg)
            
            # 检查是否需要倒数显示：MainHint是纯数字且能被Rhythms整除
            rhythms = int(row['Rhythms'])
            main_hint_str = str(main_hint) if pd.notna(main_hint) else ""
            if main_hint_str.isdigit() and len(main_hint_str) > 1 and rhythms % len(main_hint_str) == 0:
                # 倒数模式：将每个数字分配到对应的rhythm时间段
                chars = list(main_hint_str)  # 如 "4321" -> ['4','3','2','1']
                chars_per_rhythm = rhythms // len(chars)
                beat_duration = (end_time - start_time) / rhythms
                for idx, char in enumerate(chars):
                    char_start = start_time + idx * chars_per_rhythm * beat_duration
                    char_duration = chars_per_rhythm * beat_duration
                    char_clip = self.create_text_clip(char, 160, text_color, char_duration, char_start, -0.02)
                    self.clips.append(char_clip)
            else:
                # MainHint - 贴顶显示，继续上移增加间距
                main_clip = self.create_text_clip(main_hint, 160, text_color, duration, start_time, -0.02, min_lines=2)
                self.clips.append(main_clip)
            
            # SubHint 和 Type 分开显示，增加间距
            if sub_hint:
                # SubHint - MainHint下方，预留2行空间，增加间距
                sub_hint_clip = self.create_text_clip(sub_hint, 100, text_color, duration, start_time, 0.38, min_lines=2)
                self.clips.append(sub_hint_clip)
                type_display = f"{idx_in_group}/{type_num}"
                # Type - SubHint下方，增加间距
                type_clip = self.create_text_clip(type_display, 100, text_color, duration, start_time, 0.54)
                self.clips.append(type_clip)
            else:
                type_display = f"{idx_in_group}/{type_num}"
                # Type - MainHint下方（无SubHint时）
                type_clip = self.create_text_clip(type_display, 100, text_color, duration, start_time, 0.38)
                self.clips.append(type_clip)
            
            # ActionName - Type下方，继续下移增加间距
            action_name_clip = self.create_text_clip(display_action_name, 80, '#808080', duration, start_time, 0.72)
            self.clips.append(action_name_clip)
            
            if is_preview and next_action:
                preview_clips = self.create_preview_overlay(next_action, duration, start_time)
                self.clips.extend(preview_clips)
            elif idx_in_group == type_num - 1 and type_num >= 2 and i < len(timeline) - 1:
                next_row = timeline[i+1]['row']
                next_name = str(next_row.get('NextActionName', '')) if pd.notna(next_row.get('NextActionName', '')) else str(next_row['ActionName'])
                auto_preview_text = f"准备: {next_name}"
                auto_preview_lines = auto_preview_text.count('\n') + 1
                auto_preview = TextClip(
                    text=auto_preview_text, font_size=45, color='yellow', font=FONT_PATH,
                    bg_color='black', method='caption', 
                    size=(int(VIDEO_WIDTH * 0.9), int(45 * auto_preview_lines * 1.6)),
                    text_align='center', horizontal_align='center', vertical_align='center'
                ).with_duration(duration).with_start(start_time)
                auto_preview = auto_preview.with_position(('center', VIDEO_HEIGHT * 0.86))
                self.clips.append(auto_preview)
        
        print("🎞️ 合成视频...")
        final = CompositeVideoClip(self.clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        audio = AudioFileClip(self.music_path).subclipped(0, final.duration)
        final = final.with_audio(audio)
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        final.write_videofile(
            self.output_path, fps=30, codec='libx264', audio_codec='aac',
            temp_audiofile='temp-audio.m4a', remove_temp=True, threads=4
        )
        print(f"✅ 完成: {self.output_path}")
        return self.output_path

def process_single(music_path, excel_path, output_name):
    """处理单个视频"""
    output_path = os.path.join(OUTPUT_DIR, output_name)
    gen = iPadVideoGenerator(music_path, excel_path, output_path)
    return gen.generate()

def main():
    print("=" * 60)
    print("🎬 iPad 横屏视频生成器 - 完整版 (1920x1080)")
    print("=" * 60)
    
    if BATCH_CONFIGS:
        print(f"\n📋 批量处理模式: 共 {len(BATCH_CONFIGS)} 个任务")
        print("=" * 60)
        
        for i, config in enumerate(BATCH_CONFIGS, 1):
            print(f"\n[{i}/{len(BATCH_CONFIGS)}] 开始处理...")
            print("-" * 40)
            
            music_path = config["music"]
            excel_path = config["excel"]
            output_name = config["output"]
            
            if not os.path.exists(music_path):
                print(f"⚠️ 跳过: 音乐文件不存在 {music_path}")
                continue
            if not os.path.exists(excel_path):
                print(f"⚠️ 跳过: Excel文件不存在 {excel_path}")
                continue
            
            try:
                process_single(music_path, excel_path, output_name)
                print(f"✅ [{i}/{len(BATCH_CONFIGS)}] 完成: {output_name}")
            except Exception as e:
                print(f"❌ [{i}/{len(BATCH_CONFIGS)}] 失败: {e}")
                continue
        
        print("\n" + "=" * 60)
        print("🎉 批量处理完成!")
    else:
        print("\n📋 单文件模式")
        print("-" * 40)
        if not os.path.exists(DEFAULT_MUSIC_PATH):
            print(f"❌ 错误: 音乐文件不存在 {DEFAULT_MUSIC_PATH}")
            return
        if not os.path.exists(DEFAULT_EXCEL_PATH):
            print(f"❌ 错误: Excel文件不存在 {DEFAULT_EXCEL_PATH}")
            return
        
        output_name = f"fitness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        process_single(DEFAULT_MUSIC_PATH, DEFAULT_EXCEL_PATH, output_name)

if __name__ == "__main__":
    main()
