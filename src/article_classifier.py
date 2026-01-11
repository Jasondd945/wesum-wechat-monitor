"""
文章分类模块
使用 AI + 关键词判断文章类型和是否为干扰内容
"""

import json
import re
from typing import Dict, List


class ArticleClassifier:
    """文章分类器"""

    def __init__(self, noise_keywords: Dict[str, List[str]] = None):
        """
        初始化文章分类器

        Args:
            noise_keywords: 干扰类型的关键词字典
        """
        self.noise_keywords = noise_keywords or self._default_noise_keywords()

    def _default_noise_keywords(self) -> Dict[str, List[str]]:
        """默认的干扰关键词"""
        return {
            "招聘": ["招聘", "诚聘", "猎头", "职位", "JD", "简历", "应聘", "面试"],
            "带货": ["购买", "下单", "优惠", "限时", "折扣", "促销", "购买链接", "立即抢"],
            "广告": ["赞助", "广告", "品牌推广", "商业合作"],
            "课程": ["课程", "训练营", "扫码", "立减", "报名", "学习"],
            "社群": ["知识星球", "付费社群", "会员", "加入社群", "社群"],
            "活动推广": ["会议报名", "展会报名", "早鸟票", "活动报名", "立即报名", "报名开启"],
            "融资": ["融资", "轮融资", "估值", "投资方", "募资"],
            "公关": ["发布", "新品发布", "隆重推出", "盛大发布", "战略合作", "签署协议", "获奖"]
        }

    def classify(self, article: Dict) -> Dict:
        """
        分类文章（AI + 关键词辅助）

        Args:
            article: 文章信息（包含 title, content）

        Returns:
            分类结果字典：
            {
                "categories": ["AI", "芯片"],  # 3-5个分类标签
                "is_noise": false,              # 是否为干扰内容
                "noise_type": null,             # 干扰类型（招聘、带货等）
                "noise_level": null             # 干扰级别（noise/pr/light）
            }
        """
        title = article.get('title', '')
        content = article.get('content', '')

        # 步骤1：关键词匹配（辅助判断）
        keyword_result = self._match_keywords(title + content)

        # 步骤2：如果关键词匹配度高，直接判断
        if keyword_result['confidence'] > 0.8:
            return self._build_result(
                categories=keyword_result['categories'],
                is_noise=True,
                noise_type=keyword_result['noise_type'],
                noise_level=self._get_noise_level(keyword_result['noise_type'])
            )

        # 步骤3：正常文章，返回空标签（后续由 AI 生成）
        return {
            "categories": [],
            "is_noise": False,
            "noise_type": None,
            "noise_level": None
        }

    def _match_keywords(self, text: str) -> Dict:
        """
        关键词匹配

        Args:
            text: 文章标题+内容

        Returns:
            匹配结果
        """
        best_match_type = None
        best_match_count = 0
        best_match_total = 0

        for noise_type, keywords in self.noise_keywords.items():
            type_count = 0
            for keyword in keywords:
                if keyword in text:
                    type_count += 1
                    print(f"[DEBUG] Found keyword: '{keyword}' in type: {noise_type}")

            # 计算该类型的匹配率
            if type_count > 0:
                match_rate = type_count / len(keywords)
                print(f"[DEBUG] Type '{noise_type}': matched {type_count}/{len(keywords)} keywords, rate={match_rate:.2f}")

                # 如果这个类型的匹配数更多，或者匹配率更高，则更新最佳匹配
                if type_count > best_match_count or (type_count == best_match_count and match_rate > best_match_total):
                    best_match_type = noise_type
                    best_match_count = type_count
                    best_match_total = match_rate

        # 计算置信度：基于最佳匹配类型的匹配数（至少2个关键词才算）
        # 阈值调整为：匹配关键词数 >= 2，或者匹配率 >= 0.3
        confidence = 0
        if best_match_count >= 2:
            confidence = 0.9  # 匹配2个以上关键词，高置信度
        elif best_match_count == 1 and best_match_total > 0:
            confidence = 0.5  # 匹配1个关键词，中等置信度

        print(f"[DEBUG] Best match: '{best_match_type}' with {best_match_count} keywords, confidence={confidence}")

        return {
            "categories": [best_match_type] if best_match_type else [],
            "confidence": confidence,
            "noise_type": best_match_type
        }

    def _get_noise_level(self, noise_type: str) -> str:
        """
        获取干扰级别

        Args:
            noise_type: 干扰类型

        Returns:
            noise（必须过滤）/pr（仅推送标题）/light（可推送）
        """
        # 必须过滤的类型
        if noise_type in ["招聘", "带货", "广告", "课程", "社群", "活动推广"]:
            return "noise"

        # 仅推送标题的类型
        if noise_type in ["融资", "公关"]:
            return "pr"

        return "light"

    def _build_result(self, categories: List[str], is_noise: bool,
                     noise_type: str, noise_level: str) -> Dict:
        """构建分类结果"""
        return {
            "categories": categories,
            "is_noise": is_noise,
            "noise_type": noise_type,
            "noise_level": noise_level
        }
