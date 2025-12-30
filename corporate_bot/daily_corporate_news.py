#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기업뉴스봇 - 산업/기업 동향 전문
"""

import os
import sys
import json
from datetime import datetime
from naver_corporate_collector import NaverCorporateCollector
from gemini_corporate_editor import GeminiCorporateEditor
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("🏢 기업뉴스봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1단계: 산업별 뉴스 수집
    print("\n[1/4] 📰 산업별 뉴스 수집 중...")
    try:
        collector = NaverCorporateCollector(
            client_id=os.environ['NAVER_CLIENT_ID'],
            client_secret=os.environ['NAVER_CLIENT_SECRET']
        )
        
        # 산업별 2개씩 수집 (총 14개)
        categorized_news = collector.collect_by_industry()
        
        total_count = sum(len(news) for news in categorized_news.values())
        print(f"✓ 수집 완료: {total_count}개 뉴스")
        
        if total_count == 0:
            print("❌ 수집된 뉴스가 없습니다.")
            return
            
    except Exception as e:
        print(f"❌ 뉴스 수집 실패: {e}")
        return
    
    # 2단계: Gemini AI 편집
    print("\n[2/4] 🤖 AI 편집 중...")
    try:
        editor = GeminiCorporateEditor(
            api_key=os.environ['GEMINI_API_KEY']
        )
        
        formatted_news = editor.format_corporate_news(categorized_news)
        print(f"✓ 편집 완료")
        
    except Exception as e:
        print(f"⚠️ AI 편집 오류: {e}")
        formatted_news = categorized_news
    
    # 3단계: 메시지 포맷팅
    print("\n[3/4] 📝 메시지 포맷팅 중...")
    message = format_corporate_message(formatted_news)
    print(f"✓ 메시지 길이: {len(message)}자")
    
    # 4단계: 카카오톡 발송
    print("\n[4/4] 📤 카카오톡 발송 중...")
    try:
        sender = KakaoSender(
            rest_api_key=os.environ['KAKAO_REST_API_KEY'],
            refresh_token=os.environ['KAKAO_REFRESH_TOKEN']
        )
        
        result = sender.send_message(message)
        
        if result:
            print("✓ 발송 성공!")
        else:
            print("❌ 발송 실패")
            
    except Exception as e:
        print(f"❌ 발송 오류: {e}")
        return
    
    # 결과 저장
    save_result(formatted_news, "corporate")
    
    print("\n" + "=" * 50)
    print("✅ 기업뉴스봇 완료!")
    print("=" * 50)

def format_corporate_message(categorized_news):
    """기업뉴스 포맷 (산업별)"""
    
    header = f"🏢 오늘의 산업 뉴스 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 30 + "\n\n"
    
    # 산업별 이모지
    industry_icons = {
        'IT/기술': '💻',
        '조선': '🚢',
        '반도체': '🔌',
        '제조/산업': '🏭',
        '금융': '💰',
        '건설/부동산': '🏗️',
        '바이오/의료': '💊'
    }
    
    sections = []
    
    for industry, news_list in categorized_news.items():
        if not news_list:
            continue
        
        icon = industry_icons.get(industry, '📌')
        section = f"{icon} {industry}\n"
        
        for i, news in enumerate(news_list, 1):
            title = news.get('title', '제목 없음')
            link = news.get('link', '')
            
            # 제목 길이 제한
            if len(title) > 30:
                title = title[:27] + "..."
            
            section += f"{i}. {title}\n"
            section += f"   {link}\n"
        
        sections.append(section)
    
    full_message = header + "\n".join(sections)
    
    # 1000자 제한
    if len(full_message) > 1000:
        # 각 산업당 1개씩만
        sections = []
        for industry, news_list in categorized_news.items():
            if not news_list:
                continue
            
            icon = industry_icons.get(industry, '📌')
            news = news_list[0]
            title = news.get('title', '')[:25] + "..."
            link = news.get('link', '')
            
            section = f"{icon} {industry}\n{title}\n{link}\n"
            sections.append(section)
        
        full_message = header + "\n".join(sections)
    
    return full_message[:1000]

def save_result(news_dict, bot_type):
    """결과 저장"""
    
    result_data = {
        "bot_type": bot_type,
        "timestamp": datetime.now().isoformat(),
        "news": news_dict
    }
    
    filename = f"{bot_type}_news_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
