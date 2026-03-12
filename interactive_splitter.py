#!/usr/bin/env python3
"""
交互式图片分割工具
支持手动调整分割线位置
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os

class ImageSplitter:
    def __init__(self, root):
        self.root = root
        self.root.title("🏝️ 岛屿图片分割工具")
        self.root.geometry("1400x900")
        
        # 变量
        self.image_path = None
        self.original_image = None
        self.display_image = None
        self.tk_image = None
        self.rows = tk.IntVar(value=5)
        self.cols = tk.IntVar(value=5)
        
        # 分割线位置（相对于图片尺寸的比例）
        self.h_lines = []  # 水平线位置 (0-1)
        self.v_lines = []  # 垂直线位置 (0-1)
        
        # 拖拽状态
        self.dragging = None
        self.drag_start = None
        
        # 显示比例
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        self.setup_ui()
        
    def setup_ui(self):
        """创建UI界面"""
        # 顶部控制面板
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # 文件选择
        ttk.Button(control_frame, text="📁 选择图片", command=self.load_image).pack(side=tk.LEFT, padx=5)
        
        # 网格设置
        ttk.Label(control_frame, text="行数:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Spinbox(control_frame, from_=1, to=20, textvariable=self.rows, width=5, 
                   command=self.update_grid).pack(side=tk.LEFT)
        
        ttk.Label(control_frame, text="列数:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Spinbox(control_frame, from_=1, to=20, textvariable=self.cols, width=5,
                   command=self.update_grid).pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="🔄 重置分割线", command=self.reset_lines).pack(side=tk.LEFT, padx=20)
        
        # 操作按钮
        ttk.Button(control_frame, text="👁️ 预览分割", command=self.preview_split).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="💾 保存分割", command=self.save_split).pack(side=tk.LEFT, padx=5)
        
        # 缩放控制
        ttk.Label(control_frame, text="缩放:").pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(control_frame, text="➕", command=lambda: self.zoom(1.2), width=3).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="➖", command=lambda: self.zoom(0.8), width=3).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="适应", command=self.fit_to_window, width=6).pack(side=tk.LEFT, padx=5)
        
        # 主画布
        canvas_frame = ttk.Frame(self.root)
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#2b2b2b', highlightthickness=1, 
                               highlightbackground='#555')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 绑定事件
        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Motion>', self.on_move)
        self.canvas.bind('<MouseWheel>', self.on_scroll)
        self.canvas.bind('<Button-4>', lambda e: self.zoom(1.1))  # Linux滚轮
        self.canvas.bind('<Button-5>', lambda e: self.zoom(0.9))
        
        # 底部状态栏
        self.status_var = tk.StringVar(value="请选择图片文件")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 说明面板
        help_frame = ttk.LabelFrame(self.root, text="操作说明", padding="5")
        help_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        help_text = """
        📌 操作步骤：
        1. 点击"选择图片"导入图片
        2. 设置行数和列数
        3. 拖动分割线调整位置（鼠标悬停在线上会高亮显示）
        4. 点击"预览分割"查看效果
        5. 点击"保存分割"导出所有小图片
        
        🖱️ 鼠标操作：
        • 左键拖动分割线：调整位置
        • 滚轮：缩放图片
        • 拖动空白区域：平移图片
        """
        ttk.Label(help_frame, text=help_text, justify=tk.LEFT).pack()
        
    def load_image(self):
        """加载图片"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("所有文件", "*.*")
            ]
        )
        
        if not file_path:
            return
            
        try:
            self.image_path = file_path
            self.original_image = Image.open(file_path)
            self.status_var.set(f"已加载: {os.path.basename(file_path)} ({self.original_image.size[0]}x{self.original_image.size[1]})")
            
            # 初始化分割线
            self.reset_lines()
            
            # 适应窗口
            self.fit_to_window()
            
        except Exception as e:
            messagebox.showerror("错误", f"无法加载图片:\n{str(e)}")
    
    def reset_lines(self):
        """重置分割线到均匀位置"""
        rows = self.rows.get()
        cols = self.cols.get()
        
        # 创建均匀分布的分割线
        self.h_lines = [i / rows for i in range(1, rows)]
        self.v_lines = [i / cols for i in range(1, cols)]
        
        self.draw_image()
    
    def update_grid(self):
        """更新网格（保持现有线的相对位置）"""
        if self.original_image:
            self.reset_lines()
    
    def fit_to_window(self):
        """适应窗口大小"""
        if not self.original_image:
            return
            
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 10 or canvas_height < 10:
            canvas_width = 1000
            canvas_height = 600
        
        img_width, img_height = self.original_image.size
        
        # 计算缩放比例
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.scale = min(scale_x, scale_y) * 0.95  # 留一点边距
        
        # 居中
        self.offset_x = (canvas_width - img_width * self.scale) / 2
        self.offset_y = (canvas_height - img_height * self.scale) / 2
        
        self.draw_image()
    
    def zoom(self, factor):
        """缩放图片"""
        self.scale *= factor
        self.scale = max(0.1, min(10, self.scale))  # 限制缩放范围
        self.draw_image()
    
    def draw_image(self):
        """绘制图片和分割线"""
        if not self.original_image:
            return
            
        self.canvas.delete("all")
        
        # 计算显示尺寸
        img_width, img_height = self.original_image.size
        display_width = int(img_width * self.scale)
        display_height = int(img_height * self.scale)
        
        # 调整图片大小
        self.display_image = self.original_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        
        # 绘制图片
        self.canvas.create_image(self.offset_x, self.offset_y, 
                                anchor=tk.NW, image=self.tk_image, tags="image")
        
        # 绘制分割线
        self.draw_lines()
        
    def draw_lines(self, highlight_h=None, highlight_v=None):
        """绘制分割线"""
        if not self.original_image:
            return
            
        img_width, img_height = self.original_image.size
        
        # 清除旧的线
        self.canvas.delete("line")
        
        # 绘制水平线
        for i, pos in enumerate(self.h_lines):
            y = self.offset_y + pos * img_height * self.scale
            color = '#ffff00' if i == highlight_h else '#00ff00'
            width = 3 if i == highlight_h else 2
            self.canvas.create_line(
                self.offset_x, y, 
                self.offset_x + img_width * self.scale, y,
                fill=color, width=width, tags=f"line hline_{i}"
            )
            # 显示位置百分比
            self.canvas.create_text(
                self.offset_x - 30, y,
                text=f"{pos*100:.1f}%",
                fill='#00ff00', font=('Arial', 9), tags="line"
            )
        
        # 绘制垂直线
        for i, pos in enumerate(self.v_lines):
            x = self.offset_x + pos * img_width * self.scale
            color = '#ffff00' if i == highlight_v else '#ff0000'
            width = 3 if i == highlight_v else 2
            self.canvas.create_line(
                x, self.offset_y,
                x, self.offset_y + img_height * self.scale,
                fill=color, width=width, tags=f"line vline_{i}"
            )
            # 显示位置百分比
            self.canvas.create_text(
                x, self.offset_y - 15,
                text=f"{pos*100:.1f}%",
                fill='#ff0000', font=('Arial', 9), tags="line"
            )
    
    def find_nearest_line(self, x, y, threshold=10):
        """找到最近的分割线"""
        if not self.original_image:
            return None, None
            
        img_width, img_height = self.original_image.size
        
        # 检查水平线
        for i, pos in enumerate(self.h_lines):
            line_y = self.offset_y + pos * img_height * self.scale
            if abs(y - line_y) < threshold:
                return 'h', i
        
        # 检查垂直线
        for i, pos in enumerate(self.v_lines):
            line_x = self.offset_x + pos * img_width * self.scale
            if abs(x - line_x) < threshold:
                return 'v', i
        
        return None, None
    
    def on_click(self, event):
        """鼠标点击"""
        line_type, line_idx = self.find_nearest_line(event.x, event.y)
        if line_type:
            self.dragging = (line_type, line_idx)
            self.drag_start = (event.x, event.y)
    
    def on_drag(self, event):
        """鼠标拖动"""
        if not self.original_image:
            return
            
        if self.dragging:
            line_type, line_idx = self.dragging
            img_width, img_height = self.original_image.size
            
            if line_type == 'h':
                # 水平线
                new_pos = (event.y - self.offset_y) / (img_height * self.scale)
                new_pos = max(0.01, min(0.99, new_pos))  # 限制范围
                self.h_lines[line_idx] = new_pos
            else:
                # 垂直线
                new_pos = (event.x - self.offset_x) / (img_width * self.scale)
                new_pos = max(0.01, min(0.99, new_pos))
                self.v_lines[line_idx] = new_pos
            
            self.draw_image()
            self.status_var.set(f"调整分割线: {line_type.upper()}{line_idx+1} = {new_pos*100:.1f}%")
    
    def on_release(self, event):
        """鼠标释放"""
        self.dragging = None
        self.drag_start = None
    
    def on_move(self, event):
        """鼠标移动"""
        if not self.original_image:
            return
            
        line_type, line_idx = self.find_nearest_line(event.x, event.y)
        
        if line_type:
            if line_type == 'h':
                self.draw_lines(highlight_h=line_idx)
            else:
                self.draw_lines(highlight_v=line_idx)
            self.canvas.config(cursor='fleur')
        else:
            self.canvas.config(cursor='arrow')
    
    def on_scroll(self, event):
        """鼠标滚轮缩放"""
        if event.delta > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)
    
    def get_crop_regions(self):
        """获取裁剪区域"""
        if not self.original_image:
            return []
            
        img_width, img_height = self.original_image.size
        
        # 添加边界
        h_positions = [0] + self.h_lines + [1]
        v_positions = [0] + self.v_lines + [1]
        
        regions = []
        for i in range(len(h_positions) - 1):
            for j in range(len(v_positions) - 1):
                # 计算像素坐标
                left = int(v_positions[j] * img_width)
                right = int(v_positions[j + 1] * img_width)
                top = int(h_positions[i] * img_height)
                bottom = int(h_positions[i + 1] * img_height)
                
                regions.append((left, top, right, bottom))
        
        return regions
    
    def preview_split(self):
        """预览分割结果"""
        if not self.original_image:
            messagebox.showwarning("警告", "请先选择图片")
            return
        
        regions = self.get_crop_regions()
        
        # 创建预览窗口
        preview_window = tk.Toplevel(self.root)
        preview_window.title(f"预览 - 共{len(regions)}个区域")
        preview_window.geometry("1000x700")
        
        # 创建画布和滚动条
        canvas_frame = ttk.Frame(preview_window)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg='#2b2b2b')
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 计算网格布局
        cols = self.cols.get()
        thumb_size = 150
        padding = 10
        
        row_idx = 0
        col_idx = 0
        
        for idx, (left, top, right, bottom) in enumerate(regions):
            # 裁剪图片
            crop = self.original_image.crop((left, top, right, bottom))
            
            # 创建缩略图
            crop.thumbnail((thumb_size, thumb_size), Image.Resampling.LANCZOS)
            tk_crop = ImageTk.PhotoImage(crop)
            
            # 计算位置
            x = col_idx * (thumb_size + padding) + padding
            y = row_idx * (thumb_size + padding) + padding
            
            # 显示图片
            canvas.create_image(x, y, anchor=tk.NW, image=tk_crop, tags=f"img_{idx}")
            canvas.create_text(x + thumb_size//2, y + thumb_size + 5, 
                             text=f"#{idx+1}", fill='white', font=('Arial', 10))
            
            # 保持引用
            if not hasattr(canvas, 'images'):
                canvas.images = []
            canvas.images.append(tk_crop)
            
            # 更新位置
            col_idx += 1
            if col_idx >= cols:
                col_idx = 0
                row_idx += 1
        
        # 更新滚动区域
        total_rows = (len(regions) + cols - 1) // cols
        canvas.configure(scrollregion=(0, 0, 
                                       cols * (thumb_size + padding) + padding,
                                       total_rows * (thumb_size + padding) + padding))
        
        # 关闭按钮
        ttk.Button(preview_window, text="关闭", 
                  command=preview_window.destroy).pack(pady=10)
    
    def save_split(self):
        """保存分割结果"""
        if not self.original_image:
            messagebox.showwarning("警告", "请先选择图片")
            return
        
        # 选择保存目录
        save_dir = filedialog.askdirectory(title="选择保存目录")
        if not save_dir:
            return
        
        # 获取裁剪区域
        regions = self.get_crop_regions()
        
        # 创建子目录
        base_name = os.path.splitext(os.path.basename(self.image_path))[0]
        output_dir = os.path.join(save_dir, f"{base_name}_split")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            # 裁剪并保存
            for idx, (left, top, right, bottom) in enumerate(regions):
                crop = self.original_image.crop((left, top, right, bottom))
                output_path = os.path.join(output_dir, f"{base_name}_{idx+1:03d}.png")
                crop.save(output_path, 'PNG')
            
            messagebox.showinfo("成功", 
                              f"已保存 {len(regions)} 张图片到:\n{output_dir}")
            
            # 打开输出目录
            os.system(f'xdg-open "{output_dir}"' if os.name != 'nt' else f'explorer "{output_dir}"')
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败:\n{str(e)}")

def main():
    root = tk.Tk()
    app = ImageSplitter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
