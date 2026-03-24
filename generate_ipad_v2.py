#!/usr/bin/env python3
"""
iPad 横屏视频生成器 - 完整版 (1920x1080)
支持批量处理多个音乐+Excel组合
"""
import librosa
import pandas as pd
import numpy as np
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, TextClip
import os
from typing import Tuple, List, Dict

# ==================== 批量处理配置 ====================
BATCH_CONFIGS = [
    {"music": "music/buttScaler23/01 I Just Might.mp3", "excel": "excel/butterScaler/butterScaler23.xlsx", "output": "butterScaler23_Section01_iPad.mp4"},
    {"music": "music/buttScaler23/02 02 ONE MORE TIME.mp3", "excel": "excel/butterScaler/butterScaler23.xlsx", "output": "butterScaler23_Section02_iPad.mp4"},
    {"music": "music/buttScaler23/06 06 Lose Control.mp3", "excel": "excel/butterScaler/butterScaler23_.xlsx", "output": "butterScaler23_Section06_iPad.mp4"},
]

DEFAULT_MUSIC_PATH = "music/buttScaler23/06 06 Lose Control.mp3"
DEFAULT_EXCEL_PATH = "excel/butterScaler/butterScaler23.xlsx"
OUTPUT_DIR = "output/buttScaler23"
FONT_PATH = "fonts/SourceHanSansHWSC-Bold.otf"
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
BEATS_PER_RHYTHM = 2

def get_type_color(type_num):
    color_map = {2: (255, 255, 255), 4: (255, 235, 59), 6: (255, 152, 0), 8: (244, 67, 54), 10: (156, 39, 176), 12: (63, 81, 181), 14: (0, 150, 136), 16: (76, 175, 80)}
    return color_map.get(type_num, (128, 128, 128))

def get_text_color(type_num):
    return 'black' if type_num in [2, 4, 6] else 'white'

def create_text_clip(text, fontsize, color, duration, start, pos_y):
    lines = text.count('\n') + 1
    return TextClip(text=text, font_size=fontsize, color=color, font=FONT_PATH, method='caption', size=(int(VIDEO_WIDTH * 0.8), int(fontsize * lines * 1.5)), text_align='center', horizontal_align='center', vertical_align='center').with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * pos_y))

class iPadVideoGenerator:
    def __init__(self, music_path, excel_path, output_path):
        self.music_path = music_path
        self.excel_path = excel_path
        self.output_path = output_path
        self.beat_times = None
        self.bpm = None
        self.clips = []
        
    def analyze_music(self):
        print(f"  Analyzing: {os.path.basename(self.music_path)}")
        y, sr = librosa.load(self.music_path, sr=None)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=128)
        self.bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
        self.beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        
    def get_beat_time(self, beat_idx):
        if beat_idx < 0:
            return self.beat_times[0] + beat_idx * (60/self.bpm) if len(self.beat_times) > 0 else 0
        if beat_idx < len(self.beat_times):
            return self.beat_times[beat_idx]
        return self.beat_times[-1] + (beat_idx - len(self.beat_times) + 1) * (60/self.bpm)

    def generate(self):
        self.analyze_music()
        df = pd.read_excel(self.excel_path)
        
        group_counters = {}
        current_group_id = None
        timeline = []
        current_beat = 0
        
        for idx, row in df.iterrows():
            rhythms = int(row['Rhythms'])
            beats = rhythms * BEATS_PER_RHYTHM
            type_num = int(row['Type'])
            action_name = str(row['ActionName'])
            group_key = f"{action_name}_{type_num}"
            
            if group_key != current_group_id:
                current_group_id = group_key
                group_counters[current_group_id] = 0
            group_counters[current_group_id] += 1
            idx_in_group = group_counters[current_group_id]
            
            start_beat = current_beat
            end_beat = start_beat + beats
            timeline.append({'row': row, 'start_beat': start_beat, 'end_beat': end_beat, 'idx_in_group': idx_in_group})
            current_beat = end_beat
        
        for item in timeline:
            row = item['row']
            start_time = self.get_beat_time(item['start_beat'])
            end_time = self.get_beat_time(item['end_beat'])
            duration = end_time - start_time
            idx_in_group = item['idx_in_group']
            
            type_num = int(row['Type'])
            main_hint = str(row['MainHint']) if pd.notna(row['MainHint']) else str(row['ActionName'])
            sub_hint = str(row['SubHint']) if pd.notna(row['SubHint']) else ""
            
            bg_color = get_type_color(type_num)
            text_color = get_text_color(type_num)
            
            bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=bg_color, duration=duration).with_start(start_time)
            self.clips.append(bg)
            
            self.clips.append(create_text_clip(main_hint, 80, text_color, duration, start_time, 0.35))
            
            sub_display = f"{sub_hint}\n{idx_in_group}/{type_num}" if sub_hint else f"{idx_in_group}/{type_num}"
            self.clips.append(create_text_clip(sub_display, 50, text_color, duration, start_time, 0.55))
        
        final = CompositeVideoClip(self.clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        audio = AudioFileClip(self.music_path).subclipped(0, final.duration)
        final = final.with_audio(audio)
        
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        final.write_videofile(self.output_path, fps=30, codec='libx264', audio_codec='aac', temp_audiofile='temp-audio.m4a', remove_temp=True, threads=4)

def main():
    print("=" * 60)
    print("iPad Video Generator - Batch Mode")
    print("=" * 60)
    
    if BATCH_CONFIGS:
        for i, config in enumerate(BATCH_CONFIGS, 1):
            print(f"\n[{i}/{len(BATCH_CONFIGS)}] Processing...")
            if not os.path.exists(config["music"]) or not os.path.exists(config["excel"]):
                print(f"  Skipped: File not found")
                continue
            try:
                gen = iPadVideoGenerator(config["music"], config["excel"], os.path.join(OUTPUT_DIR, config["output"]))
                gen.generate()
                print(f"  Done: {config['output']}")
            except Exception as e:
                print(f"  Error: {e}")
    else:
        output_name = "ipad_video.mp4"
        gen = iPadVideoGenerator(DEFAULT_MUSIC_PATH, DEFAULT_EXCEL_PATH, os.path.join(OUTPUT_DIR, output_name))
        gen.generate()

if __name__ == "__main__":
    main()
