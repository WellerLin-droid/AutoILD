# ============================================
# ILD 分类规则库（最终版 - 严格限定11分类）
# ============================================
# 分类依据：用户自定义11分类框架
# 逻辑策略：特异性诊断优先（1-7,9,10），描述性/未分类诊断兜底（8），其余归入其他（11）

import re
from typing import List, Dict, Optional, Tuple

class CategoryRule:
    def __init__(self, name: str, priority: int, keywords: List[str], 
                 exclude_keywords: List[str] = None, 
                 negative_phrases: List[str] = None):
        self.name = name
        self.priority = priority
        self.keywords = keywords
        self.exclude_keywords = exclude_keywords or []
        self.negative_phrases = negative_phrases or []

# ============================================
# 全局否定词配置
# ============================================
GLOBAL_NEGATIONS = [
    "排除", "除外", "不考虑", "未见", "无", "未诊断", "未发现",
    "待排", "待查", "？", "?", "可疑", "阴性", "无依据",
    "不支持", "可能性小", "暂不考虑", "需排除", "缺乏依据"
]

# 双重否定转肯定（不除外 = 考虑）
DOUBLE_NEGATION_POSITIVE = ["不除外", "不能排除", "不能完全排除", "尚不能排除"]

def is_negated(text: str, keyword: str, window: int = 25) -> bool:
    """检查关键词在上下文中是否被否定"""
    # 双重否定检查
    for double_neg in DOUBLE_NEGATION_POSITIVE:
        if double_neg in text:
            if abs(text.find(double_neg) - text.find(keyword)) < window * 2:
                return False
    
    match = re.search(re.escape(keyword), text)
    if not match:
        return False
    
    start, end = match.span()
    prefix = text[max(0, start - window): start]
    
    for neg in GLOBAL_NEGATIONS:
        if neg in prefix:
            return True
    return False

# ============================================
# 11 类 ILD 分类规则定义（优先级经过精密调校）
# ============================================

