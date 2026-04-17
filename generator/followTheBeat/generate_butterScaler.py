#!/usr/bin/env python3
"""
butterScaler23 批量视频生成器
调用 generate_ipad.py 中的 process_single 完成批量任务
"""

import os
import sys
from generate_ipad import process_single

# ==================== butterScaler23 批量处理配置 ====================
BATCH_CONFIGS = [
    # {
    #     "music": "../../music/buttScaler23/01 I Just Might.mp3",
    #     "excel": "../../excel/butterScaler/butterScaler23-Section01.xlsx",
    #     "output": "butterScaler23_Section01_iPad.mp4"
    # },
    {
        "music": "../../music/buttScaler23/02 02 ONE MORE TIME.mp3",
        "excel": "../../excel/butterScaler/butterScaler23-Section02.xlsx",
        "output": "butterScaler23_Section02_iPad.mp4"
    },
    {
        "music": "../../music/buttScaler23/03 03 Hold Up.mp3",
        "excel": "../../excel/butterScaler/butterScaler23-Section03.xlsx",
        "output": "butterScaler23_Section03_iPad.mp4"
    },
    {
        "music": "../../music/buttScaler23/04 04 Perfect.mp3",
        "excel": "../../excel/butterScaler/butterScaler23-Section04.xlsx",
        "output": "butterScaler23_Section04_iPad.mp4"
    },
    {
        "music": "../../music/buttScaler23/05 05 I WANT IT.mp3",
        "excel": "../../excel/butterScaler/butterScaler23-Section05.xlsx",
        "output": "butterScaler23_Section05_iPad.mp4"
    },
    {
        "music": "../../music/buttScaler23/06 06 Lose Control.mp3",
        "excel": "../../excel/butterScaler/butterScaler23-Section06.xlsx",
        "output": "butterScaler23_Section06_iPad.mp4"
    },
    # {
    #     "music": "../../music/buttScaler23/07 07 Fame is a Gun.mp3",
    #     "excel": "../../excel/butterScaler/butterScaler23-Section07.xlsx",
    #     "output": "butterScaler23_Section07_iPad.mp4"
    # },
    # {
    #     "music": "../../music/buttScaler23/08 08 南京恋爱通告.mp3",
    #     "excel": "../../excel/butterScaler/butterScaler23-Section08.xlsx",
    #     "output": "butterScaler23_Section08_iPad.mp4"
    # },
    # {
    #     "music": "../../music/buttScaler23/09 B06 Spring Girl.mp3",
    #     "excel": "../../excel/butterScaler/butterScaler23-Section09.xlsx",
    #     "output": "butterScaler23_Section09_iPad.mp4"
    # },
]


def main():
    preview = 'preview' in sys.argv[1:]
    print("=" * 60)
    print("🎬 butterScaler23 批量生成器 (iPad 横屏 1920x1080)")
    if preview:
        print("👁️ 预览模式: 只生成前 60 秒")
    print("=" * 60)

    if not BATCH_CONFIGS:
        print("⚠️ BATCH_CONFIGS 为空，请在脚本中配置任务列表")
        return

    print(f"\n📋 批量处理模式: 共 {len(BATCH_CONFIGS)} 个任务")
    print("=" * 60)

    for i, config in enumerate(BATCH_CONFIGS, 1):
        print(f"\n[{i}/{len(BATCH_CONFIGS)}] 开始处理...")
        print("-" * 40)

        music_path = config["music"]
        excel_path = config["excel"]
        output_name = config["output"]

        if preview:
            base, ext = os.path.splitext(output_name)
            output_name = f"{base}_preview{ext}"

        if not os.path.exists(music_path):
            print(f"⚠️ 跳过: 音乐文件不存在 {music_path}")
            continue
        if not os.path.exists(excel_path):
            print(f"⚠️ 跳过: Excel文件不存在 {excel_path}")
            continue

        try:
            process_single(music_path, excel_path, output_name, preview=preview)
            print(f"✅ [{i}/{len(BATCH_CONFIGS)}] 完成: {output_name}")
        except Exception as e:
            print(f"❌ [{i}/{len(BATCH_CONFIGS)}] 失败: {e}")
            continue

    print("\n" + "=" * 60)
    print("🎉 批量处理完成!")


if __name__ == "__main__":
    main()
