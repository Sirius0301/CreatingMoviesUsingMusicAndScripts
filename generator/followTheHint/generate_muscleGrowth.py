#!/usr/bin/env python3
"""
muscleGrowth14 批量视频生成器
调用 generate_hint_video.py 中的 process_single 完成批量任务
"""

import os
import sys

from generate_hint_video import process_single, MARKDOWN_DIR

# ==================== muscleGrowth14 批量处理配置 ====================
BATCH_CONFIGS = [
    {"md": "T1-热身.md"},
    {"md": "T2-下肢.md"},
    {"md": "T3-上肢1.md"},
    {"md": "T4-上肢2.md"},
    {"md": "T5-上肢3.md"},
    {"md": "T6-拉伸.md"},
]


def main():
    preview = 'preview' in sys.argv[1:]
    print("=" * 60)
    print("🎬 muscleGrowth14 批量生成器 (iPad 横屏 1920x1080)")
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

        md_file = config["md"]
        md_path = os.path.join(MARKDOWN_DIR, md_file)

        if not os.path.exists(md_path):
            print(f"⚠️ 跳过: Markdown 文件不存在 {md_path}")
            continue

        try:
            process_single(md_path, preview=preview)
            print(f"✅ [{i}/{len(BATCH_CONFIGS)}] 完成: {md_file}")
        except Exception as e:
            print(f"❌ [{i}/{len(BATCH_CONFIGS)}] 失败: {e}")
            continue

    print("\n" + "=" * 60)
    print("🎉 批量处理完成!")


if __name__ == "__main__":
    main()
