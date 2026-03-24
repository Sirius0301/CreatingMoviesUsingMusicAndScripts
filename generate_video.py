#!/usr/bin/env python3
"""
健身团课视频生成器 - 竖屏完整版 (1080x1920)
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
    {
        "music": "music/buttScaler23/01 I Just Might.mp3",
        "excel": "excel/butterScaler/butterScaler23.xlsx",
        "output": "butterScaler23_Section01_Full.mp4"
    },
    {
        "music": "music/buttScaler23/02 02 ONE MORE TIME.mp3",
        "excel": "excel/butterScaler/butterScaler23.xlsx",
        "output": "butterScaler23_Section02_Full.mp4"
    },
    {
        "music": "music/buttScaler23/06 06 Lose Control.mp3",
        "excel": "excel/butterScaler/butterScaler23.xlsx",
        "output": "butterScaler23_Section06_Full.mp4"
    },
]

DEFAULT_MUSIC_PATH = "music/buttScaler23/06 06 Lose Control.mp3"
DEFAULT_EXCEL_PATH = "excel/butterScaler/butterScaler23.xlsx"
OUTPUT_DIR = "output/buttScaler23"
FONT_PATH = "fonts/SourceHanSansHWSC-Bold.otf"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
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

class FitnessVideoGenerator:
    def __init__(self, music_path, excel_path, output_path):
        self.music_path = music_path
        self.excel_path = excel_path
        self.output_path = output_path
        self.beat_times = None
        self.bpm = None
        self.clips = []
        
    def analyze_music(self):
        print(f"🎵 分析音频: {self.music_path}")
        y, sr = librosa.load(self.music_path, sr=None)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=128)
        self.bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        print(f"✅ BPM: {self.bpm:.1f}, 检测到 {len(self.beat_times)} 个节拍")
        
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
        
    def create_text_clip(self, text, fontsize, color, duration, start, pos_y):
        lines = text.count('\n') + 1
        return TextClip(
            text=text, font_size=fontsize, color=color, font=FONT_PATH,
            method='caption', size=(int(VIDEO_WIDTH * 0.85), int(fontsize * lines * 1.5)),
            text_align='center', horizontal_align='center', vertical_align='center'
        ).with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * pos_y))
    
    def create_alert_clip(self, next_action, duration, start):
        bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(255, 87, 34), duration=duration).with_start(start)
        bg = FadeIn(0.1).apply(bg)
        bg = bg.with_opacity(0.9)
        text_content = "节奏变化！\n" + (f"即将: {next_action}" if next_action else "")
        lines = text_content.count('\n') + 1
        txt = TextClip(
            text=text_content, font_size=100, color='white', font=FONT_PATH, method='caption',
            size=(int(VIDEO_WIDTH * 0.9), int(100 * lines * 1.6)), text_align='center',
            horizontal_align='center', vertical_align='center',
            stroke_color='black', stroke_width=3
        ).with_duration(duration).with_start(start).with_position('center')
        return [bg, txt]
    
    def create_preview_overlay(self, next_action, duration, start):
        overlay = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=(0, 0, 0), duration=duration).with_start(start).with_opacity(0.4)
        preview_text = f"NEXT\n{next_action}"
        preview_lines = preview_text.count('\n') + 1
        preview_txt = TextClip(
            text=preview_text, font_size=120, color='#FFD700', font=FONT_PATH,
            method='caption', size=(int(VIDEO_WIDTH * 0.9), int(120 * preview_lines * 1.6)), text_align='center',
            horizontal_align='center', vertical_align='center',
            stroke_color='black', stroke_width=4
        ).with_duration(duration).with_start(start).with_position('center')
        countdown_text = "▶▶▶ 准备切换 ▶▶▶"
        countdown_lines = countdown_text.count('\n') + 1
        countdown = TextClip(
            text=countdown_text, font_size=60, color='yellow', font=FONT_PATH,
            bg_color='black', method='caption', 
            size=(int(VIDEO_WIDTH * 0.9), int(60 * countdown_lines * 1.6)),
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
        
        print(f"🎬 总时长: {self.get_beat_time(current_beat):.1f}秒")
        
        for i, item in enumerate(timeline):
            row = item['row']
            start_beat = item['start_beat']
            end_beat = item['end_beat']
            idx_in_group = item['idx_in_group']
            start_time = self.get_beat_time(start_beat)
            end_time = self.get_beat_time(end_beat)
            duration = end_time - start_time
            
            action_name = str(row['ActionName'])
            type_num = int(row['Type'])
            main_hint = str(row['MainHint']) if pd.notna(row['MainHint']) else action_name
            sub_hint = str(row['SubHint']) if pd.notna(row['SubHint']) else ""
            is_preview = bool(row.get('IsPreview', False))
            next_action = str(row.get('NextActionName', '')) if pd.notna(row.get('NextActionName', '')) else ''
            rhythm_alert = bool(row.get('RhythmAlert', False))
            
            bg_color = get_type_color(type_num)
            text_color = get_text_color(type_num)
            
            print(f"  处理: {action_name} [{idx_in_group}/{type_num}] ({duration:.1f}s)")
            
            if rhythm_alert and i > 0:
                alert_start = self.get_beat_time(start_beat - ALERT_BEATS)
                alert_duration = start_time - alert_start
                if alert_duration > 0:
                    alert_clips = self.create_alert_clip(action_name, alert_duration, alert_start)
                    self.clips.extend(alert_clips)
            
            bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=bg_color, duration=duration).with_start(start_time)
            self.clips.append(bg)
            
            main_clip = self.create_text_clip(main_hint, 80, text_color, duration, start_time, 0.35)
            self.clips.append(main_clip)
            
            sub_display = f"{sub_hint}\n{idx_in_group}/{type_num}" if sub_hint else f"{idx_in_group}/{type_num}"
            sub_clip = self.create_text_clip(sub_display, 50, text_color, duration, start_time, 0.50)
            self.clips.append(sub_clip)
            
            if is_preview and next_action:
                preview_clips = self.create_preview_overlay(next_action, duration, start_time)
                self.clips.extend(preview_clips)
            elif idx_in_group == type_num - 1 and type_num >= 2 and i < len(timeline) - 1:
                next_row = timeline[i+1]['row']
                next_name = str(next_row['ActionName'])
                auto_preview_text = f"准备: {next_name}"
                auto_preview_lines = auto_preview_text.count('\n') + 1
                auto_preview = TextClip(
                    text=auto_preview_text, font_size=45, color='yellow', font=FONT_PATH,
                    bg_color='black', method='caption', 
                    size=(int(VIDEO_WIDTH * 0.9), int(45 * auto_preview_lines * 1.6)),
                    text_align='center', horizontal_align='center', vertical_align='center'
                ).with_duration(duration).with_start(start_time)
                auto_preview = auto_preview.with_position(('center', VIDEO_HEIGHT * 0.84))
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
    gen = FitnessVideoGenerator(music_path, excel_path, output_path)
    return gen.generate()

def main():
    print("=" * 60)
    print("🎬 健身团课视频生成器 - 竖屏完整版")
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
