#!/usr/bin/env python3
"""
岛屿图片分割脚本
将包含多个岛屿的图片分割成独立的岛屿图片
"""

from PIL import Image
import os

def split_islands(image_path, rows, cols, output_dir, start_index=1):
    """
    将图片分割成多个小图片
    
    Args:
        image_path: 原图片路径
        rows: 行数
        cols: 列数
        output_dir: 输出目录
        start_index: 起始编号
    """
    # 打开图片
    img = Image.open(image_path)
    width, height = img.size
    
    # 计算每个岛屿的尺寸
    island_width = width // cols
    island_height = height // rows
    
    print(f"\n处理图片: {os.path.basename(image_path)}")
    print(f"  原图尺寸: {width}x{height}")
    print(f"  网格: {rows}行x{cols}列")
    print(f"  岛屿尺寸: {island_width}x{island_height}")
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    count = 0
    for row in range(rows):
        for col in range(cols):
            # 计算裁剪区域
            left = col * island_width
            top = row * island_height
            right = left + island_width
            bottom = top + island_height
            
            # 裁剪图片
            island = img.crop((left, top, right, bottom))
            
            # 保存岛屿图片
            output_path = os.path.join(output_dir, f"island_{start_index + count:03d}.png")
            island.save(output_path)
            count += 1
    
    print(f"  已分割: {count}个岛屿")
    return count

def main():
    # 设置路径
    input_dir = "/home/supertaotao/.openclaw/workspace/temp/islands"
    output_dir = "/home/supertaotao/.openclaw/workspace/temp/islands/output"
    
    # 图片配置：(文件名, 行数, 列数)
    images = [
        ("Copilot_20260309_092850.png", 4, 5),  # 4行5列 = 20个
        ("Copilot_20260309_092858.png", 5, 5),  # 5行5列 = 25个
        ("Copilot_20260309_093321.png", 5, 5),  # 5行5列 = 25个
    ]
    
    print("="*60)
    print("🏝️  岛屿图片分割工具")
    print("="*60)
    
    total = 0
    for idx, (filename, rows, cols) in enumerate(images):
        image_path = os.path.join(input_dir, filename)
        if os.path.exists(image_path):
            start_index = total + 1
            count = split_islands(image_path, rows, cols, output_dir, start_index)
            total += count
        else:
            print(f"\n⚠️  图片不存在: {filename}")
    
    print("\n" + "="*60)
    print(f"✅ 分割完成！")
    print(f"   总计分割: {total}个岛屿")
    print(f"   输出目录: {output_dir}")
    print("="*60)
    
    # 列出部分输出文件
    output_files = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])
    print(f"\n前10个文件:")
    for f in output_files[:10]:
        print(f"  - {f}")
    if len(output_files) > 10:
        print(f"  ... 还有 {len(output_files) - 10} 个文件")

if __name__ == "__main__":
    main()