ILD_CATEGORIES: List[CategoryRule] = [
    
    # ---------------------------------------------------------
    # 1: 结缔组织病相关ILD (CTD-ILD) - 最高优先级
    # ---------------------------------------------------------
    CategoryRule(
        name="结缔组织病",
        priority=1,
        keywords=[
            # 明确CTD诊断
            "结缔组织病", "结缔组织",
            "类风湿性关节炎", "类风湿性", "类风关", "RA",
            "皮肌炎", "多发性肌炎", "无肌病性皮肌炎", "临床无肌病性皮肌炎",
            "抗MDA5阳性皮肌炎", "抗MDA5抗体阳性皮肌炎", "MDA5皮肌炎",
            "干燥综合征", "舍格伦", "Sjogren", "SS",
            "系统性硬化症", "硬皮病", "全身性硬皮病", "SSc",
            "系统性红斑狼疮", "SLE", "狼疮",
            "混合性结缔组织病", "MCTD", "Sharp综合征",
            "未分化结缔组织病", "UCTD",
            "重叠综合征", "重叠症候群",
            
            # 抗合成酶综合征
            "抗合成酶综合征", "抗合成酶抗体综合征", "ASS", "ASS-ILD",
            "抗Jo-1", "抗Jo1", "Jo-1抗体", "Jo1抗体",
            "抗EJ", "EJ抗体", "抗PL-7", "PL-7抗体", "抗PL7",
            "抗PL-12", "PL-12抗体", "抗PL12", "抗OJ", "OJ抗体",
            "抗KS", "KS抗体", "抗Zo", "Zo抗体", "抗HA", "HA抗体",
            
            # 其他肌炎/CTD相关抗体
            "抗Mi-2", "抗TIF1γ", "抗TIF1", "抗NXP2", "抗SAE", "抗SRP", "抗HMGCR",
            "抗Ro52", "Ro52抗体", "抗Ku", "Ku抗体",
            "抗PM-Scl", "PM-Scl抗体", "抗PM-Scl75", "抗PM-Scl100",
            "抗U1RNP", "U1RNP抗体", "抗RNP", "抗Sm", "Sm抗体",
            "抗SSA", "SSA抗体", "抗Ro", "抗SSB", "SSB抗体", "抗La",
            "抗Scl-70", "Scl-70抗体", "抗拓扑异构酶",
            "抗着丝点", "着丝点抗体", "ACA",
            "抗RNA聚合酶III", "RNA聚合酶III抗体",
            "抗核抗体阳性", "ANA阳性", "高滴度ANA",
            
            # 血管炎相关
            "血管炎", "ANCA相关性血管炎", "AAV",
            "显微镜下多血管炎", "MPA", "肉芽肿性多血管炎", "GPA", "韦格纳",
            "嗜酸性肉芽肿性多血管炎", "EGPA", "Churg-Strauss",
            "抗MPO抗体", "MPO-ANCA", "p-ANCA",
            "抗PR3抗体", "PR3-ANCA", "c-ANCA",
            
            # 其他自身免疫病
            "免疫检查点抑制剂相关性", "ICI相关", "irAE肺炎",
            "抗磷脂综合征", "APS", "复发性多软骨炎",
            
            # 相关性描述
            "结缔组织相关性", "结缔组织病相关性", "CTD相关",
            "结缔组织病继发", "结缔组织病合并", "自身免疫病相关",
            "自身免疫性间质性肺病",  # 泛指自身免疫性ILD，通常指向CTD
        ],
        exclude_keywords=[
            "具有自身免疫特征", "自身免疫特征", "IPAF",  # 归入第9类
            "未分类", "未分型", "家族史", "既往史", "病史",
            "待排除", "可能", "不除外",  # 不确定描述不归入此类
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 2: 特发性肺纤维化 (IPF)
    # ---------------------------------------------------------
    CategoryRule(
        name="特发性肺纤维化",
        priority=2,
        keywords=[
            "特发性肺纤维化", "特发性肺间质纤维化", "IPF",
            "普通型间质性肺炎", "UIP型", "UIP pattern", "UIP/IPF", "IPF/UIP",
            "特发性UIP", "idiopathic UIP",
            "IPF急性加重", "AE-IPF", "IPF-AE",
            "特发性肺纤维化急性加重",
        ],
        exclude_keywords=[
            "继发", "结缔组织", "类风湿", "皮肌炎", "抗合成酶", "血管炎",
            "自身免疫", "IPAF", 
            "可能UIP", "倾向UIP", "不确定UIP",  # 不确定诊断不归入IPF
            "家族性", "NSIP", "机化", "急性", "AIP",
            "蜂窝肺",  # 蜂窝肺是描述，如果单独出现不一定是IPF，但结合UIP模式可考虑
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 3: 淋巴细胞性间质性肺炎 (LIP)
    # ---------------------------------------------------------
    CategoryRule(
        name="淋巴细胞性",
        priority=3,
        keywords=[
            "淋巴细胞性间质性肺炎", "淋巴细胞性间质性肺病",
            "LIP", "LIP样", "淋巴细胞间质性肺炎", "淋巴样间质性肺炎",
            "滤泡性细支气管炎",
        ],
        exclude_keywords=[
            "淋巴瘤", "淋巴增殖", "白血病", "结缔组织",  # CTD相关LIP仍归入CTD
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 4: IgG4相关疾病 (IgG4-RD)
    # ---------------------------------------------------------
    CategoryRule(
        name="IgG",
        priority=4,
        keywords=[
            "IgG4相关", "IgG4相关疾病", "IgG4-RD",
            "IgG4相关性肺病", "IgG4相关性", "IgG4阳性", "IgG4升高",
        ],
        exclude_keywords=[],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 5: 闭塞性细支气管炎 (OB / BOS)
    # ---------------------------------------------------------
    CategoryRule(
        name="闭塞性",
        priority=5,
        keywords=[
            "闭塞性细支气管炎", "闭塞性细支气管炎综合征",
            "BO", "BOS", "缩窄性细支气管炎",
            "弥漫性泛细支气管炎", "DPB", "移植后闭塞性细支气管炎",
        ],
        exclude_keywords=[
            "机化性肺炎", "BOOP",  # BOOP归入第10类
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 6: 结节病 (Sarcoidosis)
    # ---------------------------------------------------------
    CategoryRule(
        name="结节病",
        priority=6,
        keywords=[
            "结节病", "肺结节病", "系统性结节病",
            "Sarcoidosis", "sarcoid", "Lofgren", "Löfgren", "Heerfordt", "肉样瘤病",
        ],
        exclude_keywords=[
            "结节", "肿瘤", "癌", "转移", "矽肺", "尘肺",
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 7: 肺泡蛋白沉积症 (PAP)
    # ---------------------------------------------------------
    CategoryRule(
        name="肺泡蛋白沉积症",
        priority=7,
        keywords=[
            "肺泡蛋白沉积症", "肺泡蛋白沉着症",
            "PAP", "PAP综合征",
            "特发性肺泡蛋白沉积症", "自身免疫性肺泡蛋白沉积症",
            "继发性肺泡蛋白沉积症", "GM-CSF抗体", "GM-CSF自身抗体",
        ],
        exclude_keywords=[],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 8: 具有自身免疫特征的间质性肺病 (IPAF)
    # ---------------------------------------------------------
    CategoryRule(
        name="具有自身免疫特征的间质性肺病",
        priority=8,
        keywords=[
            "具有自身免疫特征",
            "具有自身免疫特征的间质性肺病",
            "具有自身免疫特征的间质性肺炎",
            "自身免疫特征性",
            "自身免疫特征",
            "自身免疫特征的间质性肺炎",
            "免疫特征性",
            "免疫特征",
            "免疫特征性间质性肺炎",
            "免疫特征性间质性肺病",
            "IPAF",
            "间质性肺炎伴自身免疫特征",
            "自身免疫倾向", "免疫介导倾向",
        ],
        exclude_keywords=[
            # 排除明确CTD，确保IPAF是排他性诊断
            "类风湿", "皮肌炎", "多发性肌炎", "无肌病性皮肌炎",
            "干燥综合征", "舍格伦", "系统性硬化", "硬皮病",
            "系统性红斑狼疮", "混合性结缔组织病", "未分化结缔组织病",
            "抗合成酶综合征", "抗Jo-1", "抗EJ", "抗PL-7", "抗PL-12",
            "血管炎", "ANCA",
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 9: 机化性肺炎 (OP)
    # ---------------------------------------------------------
    CategoryRule(
        name="机化",
        priority=9,
        keywords=[
            "机化性肺炎", "隐源性机化肺炎", "COP",
            "BOOP", "闭塞性细支气管炎伴机化性肺炎",
            "继发性机化肺炎", "SOP", "局灶性机化肺炎", "FOP",
            "机化性改变", "机化样改变",
        ],
        exclude_keywords=[
            "单纯闭塞性", "BOS",  # BOS归入第5类
            "COPD", "慢阻肺",  # 避免COPD被错误分类为机化
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
    
    # ---------------------------------------------------------
    # 10: 间质性肺病伴有纤维化
    # ---------------------------------------------------------
    CategoryRule(
        name="间质性肺病伴有纤维化",
        priority=12,  
        keywords=[
            # 明确伴有纤维化
            "间质性肺病伴有纤维化", "间质性肺炎伴有纤维化",
            "肺间质纤维化", "双肺间质纤维化", "肺纤维化", "弥漫性肺纤维化",
            "纤维化性间质性肺病", "纤维化性间质性肺炎",
            "进行性纤维化性间质性肺病", "PF-ILD", "进行性肺纤维化", "PPF",
            
            # 纤维化型NSIP
            "纤维化型NSIP", "纤维性NSIP",
        ],
        exclude_keywords=[
            # 排除所有已知特异性诊断的关键词，确保兜底纯净
            "结缔组织", "类风湿", "皮肌炎", "多发性肌炎", "干燥综合征",
            "系统性硬化", "系统性红斑狼疮", "抗合成酶", "MCTD", "UCTD",
            "血管炎", "ANCA", "IgG4",
            "过敏性肺炎", "HP", "农民肺", "饲鸟者肺", "加湿器肺",
            "药物性", "药源性", "胺碘酮", "甲氨蝶呤", "博来霉素",
            "放射性", "放疗后",
            "结节病", "肺泡蛋白", "LIP", "淋巴细胞性",
            "闭塞性", "DPB", "BOS",
            "机化性肺炎", "OP", "BOOP", "机化",
            "具有自身免疫特征", "IPAF", "自身免疫特征性",
            "特发性肺纤维化", "IPF", "特发性间质",
            "尘肺", "矽肺", "石棉肺", "煤工尘肺", "职业性",
            "LAM", "淋巴管平滑肌瘤病", "PLCH", "朗格汉斯", "DIP", "RB-ILD",
            "急性间质性肺炎", "AIP", "弥漫性肺泡损伤", "DAD",  # 急性期归入其他
            "呼吸衰竭", "心力衰竭",  # 排除并发症
        ],
        negative_phrases=GLOBAL_NEGATIONS,
    ),
]

# ============================================
# 非ILD诊断关键词（归入"其他"）
# ============================================
NON_ILD_KEYWORDS = [
    # 感染
    "肺炎", "肺部感染", "细菌性肺炎", "社区获得性肺炎", "CAP",
    "重症肺炎", "肺结核", "结核", "TB",
    "肺真菌感染", "肺曲霉病", "肺隐球菌病", "肺诺卡菌病", "NTM",
    "卡氏肺孢子菌肺炎", "PCP", "PJP", "巨细胞病毒性肺炎", "CMV肺炎",
    "新型冠状病毒感染", "COVID-19", "流感", "肺脓肿", "脓胸",
    
    # 急性间质性肺炎 / DAD（归入其他）
    "急性间质性肺炎", "AIP", "弥漫性肺泡损伤", "DAD",
    "Hamman-Rich综合征", "急性呼吸窘迫综合征", "ARDS",
    
    # 肿瘤
    "肺恶性肿瘤", "肺腺癌", "肺鳞状细胞癌", "肺癌",
    "小细胞肺癌", "非小细胞肺癌", "肺转移瘤", "肺结节", "肺占位", "肺肿块",
    "淋巴瘤", "胸腺瘤", "间皮瘤", "错构瘤",
    
    # 气道疾病
    "慢性阻塞性肺病", "COPD", "慢阻肺", "肺气肿",
    "支气管哮喘", "哮喘", "支气管扩张", "支扩",
    
    # 血管疾病
    "肺动脉高压", "肺心病", "肺栓塞", "PTE",
    
    # 其他肺部疾病
    "肺水肿", "肺大泡", "肺大疱", "气胸", "胸腔积液", "纵隔气肿",
    "肺出血", "尘肺", "矽肺", "石棉肺",
    
    # 心血管
    "高血压", "冠心病", "心绞痛", "心肌梗死", "心力衰竭", "心衰",
    "心律失常", "房颤",
    
    # 代谢/内分泌
    "糖尿病", "高脂血症", "高尿酸血症", "痛风", "甲亢", "甲减",
    
    # 其他系统
    "胃炎", "胃溃疡", "肝硬化", "肾功能不全", "脑梗死",
    "术后", "化疗后", "放疗后", "移植状态",
]

# ============================================
# 输出列定义
# ============================================
OUTPUT_COLUMNS = [
    "姓名",
    "结缔组织病",
    "特发性肺纤维化",
    "淋巴细胞性",
    "IgG",
    "闭塞性",
    "结节病",
    "肺泡蛋白沉积症",
    "间质性肺病伴有纤维化",
    "具有自身免疫特征的间质性肺病",
    "机化",
    "其他",
]

# ============================================
# 核心分类函数
# ============================================
def classify_ild(text: str) -> Tuple[str, Dict]:
    if not text:
        return "其他", {"reason": "空文本"}
    
    text_lower = text.lower()
    matched_category = None
    matched_keyword = None
    
    # 按优先级遍历ILD分类
    for category in sorted(ILD_CATEGORIES, key=lambda x: x.priority):
        for keyword in category.keywords:
            # 检查关键词是否在文本中
            # 对于特定英文关键词（如"SS"），使用正则表达式确保完整匹配
            # 对于其他关键词，直接检查子字符串
            match_found = False
            if keyword in text or keyword.lower() in text_lower:
                # 对于容易被误匹配的英文缩写，使用正则表达式确保完整匹配
                if keyword in ["SS", "RA", "SLE", "MCTD", "UCTD", "SSc", "IPF", "UIP", "LIP", "PAP", "BO", "BOS", "DPB", "IPAF", "NSIP", "ASS"]:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    pattern_lower = r'\b' + re.escape(keyword.lower()) + r'\b'
                    if re.search(pattern, text) or re.search(pattern_lower, text_lower):
                        match_found = True
                else:
                    match_found = True
            
            if match_found:
                # 排除检查 - 避免子字符串匹配导致的错误
                excluded = False
                for excl in category.exclude_keywords:
                    # 对于结节病，避免"结节"排除"结节病"
                    if category.name == "结节病" and excl == "结节" and "结节病" in text:
                        continue
                    # 对于特发性肺纤维化，避免"急性"排除"急性加重"
                    if category.name == "特发性肺纤维化" and excl == "急性" and "急性加重" in text:
                        continue
                    if excl in text:
                        excluded = True
                        break
                if excluded:
                    continue
                
                # 否定检查
                if is_negated(text, keyword):
                    continue
                
                matched_category = category
                matched_keyword = keyword
                break
        if matched_category:
            break
    
    if matched_category:
        return matched_category.name, {
            "matched_keyword": matched_keyword,
            "category": matched_category.name
        }
    
    # 所有不满足前10大分类的都属于其他
    return "其他", {"reason": "无匹配规则"}

def batch_classify(texts: List[str]) -> List[Dict[str, str]]:
    results = []
    for text in texts:
        category, info = classify_ild(text)
        row = {col: "" for col in OUTPUT_COLUMNS}
        if category in row:
            row[category] = "是"
        else:
            row["其他"] = "是"
        results.append(row)
    return results
