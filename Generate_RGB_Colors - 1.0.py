import json

def generate_rgb_colors():
    """生成从(0,0,0)到(255,255,255)的所有RGB颜色"""
    colors = {}
    
    # 可以选择步长来减少生成的数据量，这里设为1生成所有颜色
    step = 1
    
    for r in range(0, 256, step):
        for g in range(0, 256, step):
            for b in range(0, 256, step):
                rgb_key = f"({r},{g},{b})"
                colors[rgb_key] = f"RGB({r},{g},{b})"
    
    return colors

def save_to_json(data, filename):
    """将数据保存为JSON文件"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"颜色数据已保存到 {filename}")

if __name__ == "__main__":
    # 生成所有RGB颜色
    rgb_colors = generate_rgb_colors()
    print(f"共生成 {len(rgb_colors)} 种RGB颜色")
    
    # 保存为JSON文件
    output_file = "rgb_colors.json"
    save_to_json(rgb_colors, output_file)
