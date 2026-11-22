import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from collections import defaultdict
import numpy as np

class ColorNameGenerator:
    def __init__(self):
        self.color_databases = {
            "RAL": {},
            "中国传统色": {},
            "CSS颜色": {},
            "国标颜色": {},
            "日本传统色": {},
            "NCS颜色": {},
            "Pantone颜色": {},
            "X11颜色": {}
        }
        self.combined_colors = {}
        self.output_colors = {}

    def load_color_databases(self):
        try:
            # 加载RAL颜色
            with open("ral_colors.json", "r", encoding="utf-8") as f:
                self.color_databases["RAL"] = json.load(f)
            
            # 加载中国传统色
            with open("chinese_colors.json", "r", encoding="utf-8") as f:
                self.color_databases["中国传统色"] = json.load(f)
            
            # 加载CSS颜色
            with open("css_colors.json", "r", encoding="utf-8") as f:
                css_colors = json.load(f)
                # 转换CSS颜色格式为统一格式
                self.color_databases["CSS颜色"] = {f"({rgb[0]}, {rgb[1]}, {rgb[2]})": name 
                                                 for name, rgb in css_colors.items()}
            
            # 加载国标颜色
            with open("gb_colors.json", "r", encoding="utf-8") as f:
                gb_colors = json.load(f)
                # 转换国标颜色格式为统一格式
                self.color_databases["国标颜色"] = {f"({rgb[0]}, {rgb[1]}, {rgb[2]})": f"{info['name']} (GB-{key.split('-')[1]}-{key.split('-')[2]})" 
                                                  for key, info in gb_colors.items() 
                                                  if 'rgb' in info}
            
            # 加载日本传统色
            with open("japanese_colors.json", "r", encoding="utf-8") as f:
                jp_colors = json.load(f)
                # 转换日本传统色格式为统一格式
                self.color_databases["日本传统色"] = {f"({rgb[0]}, {rgb[1]}, {rgb[2]})": name 
                                                    for name, rgb in jp_colors.items()}
            
            # 加载NCS颜色
            with open("ncs_colors.json", "r", encoding="utf-8") as f:
                self.color_databases["NCS颜色"] = json.load(f)
            
            # 加载Pantone颜色
            with open("pantone_colors.json", "r", encoding="utf-8") as f:
                self.color_databases["Pantone颜色"] = json.load(f)
            
            # 加载X11颜色
            with open("x11_colors.json", "r", encoding="utf-8") as f:
                x11_colors = json.load(f)
                # 转换X11颜色格式为统一格式
                self.color_databases["X11颜色"] = {f"({rgb.split(', ')[0]}, {rgb.split(', ')[1]}, {rgb.split(', ')[2]})": name 
                                                 for rgb, name in x11_colors.items()}
            
            return True
        except Exception as e:
            print(f"加载颜色数据库时出错: {e}")
            return False

    def combine_colors(self):
        """合并所有颜色数据库，优先使用更具体的颜色名称"""
        color_dict = defaultdict(list)
        
        # 按照优先级顺序添加颜色数据库
        databases = [
            ("中国传统色", 1),
            ("日本传统色", 1),
            ("RAL", 1),
            ("Pantone颜色", 1),
            ("NCS颜色", 1),
            ("国标颜色", 1),
            ("CSS颜色", 1),
            ("X11颜色", 1)
        ]
        
        for db_name, weight in databases:
            if db_name in self.color_databases:
                for rgb, name in self.color_databases[db_name].items():
                    # 标准化RGB格式
                    if not rgb.startswith("("):
                        rgb = f"({rgb})"
                    color_dict[rgb].append((name, weight))
        
        # 对于每个RGB值，选择权重最高的名称
        self.combined_colors = {}
        for rgb, names in color_dict.items():
            # 按权重排序，相同权重时按名称长度排序（优先选择更具体的名称）
            names_sorted = sorted(names, key=lambda x: (-x[1], len(x[0])))
            self.combined_colors[rgb] = names_sorted[0][0]
        
        print(f"合并后共有 {len(self.combined_colors)} 种唯一颜色")

    def rgb_to_lab(self, rgb):
        """将RGB颜色转换为LAB颜色空间，用于计算颜色距离"""
        # 首先将RGB归一化到0-1范围
        r, g, b = rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0
        
        # 线性化RGB值
        r = r if r <= 0.04045 else ((r + 0.055)/1.055)**2.4
        g = g if g <= 0.04045 else ((g + 0.055)/1.055)**2.4
        b = b if b <= 0.04045 else ((b + 0.055)/1.055)**2.4
        
        # 转换为XYZ颜色空间
        x = r * 0.4124564 + g * 0.3575761 + b * 0.1804375
        y = r * 0.2126729 + g * 0.7151522 + b * 0.0721750
        z = r * 0.0193339 + g * 0.1191920 + b * 0.9503041
        
        # 参考白点(D65)
        x_ref, y_ref, z_ref = 0.95047, 1.00000, 1.08883
        
        # 归一化
        x = x / x_ref
        y = y / y_ref
        z = z / z_ref
        
        # 转换为LAB
        x = x if x > 0.008856 else (x * 903.3 + 16) / 116
        y = y if y > 0.008856 else (y * 903.3 + 16) / 116
        z = z if z > 0.008856 else (z * 903.3 + 16) / 116
        
        L = max(0, min(100, 116 * y - 16))
        a = 500 * (x - y)
        b = 200 * (y - z)
        
        return (L, a, b)

    def color_distance(self, rgb1, rgb2):
        """计算两个RGB颜色之间的CIEDE2000距离"""
        lab1 = self.rgb_to_lab(rgb1)
        lab2 = self.rgb_to_lab(rgb2)
        
        # 简化的欧几里得距离计算（实际CIEDE2000更复杂）
        return np.sqrt((lab1[0]-lab2[0])**2 + (lab1[1]-lab2[1])**2 + (lab1[2]-lab2[2])**2)

    def find_closest_color(self, target_rgb):
        """找到与目标RGB最接近的颜色名称"""
        min_distance = float('inf')
        closest_color = "未知颜色"
        closest_rgb = (0, 0, 0)
        
        # 将目标RGB转换为元组
        target_rgb_tuple = (int(target_rgb[0]), int(target_rgb[1]), int(target_rgb[2]))
        
        # 在合并的颜色中查找最接近的颜色
        for rgb_str, name in self.combined_colors.items():
            # 从字符串解析RGB值
            rgb_str = rgb_str.strip("()")
            rgb_parts = [x.strip() for x in rgb_str.split(",")]
            if len(rgb_parts) != 3:
                continue
                
            try:
                r = int(rgb_parts[0])
                g = int(rgb_parts[1])
                b = int(rgb_parts[2])
            except ValueError:
                continue
                
            current_rgb = (r, g, b)
            distance = self.color_distance(target_rgb_tuple, current_rgb)
            
            if distance < min_distance:
                min_distance = distance
                closest_color = name
                closest_rgb = current_rgb
        
        return closest_color, closest_rgb, min_distance

    def generate_full_color_map(self):
        """为所有可能的RGB值生成颜色名称映射"""
        self.output_colors = {}
        
        # 可以选择步长来减少计算量，这里设置为5以加快演示速度
        step = 5
        
        total_colors = (256//step)**3
        processed = 0
        
        for r in range(0, 256, step):
            for g in range(0, 256, step):
                for b in range(0, 256, step):
                    rgb_str = f"({r}, {g}, {b})"
                    closest_name, closest_rgb, _ = self.find_closest_color((r, g, b))
                    self.output_colors[rgb_str] = closest_name
                    
                    processed += 1
                    if processed % 1000 == 0:
                        print(f"处理进度: {processed}/{total_colors} ({processed/total_colors*100:.1f}%)")
        
        print(f"颜色映射生成完成，共 {len(self.output_colors)} 种颜色")

    def save_color_map(self, filename):
        """将颜色映射保存到JSON文件"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.output_colors, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False


class ColorGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RGB颜色名称生成器")
        self.root.geometry("800x600")
        
        self.generator = ColorNameGenerator()
        
        self.create_widgets()
    
    def create_widgets(self):
        # 顶部标题
        title_label = tk.Label(self.root, text="RGB颜色名称生成器", font=("微软雅黑", 16, "bold"))
        title_label.pack(pady=10)
        
        # 说明文本
        desc_label = tk.Label(self.root, text="本程序将根据提供的颜色数据库，为所有RGB值生成对应的中文颜色名称", 
                            font=("微软雅黑", 10))
        desc_label.pack(pady=5)
        
        # 进度条框架
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=10, fill=tk.X, padx=20)
        
        self.progress_label = tk.Label(progress_frame, text="准备就绪", font=("微软雅黑", 10))
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode="determinate")
        self.progress_bar.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(10, 0))
        
        # 操作按钮框架
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.load_button = tk.Button(button_frame, text="加载颜色数据库", command=self.load_databases, 
                                   font=("微软雅黑", 10), width=20)
        self.load_button.pack(side=tk.LEFT, padx=10)
        
        self.generate_button = tk.Button(button_frame, text="生成颜色映射", command=self.generate_colors, 
                                      font=("微软雅黑", 10), width=20, state=tk.DISABLED)
        self.generate_button.pack(side=tk.LEFT, padx=10)
        
        self.save_button = tk.Button(button_frame, text="保存颜色映射", command=self.save_colors, 
                                   font=("微软雅黑", 10), width=20, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=10)
        
        # 日志输出框
        log_frame = tk.Frame(self.root)
        log_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=20)
        
        log_label = tk.Label(log_frame, text="操作日志:", font=("微软雅黑", 10))
        log_label.pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 9), height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # 底部状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, 
                            anchor=tk.W, font=("微软雅黑", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log_message(self, message):
        """向日志框添加消息"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def load_databases(self):
        """加载颜色数据库"""
        self.log_message("正在加载颜色数据库...")
        self.update_status("正在加载颜色数据库...")
        self.progress_bar["value"] = 0
        self.root.update_idletasks()
        
        success = self.generator.load_color_databases()
        
        if success:
            self.log_message("颜色数据库加载成功!")
            self.log_message(f"加载的颜色系统数量: {len(self.generator.color_databases)}")
            
            # 统计每种系统的颜色数量
            for name, colors in self.generator.color_databases.items():
                self.log_message(f"{name}: {len(colors)} 种颜色")
            
            self.generate_button.config(state=tk.NORMAL)
            self.update_status("颜色数据库加载成功，可以生成颜色映射")
            self.progress_bar["value"] = 100
        else:
            self.log_message("颜色数据库加载失败，请检查文件是否存在")
            self.update_status("颜色数据库加载失败")
    
    def generate_colors(self):
        """生成颜色映射"""
        self.log_message("开始合并颜色数据库...")
        self.update_status("正在合并颜色数据库...")
        self.progress_bar["value"] = 0
        self.root.update_idletasks()
        
        # 合并颜色
        self.generator.combine_colors()
        self.log_message(f"合并后共有 {len(self.generator.combined_colors)} 种唯一颜色")
        
        self.log_message("开始生成完整的RGB颜色映射...")
        self.update_status("正在生成颜色映射...")
        self.progress_bar["value"] = 0
        self.root.update_idletasks()
        
        # 生成颜色映射
        self.generator.generate_full_color_map()
        
        self.log_message("颜色映射生成完成!")
        self.log_message(f"共生成 {len(self.generator.output_colors)} 种RGB颜色的名称")
        
        self.save_button.config(state=tk.NORMAL)
        self.update_status("颜色映射生成完成，可以保存结果")
        self.progress_bar["value"] = 100
    
    def save_colors(self):
        """保存颜色映射到文件"""
        filename = filedialog.asksaveasfilename(
            title="保存颜色映射文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if not filename:
            return
        
        self.log_message(f"正在保存颜色映射到文件: {filename}")
        self.update_status("正在保存文件...")
        self.progress_bar["value"] = 0
        self.root.update_idletasks()
        
        success = self.generator.save_color_map(filename)
        
        if success:
            self.log_message("颜色映射保存成功!")
            self.update_status(f"颜色映射已保存到 {filename}")
            self.progress_bar["value"] = 100
            messagebox.showinfo("保存成功", "颜色映射文件保存成功!")
        else:
            self.log_message("颜色映射保存失败!")
            self.update_status("保存文件时出错")
            messagebox.showerror("保存失败", "保存颜色映射文件时出错")


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorGeneratorApp(root)
    root.mainloop()