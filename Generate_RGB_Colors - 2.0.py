import json

def generate_and_save_rgb_colors(filename, step=10):
    """逐步生成并保存RGB颜色到JSON文件"""
    with open(filename, 'w') as f:
        f.write('{')
        first = True
        
        for r in range(0, 256, step):
            #print(f"[DEBUG] 正在生成红色值 {r}")
            for g in range(0, 256, step):
                #print(f"[DEBUG] 正在生成绿色值 {g}")
                for b in range(0, 256, step):
                    #print(f"[DEBUG] 正在生成蓝色值 {b}")
                    if not first:
                        f.write(',')
                    first = False
                    
                    rgb_key = f'"({r},{g},{b})"'
                    #print(f"[DEBUG] 正在写入颜色键 {rgb_key}")
                    rgb_value = f'"RGB({r},{g},{b})"'
                    #print(f"[DEBUG] 正在写入颜色值 {rgb_value}")
                    f.write(f'{rgb_key}:{rgb_value}')
                    #print(f"[DEBUG] 已写入颜色键值对 {rgb_key}:{rgb_value}")
        
        f.write('}')
    
    print(f"颜色数据已保存到 {filename}")

if __name__ == "__main__":
    output_file = "rgb_colors_large.json"
    generate_and_save_rgb_colors(output_file, step=1)
