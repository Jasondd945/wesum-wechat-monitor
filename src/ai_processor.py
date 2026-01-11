"""
AI 文章处理模块（整合分类和摘要）
使用通义千问 API 生成文章总结和分类标签
"""

import dashscope
from dashscope import Generation
from typing import Dict, List
import re


class AIArticleProcessor:
    """AI 文章处理器 - 整合分类判断和摘要生成"""

    def __init__(self, api_key: str, model: str = "qwen-turbo"):
        """
        初始化 AI 文章处理器

        Args:
            api_key: 通义千问 API Key
            model: 模型名称
        """
        dashscope.api_key = api_key
        self.model = model
        self.noise_keywords = self._default_noise_keywords()

    def _default_noise_keywords(self) -> Dict[str, List[str]]:
        """默认的干扰关键词"""
        return {
            "招聘": ["招聘", "诚聘", "猎头", "职位", "JD", "简历", "应聘", "面试", "入职"],
            "带货": [
                # 价格相关（删除"元"等过于通用的词）
                "块", "毛", "折", "优惠", "限时", "特价", "清仓", "秒杀", "抢购",
                "购买", "下单", "立减", "满减", "券", "福利", "红包", "补贴",
                # 数量/单位（删除单个字母L和ml，容易误判）
                "支", "件", "套", "盒", "瓶", "袋", "斤", "克",
                # 行动词
                "立即抢", "马上抢", "抢购", "速抢", "扫码", "点击购买", "购买链接",
                # 产品描述
                "爆款", "热销", "新品", "新品上市", "配置拉满", "性价比", "超值",
                # 其他
                "包邮", "货到付款", "七天退换", "正品", "官方", "旗舰店", "自营"
            ],
            "广告": ["赞助", "广告", "品牌推广", "商业合作", "软文", "推广"],
            "课程": ["课程", "训练营", "扫码", "立减", "报名", "学习", "培训", "讲座", "公开课"],
            "社群": ["知识星球", "付费社群", "会员", "加入社群", "社群", "粉丝群", "交流群"],
            "活动推广": ["会议报名", "展会报名", "早鸟票", "活动报名", "立即报名", "报名开启", "开启报名"],
            "融资": ["融资", "轮融资", "估值", "募资", "IPO", "上市"],  # 删除"投资方"中的"投资"
            "公关": ["发布", "新品发布", "隆重推出", "盛大发布", "战略合作", "签署协议", "获奖"]
        }

    def process_article(self, article: Dict) -> Dict:
        """
        处理单篇文章（判断广告类型 + 生成摘要和标签）

        Args:
            article: 文章信息（包含 title, content, author, link, published）

        Returns:
            {
                "summary": "摘要文本",
                "categories": ["标签1", "标签2"],  # AI生成的主题分类
                "is_noise": true/false,            # 是否为干扰内容
                "noise_type": "带货/招聘/...",     # 干扰类型
                "noise_level": "noise/pr/light"    # 干扰级别
            }
        """
        title = article.get('title', '')
        content = article.get('content', '')

        # 步骤1: 关键词匹配,判断是否为广告
        noise_result = self._match_keywords(title + content)

        # 步骤2: 根据广告类型,选择不同的AI提示词
        if noise_result['is_noise']:
            # 广告文章: 生成简化摘要 + 分类标签
            result = self._generate_simple_summary(article, noise_result['noise_type'])
        else:
            # 正常文章: 生成完整总结 + 分类标签
            result = self._generate_full_summary(article)

        # 步骤3: 合并结果
        return {
            "summary": result['summary'],
            "categories": result['categories'],
            "is_noise": noise_result['is_noise'],
            "noise_type": noise_result['noise_type'],
            "noise_level": noise_result['noise_level']
        }

    def _match_keywords(self, text: str) -> Dict:
        """
        关键词匹配判断是否为广告

        Args:
            text: 文章标题+内容

        Returns:
            {
                "is_noise": true/false,
                "noise_type": "带货/招聘/...",
                "noise_level": "noise/pr/light"
            }
        """
        best_match_type = None
        best_match_count = 0

        for noise_type, keywords in self.noise_keywords.items():
            type_count = 0
            for keyword in keywords:
                if keyword in text:
                    type_count += 1

            if type_count > best_match_count:
                best_match_type = noise_type
                best_match_count = type_count

        # 匹配2个以上关键词才认为是广告
        is_noise = best_match_count >= 2
        noise_level = self._get_noise_level(best_match_type) if is_noise else None

        return {
            "is_noise": is_noise,
            "noise_type": best_match_type if is_noise else None,
            "noise_level": noise_level
        }

    def _get_noise_level(self, noise_type: str) -> str:
        """获取干扰级别"""
        if noise_type in ["招聘", "带货", "广告", "课程", "社群", "活动推广"]:
            return "noise"
        if noise_type in ["融资", "公关"]:
            return "pr"
        return "light"

    def _generate_full_summary(self, article: Dict) -> Dict:
        """
        生成正常文章的完整总结（500字 + 分类标签）

        Returns:
            {
                "summary": "总结文本",
                "categories": ["标签1", "标签2"]
            }
        """
        prompt = f"""请将以下公众号文章生成总结，要求：

【标签】
1. 输出3-5个分类标签（关键词）
2. 使用简洁的中文词汇（2-4个字）
3. 标签之间用顿号、分隔
4. 标签应该反映文章的核心主题（如：科技、互联网、商业分析等）

【总结】
1. **结构化输出**：使用 Emoji 图标作为段落标记（如🎯、🔄、🤖、💡、📊、🔍等）
2. **分段清晰**：每个大段有明确的主题标题
3. **深度解析**：不是简单摘要点，而是保留关键信息和数据的深度解析
4. **格式规范**：
   - 使用分级标题（一、二、三）
   - 关键数据用加粗标记
   - 包含具体案例和细节
5. **内容长度**：控制在500字以内
6. **段落分隔**：段落之间用空行分隔
7. **补充细节**：最后补充关键细节和背景信息

文章标题：{article['title']}

公众号：{article.get('author', 'Unknown')}

文章内容：
{article.get('content', '')[:4000]}

请按以下格式输出：

【标签】标签1、标签2、标签3

【总结】
🎯 第一个要点的标题

第一个要点的详细内容...

🔄 第二个要点的标题

第二个要点的详细内容...
"""

        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=1000
            )

            if response.status_code == 200:
                return self._parse_ai_response(response.output.text)
            else:
                return {
                    "summary": f"API 错误: {response.code}",
                    "categories": []
                }

        except Exception as e:
            return {
                "summary": f"生成总结失败: {str(e)}",
                "categories": []
            }

    def _generate_simple_summary(self, article: Dict, noise_type: str) -> Dict:
        """
        生成广告文章的简化摘要（100字 + 分类标签）

        Args:
            article: 文章信息
            noise_type: 广告类型（带货、招聘等）

        Returns:
            {
                "summary": "简化摘要",
                "categories": ["标签1", "标签2"]
            }
        """
        # 根据广告类型定制要点要求
        points_requirements = {
            "招聘": "- 招聘公司\n- 招聘岗位\n- 薪资范围\n- 工作地点\n- 岗位要求",
            "带货": "- 产品名称\n- 产品价格\n- 优惠信息\n- 购买方式\n- 活动时间",
            "广告": "- 品牌/产品\n- 核心信息\n- 推广内容",
            "课程": "- 课程名称\n- 讲师/机构\n- 课程价格\n- 课程时长\n- 报名方式",
            "社群": "- 社群名称\n- 社群类型\n- 加入方式\n- 费用信息",
            "活动推广": "- 活动名称\n- 活动时间\n- 活动地点\n- 票价信息\n- 报名方式",
            "融资": "- 融资公司\n- 融资轮次\n- 融资金额\n- 投资方\n- 公司估值",
            "公关": "- 公司/品牌\n- 核心信息\n- 发布时间\n- 相关数据"
        }

        requirements = points_requirements.get(noise_type, "- 要点1\n- 要点2\n- 要点3")

        prompt = f"""请将以下公众号文章提取为关键要点和分类标签，要求：

【标签】
根据文章内容，给出3-5个分类标签（如：电商、购物、职场、教育等），用顿号、分隔

【总结】
提炼3-5个关键要点，要求：
1. 每个要点不超过15字
2. 严格控制在100字以内
3. 必须包含以下信息：
{requirements}

文章标题：{article['title']}

文章内容：
{article.get('content', '')[:2000]}

请按以下格式输出：

【标签】分类1、分类2、分类3

【总结】
• 要点1
• 要点2
• 要点3"""

        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                max_tokens=300
            )

            if response.status_code == 200:
                return self._parse_ai_response(response.output.text)
            else:
                return {
                    "summary": f"API 错误: {response.code}",
                    "categories": []
                }

        except Exception as e:
            return {
                "summary": f"生成简化摘要失败: {str(e)}",
                "categories": []
            }

    def _parse_ai_response(self, ai_text: str) -> Dict:
        """
        解析AI响应,提取标签和摘要

        Args:
            ai_text: AI返回的文本

        Returns:
            {
                "summary": "摘要",
                "categories": ["标签1", "标签2"]
            }
        """
        categories = []
        summary = ai_text

        # 提取【标签】部分
        tag_match = re.search(r'【标签】(.+?)(?=【总结】|\n\n|$)', ai_text)
        if tag_match:
            tag_text = tag_match.group(1).strip()
            categories = re.split(r'[、,，\s]+', tag_text)
            categories = list(set([c for c in categories if c.strip()]))
            categories = categories[:5]

        # 提取【总结】部分
        summary_match = re.search(r'【总结】\s*\n(.+)', ai_text, re.DOTALL)
        if summary_match:
            summary = summary_match.group(1)
            # 只去除首尾空行，保留中间的段落结构
            summary = summary.lstrip().rstrip()
        else:
            # 如果没有【总结】标记，去除【标签】部分
            summary = re.sub(r'【标签】.+', '', ai_text)
            summary = summary.lstrip().rstrip()

        return {
            "summary": summary,
            "categories": categories
        }
