#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용뉴스봇 - 채용/취업 전문
중복 제거 강화 버전
"""

import os
import sys
import json
from datetime import datetime
from naver_employment_collector import NaverEmploymentCollector
from gemini_employment_editor import GeminiEmploymentEditor
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("💼 고용뉴스봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1단계: 네이버 뉴스 수집 (중복 제거)
    print("\n[1/4] 📰 고용 뉴스 수집 중...")
    try:
        collector = NaverEmploymentCollector(
            client_id=os.environ['NAVER_CLIENT_ID'],
            client_secret=os.environ['NAVER_CLIENT_SECRET']
        )
        
        # 30개 수집 후 중복 제거하여 상위 10개 선정
        raw_news = collector.collect_unique_news(count=30)
        print(f"✓ 수집 완료: {len(raw_news)}개 뉴스 (중복 제거됨)")
        
        if not raw_news:
            print("❌ 수집된 뉴스가 없습니다.")
            return
            
    except Exception as e:
        print(f"❌ 뉴스 수집 실패: {e}")
        return
    
    # 2단계: Gemini AI 편집
    print("\n[2/4] 🤖 AI 편집 중...")
    try:
        editor = GeminiEmploymentEditor(
            api_key=os.environ['GEMINI_API_KEY']
        )
        
        # 상위 10개만 AI 편집
        formatted_news = editor.format_news_with_recruitment_point(raw_news[:10])
        print(f"✓ 편집 완료: {len(formatted_news)}개 뉴스")
        
        if not formatted_news:
            print("⚠️ AI 편집 실패, 원본 사용")
            formatted_news = raw_news[:10]
            
    except Exception as e:
        print(f"⚠️ AI 편집 오류: {e}")
        formatted_news = raw_news[:10]
    
    # 3단계: 메시지 포맷팅
    print("\n[3/4] 📝 메시지 포맷팅 중...")
    message = format_employment_message(formatted_news)
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
    save_result(formatted_news, "employment")
    
    print("\n" + "=" * 50)
    print("✅ 고용뉴스봇 완료!")
    print("=" * 50)

def format_employment_message(news_list):
    """고용뉴스 포맷"""
    
    header = f"💼 오늘의 고용/채용 뉴스 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 30 + "\n\n"
    
    messages = []
    
    for news in news_list:
        category = determine_category(news)
        title = news.get('title', '제목 없음')
        link = news.get('link', '')
        recruitment_point = news.get('recruitment_point', '')
        
        # 제목 길이 제한
        if len(title) > 35:
            title = title[:32] + "..."
        
        msg = f"[{category}]\n"
        msg += f'"{title}"\n'
        msg += f'링크: {link}\n'
        
        if recruitment_point:
            msg += f'채용포인트: {recruitment_point}\n'
        
        messages.append(msg)
    
    full_message = header + "\n".join(messages)
    
    # 1000자 제한
    if len(full_message) > 1000:
        # 채용포인트 제거하고 재시도
        messages = []
        for news in news_list:
            category = determine_category(news)
            title = news.get('title', '')[:32] + "..."
            link = news.get('link', '')
            msg = f"[{category}] {title}\n{link}\n"
            messages.append(msg)
        
        full_message = header + "\n".join(messages)
    
    return full_message[:1000]

def determine_category(news):
    """산업 카테고리 판단"""
    
    title = news.get('title', '').lower()
    description = news.get('description', '').lower()
    content = f"{title} {description}"
    
    categories = {
        '조선': ['조선', '현대중공업', '삼성중공업', '대우조선', 'lng선', '선박'],
        '반도체': ['반도체', '삼성전자', 'sk하이닉스', '메모리', '칩', '파운드리'],
        'IT': ['it', '소프트웨어', '개발자', '프로그래머', '네이버', '카카오', '앱'],
        '제조': ['제조', '공장', '생산직', '기계', '자동차', '현대차', '기아'],
        '서비스': ['서비스', '유통', '판매', '고객', '영업', '마케팅'],
        '금융': ['금융', '은행', '증권', '보험', '투자'],
        '건설': ['건설', '부동산', '건축', '토목', 'GS건설', '현대건설'],
        '바이오': ['바이오', '제약', '의료', '헬스케어', '병원'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return '기타'

def save_result(news_list, bot_type):
    """결과 저장"""
    
    result_data = {
        "bot_type": bot_type,
        "timestamp": datetime.now().isoformat(),
        "news_count": len(news_list),
        "news": news_list
    }
    
    filename = f"{bot_type}_news_result.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
