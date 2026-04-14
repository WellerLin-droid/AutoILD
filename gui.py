#!/usr/bin/env python3
"""
ILD分类器GUI界面
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import threading
import time
from pathlib import Path
import sys

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.classifier import ILDClassifier


class ILDClassifierGUI:
    """ILD分类器GUI类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("ILD分类器")
        
        # 适配高DPI
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
        # 设置窗口最大化
        self.root.state('zoomed')
        
        # 初始化变量
        self.input_file = None
        self.result_df = None
        self.classifier = ILDClassifier()
        
        # 设置主题颜色
        self.bg_color = "#2d2d2d"
        self.text_color = "#e0e0e0"
        self.button_bg = "#404040"
        self.button_hover = "#555555"
        self.accent_color = "#4CAF50"
        
        # 设置窗口背景
        self.root.configure(bg=self.bg_color)
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 设置样式
        self.setup_styles()
        
        # 创建初始界面
        self.create_initial_screen()
    
    def setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 配置框架
        style.configure('TFrame', background=self.bg_color)
        
        # 配置标签
        style.configure('TLabel', 
                      background=self.bg_color, 
                      foreground=self.text_color,
                      font=('Segoe UI', 18))
        
        # 配置按钮
        style.configure('TButton', 
                      background=self.button_bg,
                      foreground=self.text_color,
                      font=('Segoe UI', 18, 'bold'),
                      padding=20,
                      relief='flat')
        
        style.map('TButton', 
                 background=[('active', self.button_hover)],
                 foreground=[('active', self.accent_color)])
        
        # 配置进度条
        style.configure('TProgressbar', 
                      background=self.accent_color,
                      troughcolor=self.button_bg)
        
        # 配置树状表格
        style.configure('Treeview', 
                      background=self.bg_color,
                      foreground=self.text_color,
                      fieldbackground=self.bg_color,
                      font=('Segoe UI', 14))
        
        style.configure('Treeview.Heading', 
                      background=self.button_bg,
                      foreground=self.text_color,
                      font=('Segoe UI', 16, 'bold'))
        
        style.map('Treeview.Heading', 
                 background=[('active', self.button_hover)])
        
        # 配置滚动条
        style.configure('TScrollbar', 
                      background=self.button_bg,
                      troughcolor=self.bg_color)

    
    def create_initial_screen(self):
        """创建初始屏幕"""
        # 清空主框架
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        

        
        # 创建标题
        title_frame = ttk.Frame(self.main_frame)
        title_frame.pack(expand=True, fill=tk.BOTH, pady=50)
        
        title_label = ttk.Label(
            title_frame, 
            text="AutoILD",
            font=('Segoe UI', 48, 'bold'),
            foreground=self.accent_color
        )
        title_label.pack(pady=30)
        
        subtitle_label = ttk.Label(
            title_frame, 
            text="基于Python的间质性肺病（ILD）分类系统",
            font=('Segoe UI', 24)
        )
        subtitle_label.pack(pady=20)
        
        # 创建按钮框架
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(expand=True, fill=tk.BOTH)
        
        # 创建打开文件按钮
        open_button = ttk.Button(
            button_frame, 
            text="选择Excel文件", 
            command=self.open_file_dialog,
            style="TButton"
        )
        open_button.pack(pady=60, padx=400, ipady=25, ipadx=40)
        
        # 创建提示文本
        hint_label = ttk.Label(
            self.main_frame, 
            text="请选择包含出院诊断数据的Excel文件",
            font=('Segoe UI', 20, 'italic')
        )
        hint_label.pack(pady=30)
    
    def open_file_dialog(self):
        """打开文件对话框"""
        file_path = filedialog.askopenfilename(
            title="选择Excel文件",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            self.input_file = file_path
            self.show_loading_screen()
            # 在后台线程中处理数据
            threading.Thread(target=self.process_data).start()
    
    def show_loading_screen(self):
        """显示加载屏幕"""
        # 清空主框架
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建加载界面
        loading_frame = ttk.Frame(self.main_frame)
        loading_frame.pack(expand=True, fill=tk.BOTH)
        
        # 创建标题
        loading_label = ttk.Label(
            loading_frame, 
            text="正在分析数据...",
            font=('Segoe UI', 28, 'bold')
        )
        loading_label.pack(pady=40)
        
        # 创建副标题
        detail_label = ttk.Label(
            loading_frame, 
            text="正在处理诊断数据，请稍候...",
            font=('Segoe UI', 20)
        )
        detail_label.pack(pady=20)
        
        # 创建进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            loading_frame, 
            variable=self.progress_var, 
            length=600, 
            mode='indeterminate'
        )
        progress_bar.pack(pady=40, padx=200)
        progress_bar.start()
        
        # 创建状态信息
        status_label = ttk.Label(
            loading_frame, 
            text="正在读取文件...",
            font=('Segoe UI', 16, 'italic')
        )
        status_label.pack(pady=20)
    
    def process_data(self):
        """处理数据"""
        try:
            # 读取Excel文件
            df = pd.read_excel(self.input_file)
            
            # 执行分类
            self.result_df = self.classifier.classify_dataframe(
                df, 
                name_col="姓名",
                diagnosis_col="出院诊断"
            )
            
            # 切换到结果界面
            self.root.after(0, self.show_result_screen)
            
        except Exception as e:
            error_message = f"处理数据时出错: {str(e)}"
            self.root.after(0, lambda: messagebox.showerror("错误", error_message))
            self.root.after(0, self.create_initial_screen)
    
    def show_result_screen(self):
        """显示结果屏幕"""
        # 清空主框架
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # 创建结果界面
        result_frame = ttk.Frame(self.main_frame)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部按钮栏
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(fill=tk.X, pady=10, padx=20)
        
        # 左侧按钮
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.pack(side=tk.LEFT)
        
        back_button = ttk.Button(
            left_button_frame, 
            text="返回", 
            command=self.create_initial_screen,
            style="TButton"
        )
        back_button.pack(side=tk.LEFT, padx=10)
        

        
        # 右侧按钮
        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.pack(side=tk.RIGHT)
        
        export_button = ttk.Button(
            right_button_frame, 
            text="导出结果", 
            command=self.export_results,
            style="TButton"
        )
        export_button.pack(side=tk.RIGHT, padx=10)
        
        # 创建标题
        title_frame = ttk.Frame(result_frame)
        title_frame.pack(fill=tk.X, pady=20, padx=20)
        
        title_label = ttk.Label(
            title_frame, 
            text="分类结果",
            font=('Segoe UI', 32, 'bold'),
            foreground=self.accent_color
        )
        title_label.pack(side=tk.LEFT)
        
        # 创建统计信息
        stats_frame = ttk.Frame(result_frame)
        stats_frame.pack(fill=tk.X, pady=15, padx=20)
        
        total_count = len(self.result_df)
        stats_label = ttk.Label(
            stats_frame, 
            text=f"共处理 {total_count} 条记录",
            font=('Segoe UI', 18)
        )
        stats_label.pack(side=tk.LEFT)
        
        # 创建表格框架
        table_frame = ttk.Frame(result_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=20)
        
        # 创建滚动条
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        
        # 创建表格
        self.tree = ttk.Treeview(
            table_frame, 
            columns=list(self.result_df.columns),
            show="headings",
            xscrollcommand=scrollbar_x.set,
            yscrollcommand=scrollbar_y.set
        )
        
        # 配置滚动条
        scrollbar_x.config(command=self.tree.xview)
        scrollbar_y.config(command=self.tree.yview)
        
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # 设置列标题和宽度
        column_widths = {
            "姓名": 100,
            "结缔组织病": 150,
            "特发性肺纤维化": 120,
            "淋巴细胞性": 100,
            "IgG": 80,
            "闭塞性": 100,
            "结节病": 80,
            "肺泡蛋白沉积症": 120,
            "间质性肺病伴有纤维化": 150,
            "具有自身免疫特征的间质性肺病": 180,
            "机化": 80,
            "其他": 200
        }
        
        for col in self.result_df.columns:
            self.tree.heading(col, text=col)
            width = column_widths.get(col, 100)
            self.tree.column(col, width=width, stretch=True)
        
        # 填充数据
        for _, row in self.result_df.iterrows():
            values = [str(row[col]) if pd.notna(row[col]) else "" for col in self.result_df.columns]
            self.tree.insert("", tk.END, values=values)
    
    def export_results(self):
        """导出结果"""
        if self.result_df is None:
            messagebox.showinfo("提示", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存结果",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.result_df.to_excel(file_path, index=False)
                messagebox.showinfo("成功", f"结果已导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = ILDClassifierGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
