"""
ILD 分类器核心引擎
基于规则的医疗文本分类系统
"""

import re
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
import sys

from rules.ild_categories import (
    ILD_CATEGORIES, 
    OUTPUT_COLUMNS, 
    NON_ILD_KEYWORDS
)

sys.path.append(str(Path(__file__).parent.parent))


@dataclass
class MatchResult:
    """匹配结果"""
    category: str
    matched_terms: List[str]
    matched_text: str
    priority: int


class ILDPatternMatcher:
    """ILD模式匹配器"""
    
    def __init__(self):
        self.categories = ILD_CATEGORIES
        self.non_ild_keywords = NON_ILD_KEYWORDS
        
    def clean_text(self, text: str) -> str:
        """清洗诊断文本"""
        if pd.isna(text):
            return ""
        # 移除标记符号
        text = str(text)
        text = re.sub(r'[\*\?]', '', text)
        # 标准化空格
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def split_diagnoses(self, text: str) -> List[str]:
        """将多行诊断拆分为单个诊断项"""
        # 按数字序号或换行分割
        items = re.split(r'\d+\.|\\n|<br/?>', text)
        items = [item.strip() for item in items if item.strip()]
        return items
    
    def match_category(self, text: str, rule) -> Optional[MatchResult]:
        """
        匹配单个类别
        返回匹配结果或None
        """
        matched_terms = []
        
        # 检查排除词
        for exclude in rule.exclude_keywords or []:
            # 对于结节病，避免"结节"排除"结节病"
            if rule.name == "结节病" and exclude == "结节" and "结节病" in text:
                continue
            if exclude in text:
                return None
        
        # 检查关键词（按优先级顺序）
        for keyword in rule.keywords:
            if keyword in text:
                matched_terms.append(keyword)
        
        if matched_terms:
            return MatchResult(
                category=rule.name,
                matched_terms=matched_terms,
                matched_text=text,
                priority=rule.priority
            )
        return None
    
    def classify_single_item(self, item: str) -> Tuple[Optional[MatchResult], bool]:
        """
        对单个诊断项进行分类
        返回: (匹配结果, 是否为非ILD)
        """
        # 首先按优先级顺序匹配ILD类别
        for rule in sorted(self.categories, key=lambda x: x.priority):
            result = self.match_category(item, rule)
            if result:
                return result, False
        
        # 如果没有匹配到ILD类别，再检查是否为非ILD
        for keyword in self.non_ild_keywords:
            if keyword in item:
                return None, True
        
        # 既不是ILD也不是非ILD，返回未匹配
        return None, False
    
    def classify(self, diagnosis_text: str) -> Dict[str, any]:
        """
        对完整诊断文本进行分类
        
        返回结构:
        {
            "categories": {类别名: 匹配到的原始文本列表},
            "other": [未匹配的诊断列表],
            "details": [详细匹配信息]
        }
        """
        text = self.clean_text(diagnosis_text)
        items = self.split_diagnoses(text)
        
        result = {
            "categories": defaultdict(list),
            "other": [],
            "details": []
        }
        
        # 跟踪已匹配的文本，避免重复
        matched_items = set()
        
        for item in items:
            if not item or item in matched_items:
                continue
                
            # 按优先级顺序匹配ILD类别
            matched = False
            for rule in sorted(self.categories, key=lambda x: x.priority):
                match_result = self.match_category(item, rule)
                if match_result:
                    category = match_result.category
                    result["categories"][category].append({
                        "original": item,
                        "matched_terms": match_result.matched_terms
                    })
                    result["details"].append({
                        "original": item,
                        "category": category,
                        "priority": match_result.priority,
                        "matched_terms": match_result.matched_terms
                    })
                    matched_items.add(item)
                    matched = True
                    break
            
            # 如果没有匹配到任何ILD类别，归为其他
            if not matched:
                result["other"].append(item)
                matched_items.add(item)
        
        return result


class ILDClassifier:
    """ILD分类器主类"""
    
    def __init__(self):
        self.matcher = ILDPatternMatcher()
        self.output_columns = OUTPUT_COLUMNS
    
    def classify_patient(self, name: str, diagnosis: str) -> Dict[str, str]:
        """
        对单个患者进行分类
        
        返回标准化的输出字典
        """
        result = self.matcher.classify(diagnosis)
        
        # 构建输出行
        output = {"姓名": name}
        
        # 填充各个类别列
        for col in self.output_columns[1:-1]:  # 排除"姓名"和"其他"
            if col in result["categories"]:
                # 合并该类别下的所有匹配项
                items = result["categories"][col]
                texts = [item["original"] for item in items]
                output[col] = "；".join(texts)
            else:
                output[col] = ""
        
        # 填充"其他"列
        if result["other"]:
            output["其他"] = "；".join(result["other"])
        else:
            output["其他"] = ""
        
        return output
    
    def classify_dataframe(self, df: pd.DataFrame, 
                          name_col: str = "姓名",
                          diagnosis_col: str = "出院诊断") -> pd.DataFrame:
        """
        对DataFrame批量分类
        """
        results = []
        
        for _, row in df.iterrows():
            name = row.get(name_col, "")
            diagnosis = row.get(diagnosis_col, "")
            
            classified = self.classify_patient(name, diagnosis)
            results.append(classified)
        
        # 按指定列顺序输出
        result_df = pd.DataFrame(results)
        
        # 确保列顺序
        available_cols = [col for col in self.output_columns if col in result_df.columns]
        result_df = result_df[available_cols]
        
        return result_df
    
    def get_classification_details(self, name: str, diagnosis: str) -> Dict:
        """
        获取详细分类信息（用于调试和验证）
        """
        result = self.matcher.classify(diagnosis)
        return {
            "姓名": name,
            "原始诊断": diagnosis,
            "分类结果": dict(result["categories"]),
            "其他诊断": result["other"],
            "未匹配": result["unmatched"],
            "匹配详情": result["details"]
        }