# SplitPicture

Python 图片分割工具

## 功能

- 将大图片按照网格分割成多个小图片
- 支持交互式调整分割线位置
- 支持 PNG、JPG、BMP、GIF 等常见图片格式

## 文件说明

- `split_islands.py` - 基础分割脚本，通过代码配置分割参数
- `interactive_splitter.py` - 交互式 GUI 分割工具，支持手动调整分割线

## 依赖

```bash
pip install Pillow
```

GUI 工具需要 tkinter（通常 Python 自带）

## 使用方法

### 方法一：命令行分割

编辑 `split_islands.py` 中的配置：

```python
images = [
    ("your_image.png", 4, 5),  # 4行5列
]
```

然后运行：

```bash
python split_islands.py
```

### 方法二：交互式分割

```bash
python interactive_splitter.py
```

操作步骤：
1. 点击"选择图片"导入图片
2. 设置行数和列数
3. 拖动分割线调整位置
4. 点击"预览分割"查看效果
5. 点击"保存分割"导出所有小图片

## License

MIT