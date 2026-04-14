# AutoILD - 基于Python的间质性肺病（ILD）分类系统

## 项目简介

AutoILD是一个基于规则的医疗文本分类系统，专门用于自动分类间质性肺病(ILD)相关的出院诊断文本。该系统能够识别多种ILD亚型，包括：

- 结缔组织病相关ILD (CTD-ILD)
- 特发性肺纤维化 (IPF)
- 结节病
- 肺泡蛋白沉积症
- 淋巴细胞性间质性肺炎
- IgG4相关疾病
- 闭塞性细支气管炎
- 机化性肺炎
- 过敏性肺炎
- 具有自身免疫特征的间质性肺病 (IPAF)
- 快速进展型ILD
- 肺移植相关ILD
- 药物相关性ILD
- 尘肺/职业性ILD

## 核心功能

- **自动分类**：根据标准化的医学规则自动分类ILD诊断
- **多标签识别**：支持同一患者多条诊断的同时分类
- **详细输出**：提供分类结果的详细信息，包括匹配的关键词和优先级
- **批量处理**：支持Excel文件的批量处理
- **可配置性**：规则库可根据临床需求进行扩展和修改

## 技术特点

- **基于规则**：使用医学专家制定的规则进行分类，确保准确性
- **优先级机制**：通过优先级排序解决诊断重叠问题
- **文本清洗**：自动处理诊断文本中的噪声和格式问题
- **多诊断拆分**：智能识别和拆分多条诊断记录
- **非ILD过滤**：自动识别和过滤非ILD相关诊断

## 安装说明

### 环境要求

- Python 3.8+ 
- pandas 2.0.0+
- openpyxl 3.1.0+

### 安装步骤

1. **克隆项目**
   ```bash
   git clone <项目地址>
   cd 诊断规则聚类算法
   ```

2. **安装依赖**
   ```bash
   make install
   # 或手动安装
   pip install -r requirements.txt
   ```

## 使用方法

### 命令行模式

```bash
# 基本用法
python main.py --input data/input/出院诊断.xlsx --output data/output/分类结果.xlsx

# 详细输出模式
python main.py --input data/input/出院诊断.xlsx --output data/output/分类结果.xlsx --detail data/output/详细分类.json --verbose

# 只处理前N条记录（用于测试）
python main.py --input data/input/出院诊断.xlsx --output data/output/分类结果.xlsx --sample 10
```

### GUI模式

```bash
# 运行图形界面
python gui.py
```

### 参数说明

- `--input, -i`：输入Excel文件路径（必填）
- `--output, -o`：输出Excel文件路径
- `--detail, -d`：输出详细分类信息（JSON格式）
- `--name-col`：姓名列名（默认：姓名）
- `--diagnosis-col`：诊断列名（默认：出院诊断）
- `--verbose, -v`：显示详细处理信息
- `--sample`：只处理前N条记录（用于测试）

### 示例输出

**Excel输出**：包含姓名和各个ILD类别的分类结果

**JSON详细输出**：包含完整的分类信息，包括：
- 原始诊断文本
- 分类结果（按类别）
- 其他非ILD诊断
- 未匹配的诊断
- 匹配详情（包含匹配的关键词和优先级）

## 项目结构

```
├── config/            # 配置文件
├── data/              # 数据目录
│   ├── input/         # 输入数据
│   └── output/        # 输出结果
├── src/               # 源代码
│   ├── pipeline/      # 核心处理流程
│   ├── rules/         # 分类规则定义
│   └── utils/         # 工具函数
├── tests/             # 测试文件
├── main.py            # 主入口
├── gui.py             # GUI界面
├── Makefile           # 项目管理命令
├── pyproject.toml     # 项目配置
└── requirements.txt   # 依赖列表
```

## 规则库扩展

要扩展或修改分类规则，可编辑 `src/rules/ild_categories.py` 文件：

1. **添加新类别**：在 `ILD_CATEGORIES` 列表中添加新的 `CategoryRule` 对象
2. **修改现有规则**：调整关键词、优先级或排除词
3. **更新输出列**：在 `OUTPUT_COLUMNS` 中添加或调整列顺序
4. **添加非ILD关键词**：在 `NON_ILD_KEYWORDS` 中添加新的排除词

## 测试

```bash
# 运行所有测试
make test

# 快速功能测试
make quick-test
```

## 代码质量

```bash
# 运行代码检查
make lint
```

## 数据格式要求

输入Excel文件应包含以下列：
- **姓名**：患者姓名
- **出院诊断**：出院诊断文本（支持多行、编号等格式）

## 性能指标

- **处理速度**：约1000条记录/分钟
- **准确率**：基于规则的分类，准确率高
- **召回率**：覆盖常见ILD类型

## 应用场景

- **临床研究**：快速筛选和分类ILD患者
- **医院管理**：辅助统计和分析ILD疾病分布
- **科研数据处理**：标准化ILD诊断数据
- **临床决策支持**：提供初步的诊断分类参考

## 注意事项

1. 系统基于规则匹配，对于复杂或模糊的诊断文本可能需要人工审核
2. 规则库需要定期更新以适应医学术语的变化
3. 对于边缘案例，建议结合临床专业知识进行判断

## 许可证

MIT License

## 联系信息

- 项目名称：AutoILD
- 项目维护：Medical AI Team
- 版本：1.0.0
- 最后更新：2026-04-14
