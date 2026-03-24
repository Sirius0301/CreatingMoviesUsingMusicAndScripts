#!/usr/bin/env python3
"""
生成 1分钟预览视频（前16个8拍）- 竖屏 1080x1920
支持使用临时文件 temp-audio.m4a 和 temp-excel.xlsx
"""
import librosa
import pandas as pd
import numpy as np
from moviepy import AudioFileClip, ColorClip, CompositeVideoClip, TextClip
import os
from typing import Tuple

# ==================== 配置 ====================
# 优先使用临时文件（如果存在），否则使用默认文件
TEMP_MUSIC_PATH = "temp-audio.m4a"  # 临时音乐文件
TEMP_EXCEL_PATH = "temp-excel.xlsx"  # 临时Excel文件

DEFAULT_MUSIC_PATH = "music/buttScaler23/06 06 Lose Control.mp3"
DEFAULT_EXCEL_PATH = "excel/butterScaler/butterScaler23.xlsx"
OUTPUT_DIR = "output/buttScaler23"
FONT_PATH = "fonts/SourceHanSansHWSC-Bold.otf"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
BEATS_PER_RHYTHM = 2
MAX_8BEATS = 16

def get_music_path():
    """获取音乐文件路径，优先使用临时文件"""
    if os.path.exists(TEMP_MUSIC_PATH):
        print(f"  使用临时音乐: {TEMP_MUSIC_PATH}")
        return TEMP_MUSIC_PATH
    print(f"  使用默认音乐: {DEFAULT_MUSIC_PATH}")
    return DEFAULT_MUSIC_PATH

def get_excel_path():
    """获取Excel文件路径，优先使用临时文件"""
    if os.path.exists(TEMP_EXCEL_PATH):
        print(f"  使用临时Excel: {TEMP_EXCEL_PATH}")
        return TEMP_EXCEL_PATH
    print(f"  使用默认Excel: {DEFAULT_EXCEL_PATH}")
    return DEFAULT_EXCEL_PATH

def get_type_color(type_num: int) -> Tuple[int, int, int]:
    color_map = {
        2: (255, 255, 255), 4: (255, 235, 59), 6: (255, 152, 0),
        8: (244, 67, 54), 10: (156, 39, 176), 12: (63, 81, 181),
        14: (0, 150, 136), 16: (76, 175, 80),
    }
    return color_map.get(type_num, (128, 128, 128))

def get_text_color(type_num: int) -> str:
    return 'black' if type_num in [2, 4, 6] else 'white'

def create_text_clip(text, fontsize, color, duration, start, pos_y):
    """修复字体显示问题 - 明确指定文本区域高度"""
    lines = text.count('\n') + 1
    return TextClip(
        text=text, font_size=fontsize, color=color, font=FONT_PATH,
        method='caption', size=(int(VIDEO_WIDTH * 0.85), int(fontsize * lines * 1.5)),
        text_align='center', horizontal_align='center', vertical_align='center'
    ).with_duration(duration).with_start(start).with_position(('center', VIDEO_HEIGHT * pos_y))

def main():
    print("=" * 50)
    print(" Preview Generator (1 minute, 16 x 8 beats)")
    print("=" * 50)
    
    # 获取文件路径
    music_path = get_music_path()
    excel_path = get_excel_path()
    
    if not os.path.exists(music_path):
        print(f"Error: Music file not found: {music_path}")
        return
    if not os.path.exists(excel_path):
        print(f"Error: Excel file not found: {excel_path}")
        return
    
    print("\nAnalyzing audio...")
    y, sr = librosa.load(music_path, sr=None)
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=128)
    bpm = float(tempo[0]) if hasattr(tempo, '__len__') else float(tempo)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    print(f"  BPM: {bpm:.1f}")
    
    def get_beat_time(beat_idx):
        if beat_idx < 0:
            return beat_times[0] + beat_idx * (60/bpm) if len(beat_times) > 0 else 0
        if beat_idx < len(beat_times):
            return beat_times[beat_idx]
        return beat_times[-1] + (beat_idx - len(beat_times) + 1) * (60/bpm)
    
    df = pd.read_excel(excel_path)
    target_beats = MAX_8BEATS * 8
    current_beat = 0
    filtered_rows = []
    
    for idx, row in df.iterrows():
        rhythms = int(row['Rhythms'])
        beats = rhythms * BEATS_PER_RHYTHM
        if current_beat >= target_beats:
            break
        filtered_rows.append({
            'row': row,
            'start_beat': current_beat,
            'end_beat': min(current_beat + beats, target_beats)
        })
        current_beat += beats
    
    print(f"  Generating {len(filtered_rows)} segments")
    
    clips = []
    group_counters = {}
    current_group_id = None
    
    for i, item in enumerate(filtered_rows):
        row = item['row']
        start_beat = item['start_beat']
        end_beat = item['end_beat']
        start_time = get_beat_time(start_beat)
        end_time = get_beat_time(end_beat)
        duration = end_time - start_time
        
        action_name = str(row['ActionName'])
        type_num = int(row['Type'])
        main_hint = str(row['MainHint']) if pd.notna(row['MainHint']) else action_name
        sub_hint = str(row['SubHint']) if pd.notna(row['SubHint']) else ""
        
        group_key = f"{action_name}_{type_num}"
        if group_key != current_group_id:
            current_group_id = group_key
            group_counters[current_group_id] = 0
        group_counters[current_group_id] += 1
        idx_in_group = group_counters[current_group_id]
        
        bg_color = get_type_color(type_num)
        text_color = get_text_color(type_num)
        
        bg = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=bg_color, duration=duration).with_start(start_time)
        clips.append(bg)
        
        main_clip = create_text_clip(main_hint, 60, text_color, duration, start_time, 0.35)
        clips.append(main_clip)
        
        progress_text = f"{idx_in_group}/{type_num}"
        sub_display = f"{sub_hint}\n{progress_text}" if sub_hint else progress_text
        sub_clip = create_text_clip(sub_display, 40, text_color, duration, start_time, 0.55)
        clips.append(sub_clip)
    
    print("Rendering...")
    final = CompositeVideoClip(clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    audio = AudioFileClip(music_path).subclipped(0, min(60, final.duration))
    final = final.with_audio(audio)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, "preview.mp4")
    
    final.write_videofile(output_path, fps=30, codec='libx264', audio_codec='aac',
                         temp_audiofile='temp-audio.m4a', remove_temp=True, threads=4)
    print(f"Done: {output_path}")

if __name__ == "__main__":
    main()
