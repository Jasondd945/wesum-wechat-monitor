"""
WeSum - 微信公众号小时级摘要推送助手
主程序
"""

import json
import sys
import os
from datetime import datetime

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rss_parser import RSSParser
from ai_processor import AIArticleProcessor
from push_notifier import PushNotifier


def load_config(config_file: str = "config.json") -> dict:
    """加载配置文件"""
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """主函数"""
    print("=" * 60)
    print("WeSum - 微信公众号摘要推送助手")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1. 加载配置
        print("\n[Step 1] Loading configuration...")
        config = load_config()
        print("Configuration loaded successfully.")

        # 2. 初始化模块
        print("\n[Step 2] Initializing modules...")
        rss_parser = RSSParser(
            rss_url=config['rss']['url'],
            seen_articles_file=config['storage']['seen_articles_file']
        )

        ai_processor = AIArticleProcessor(
            api_key=config['ai']['api_key'],
            model=config['ai']['model']
        )

        push_notifier = PushNotifier(
            sendkey=config['push']['sendkey'],
            title_prefix=config['push']['title_prefix']
        )
        print("Modules initialized successfully.")

        # 3. 获取新文章
        print("\n[Step 3] Fetching new articles...")
        max_articles = config['filters'].get('max_articles_per_run', None)  # 支持无限制
        max_hours = config['filters'].get('max_hours', 24)  # 默认24小时
        articles = rss_parser.fetch_articles(max_articles=max_articles, max_hours=max_hours)

        if not articles:
            print("No new articles found. Exiting.")
            return

        print(f"Found {len(articles)} new articles.")

        # 4. AI处理文章（判断广告类型 + 生成摘要和标签）
        print("\n[Step 4] Processing articles with AI...")
        for i, article in enumerate(articles, 1):
            print(f"Processing {i}/{len(articles)}: {article['title'][:30]}...")

            # 一次性完成: 判断广告 + 生成摘要 + 生成标签
            result = ai_processor.process_article(article)

            # 更新文章信息
            article['summary'] = result['summary']
            article['categories'] = result['categories']
            article['is_noise'] = result['is_noise']
            article['noise_type'] = result['noise_type']
            article['noise_level'] = result['noise_level']

            # 打印处理结果
            noise_info = f" ({result['noise_type']})" if result['is_noise'] else ""
            print(f"  → Summary{noise_info} with tags: {result['categories']}")

        print("AI processing completed.")

        # 5. 批量推送到微信
        print("\n[Step 5] Pushing to WeChat...")
        if push_notifier.send_articles_batch(articles):
            print(f"Batch push notification sent successfully! ({len(articles)} articles)")
        else:
            print("Failed to send push notification.")

        # 6. 完成
        print("\n" + "=" * 60)
        print(f"WeSum completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Processed {len(articles)} articles.")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\n[ERROR] Config file not found: {e}")
        print("Please create 'config.json' based on 'config.example.json'")
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
