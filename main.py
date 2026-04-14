"""
ILD分类器主入口

使用方法:
    python main.py --input data/input/出院诊断.xlsx --output data/output/分类结果.xlsx
    python main.py --input data/input/出院诊断.xlsx --detail data/output/详细分类.json
"""

import argparse
import sys
import json
from pathlib import Path
import pandas as pd

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline.classifier import ILDClassifier


def main():
    parser = argparse.ArgumentParser(
        description="间质性肺病(ILD)诊断分类器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s -i 出院诊断.xlsx -o 分类结果.xlsx
  %(prog)s -i 出院诊断.xlsx -d 详细分类.json --verbose
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入Excel文件路径"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出Excel文件路径"
    )
    
    parser.add_argument(
        "-d", "--detail",
        help="输出详细分类信息(JSON格式)"
    )
    
    parser.add_argument(
        "--name-col",
        default="姓名",
        help="姓名列名 (默认: 姓名)"
    )
    
    parser.add_argument(
        "--diagnosis-col",
        default="出院诊断",
        help="诊断列名 (默认: 出院诊断)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细处理信息"
    )
    
    parser.add_argument(
        "--sample",
        type=int,
        help="只处理前N条记录（用于测试）"
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 输入文件不存在: {input_path}")
        sys.exit(1)
    
    # 读取数据
    try:
        df = pd.read_excel(input_path)
        print(f"读取数据: {len(df)} 条记录")
        
        if args.sample:
            df = df.head(args.sample)
            print(f"使用样本: 前 {args.sample} 条")
            
    except Exception as e:
        print(f"错误: 读取Excel失败: {e}")
        sys.exit(1)
    
    # 初始化分类器
    classifier = ILDClassifier()
    
    # 执行分类
    print("\\n开始分类...")
    result_df = classifier.classify_dataframe(
        df, 
        name_col=args.name_col,
        diagnosis_col=args.diagnosis_col
    )
    
    # 统计信息
    print("\\n分类统计:")
    for col in result_df.columns[1:]:  # 跳过姓名列
        count = (result_df[col] != "").sum()
        if count > 0:
            print(f"  {col}: {count} 例")
    
    # 保存Excel结果
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_excel(output_path, index=False)
        print(f"\\n 结果已保存: {output_path}")
    
    # 保存详细分类信息
    if args.detail:
        details = []
        for _, row in df.iterrows():
            name = row.get(args.name_col, "")
            diagnosis = row.get(args.diagnosis_col, "")
            detail = classifier.get_classification_details(name, diagnosis)
            details.append(detail)
        
        detail_path = Path(args.detail)
        detail_path.parent.mkdir(parents=True, exist_ok=True)
        with open(detail_path, "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        print(f" 详细信息已保存: {detail_path}")
    
    # 详细输出
    if args.verbose:
        print("\\n详细分类示例（前3条）:")
        for i, (_, row) in enumerate(df.head(3).iterrows()):
            name = row.get(args.name_col, "")
            diagnosis = row.get(args.diagnosis_col, "")
            detail = classifier.get_classification_details(name, diagnosis)
            
            print(f"\\n[{i+1}] {name}")
            print(f"  原始: {diagnosis[:80]}...")
            print(f"  分类: ", end="")
            cats = [k for k, v in detail["分类结果"].items() if v]
            print(", ".join(cats) if cats else "未分类")
    
    print("\\n完成!")


if __name__ == "__main__":
    main()