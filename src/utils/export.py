"""
导出工具模块
支持多种格式导出和统计报告生成
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter


class ClassificationReporter:
    """分类报告生成器"""
    
    def __init__(self, result_df: pd.DataFrame):
        self.df = result_df
        self.categories = [col for col in result_df.columns if col != "姓名"]
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成分类汇总统计"""
        summary = {
            "total_patients": len(self.df),
            "categories": {}
        }
        
        for cat in self.categories:
            if cat == "其他":
                continue
            count = (self.df[cat] != "").sum()
            summary["categories"][cat] = {
                "count": int(count),
                "percentage": round(count / len(self.df) * 100, 2)
            }
        
        # 统计多标签患者
        multi_label_count = 0
        for _, row in self.df.iterrows():
            ild_cats = [cat for cat in self.categories 
                       if cat != "其他" and row[cat] != ""]
            if len(ild_cats) > 1:
                multi_label_count += 1
        
        summary["multi_label_patients"] = multi_label_count
        summary["multi_label_percentage"] = round(
            multi_label_count / len(self.df) * 100, 2
        )
        
        return summary
    
    def generate_cooccurrence_matrix(self) -> pd.DataFrame:
        """生成类别共现矩阵"""
        ild_cats = [cat for cat in self.categories if cat != "其他"]
        matrix = pd.DataFrame(0, index=ild_cats, columns=ild_cats)
        
        for _, row in self.df.iterrows():
            present_cats = [cat for cat in ild_cats if row[cat] != ""]
            for cat1 in present_cats:
                for cat2 in present_cats:
                    matrix.loc[cat1, cat2] += 1
        
        return matrix
    
    def export_summary_report(self, output_path: Path):
        """导出汇总报告"""
        summary = self.generate_summary()
        matrix = self.generate_cooccurrence_matrix()
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 汇总表
            summary_df = pd.DataFrame([
                {
                    "类别": cat,
                    "病例数": info["count"],
                    "占比(%)": info["percentage"]
                }
                for cat, info in summary["categories"].items()
            ])
            summary_df.to_excel(writer, sheet_name="分类汇总", index=False)
            
            # 共现矩阵
            matrix.to_excel(writer, sheet_name="类别共现矩阵")
            
            # 统计信息
            stats_df = pd.DataFrame([{
                "总病例数": summary["total_patients"],
                "多标签病例数": summary["multi_label_patients"],
                "多标签占比(%)": summary["multi_label_percentage"]
            }])
            stats_df.to_excel(writer, sheet_name="统计信息", index=False)
        
        return summary


class DetailedExporter:
    """详细分类信息导出器"""
    
    @staticmethod
    def export_json(details: List[Dict], output_path: Path):
        """导出JSON格式详细分类"""
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def export_markdown(details: List[Dict], output_path: Path):
        """导出Markdown格式报告"""
        lines = ["# ILD分类详细报告\\n"]
        
        for detail in details:
            lines.append(f"## {detail['姓名']}\\n")
            lines.append(f"**原始诊断**: {detail['原始诊断']}\\n\\n")
            
            lines.append("**分类结果**:\\n")
            for cat, items in detail["分类结果"].items():
                if items:
                    lines.append(f"- **{cat}**: {', '.join([i['original'] for i in items])}\\n")
            
            if detail["其他诊断"]:
                lines.append(f"\\n**其他诊断**: {', '.join(detail['其他诊断'])}\\n")
            
            if detail["未匹配"]:
                lines.append(f"\\n**未匹配**: {', '.join(detail['未匹配'])}\\n")
            
            lines.append("\\n---\\n\\n")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)