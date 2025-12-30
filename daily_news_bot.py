#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용/채용/취업 뉴스봇 - 메인 실행 스크립트
매일 아침 9시 실행되어 고용 관련 뉴스 10개를 카카오톡으로 전송
"""

import os
import sys
import json
from datetime import datetime
from naver_news_collector import NaverNewsCollector
from gemini_news_editor import GeminiNewsEditor
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("🚀 고용/채용 뉴스봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1단계: 네이버 뉴스 수집
    print("\n[1/4] 📰 네이버 뉴스 수집 중...")
    try:
        collector = NaverNewsCollector(
            client_id=os.environ['NAVER_CLIENT_ID'],
            client_secret=os.environ['NAVER_CLIENT_SECRET']
        )
        raw_news = collector.collect_employment_news(count=20)
        print(f"✓ 수집 완료: {len(raw_news)}개 뉴스")
        
        if not raw_news:
            print("❌ 수집된 뉴스가 없습니다.")
            return
            
    except Exception as e:
        print(f"❌ 뉴스 수집 실패: {e}")
        return
    
    # 2단계: Gemini AI 편집 (새 포맷 적용)
    print("\n[2/4] 🤖 AI 편집 중...")
    try:
        editor = GeminiNewsEditor(
            api_key=os.environ['GEMINI_API_KEY']
        )
        formatted_news = editor.format_news_with_recruitment_point(raw_news[:10])
        print(f"✓ 편집 완료: {len(formatted_news)}개 뉴스")
        
        if not formatted_news:
            print("⚠️ AI 편집 실패, 원본 데이터 사용")
            formatted_news = raw_news[:10]
            
    except Exception as e:
        print(f"⚠️ AI 편집 오류: {e}")
        print("→ 원본 데이터 사용")
        formatted_news = raw_news[:10]
    
    # 3단계: 메시지 포맷팅
    print("\n[3/4] 📝 메시지 포맷팅 중...")
    message = format_kakao_message(formatted_news)
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
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "news_count": len(formatted_news),
        "message_length": len(message),
        "news": formatted_news
    }
    
    with open('daily_news_result.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ 모든 작업 완료!")
    print("=" * 50)

def format_kakao_message(news_list):
    """
    새로운 포맷으로 카카오톡 메시지 생성
    
    [산업]
    "뉴스 제목"
    링크: https://...
    채용포인트: 채용 관련 인사이트
    """
    
    header = f"📰 오늘의 고용/채용 뉴스 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 30 + "\n\n"
    
    messages = []
    
    for i, news in enumerate(news_list, 1):
        # 카테고리 결정 (뉴스 제목/설명 기반)
        category = determine_category(news)
        
        msg = f"[{category}]\n"
        msg += f'"{news.get("title", "제목 없음")}"\n'
        msg += f'링크: {news.get("link", "")}\n'
        
        # 채용포인트 추가 (AI가 생성한 경우)
        recruitment_point = news.get('recruitment_point', '')
        if recruitment_point:
            msg += f'채용포인트: {recruitment_point}\n'
        
        messages.append(msg)
    
    # 전체 메시지 조합
    full_message = header + "\n".join(messages)
    
    # 1000자 제한 체크
    if len(full_message) > 1000:
        # 각 뉴스 항목을 축약
        messages = []
        for i, news in enumerate(news_list, 1):
            category = determine_category(news)
            title = news.get("title", "제목 없음")
            link = news.get("link", "")
            
            # 제목이 너무 길면 축약
            if len(title) > 40:
                title = title[:37] + "..."
            
            msg = f"[{category}] {title}\n{link}\n"
            messages.append(msg)
        
        full_message = header + "\n".join(messages)
    
    return full_message

def determine_category(news):
    """뉴스 내용을 분석해 산업 카테고리 결정"""
    
    title = news.get('title', '').lower()
    description = news.get('description', '').lower()
    content = f"{title} {description}"
    
    # 산업별 키워드
    categories = {
        '조선': ['조선', '현대중공업', '삼성중공업', 'lng선', '선박'],
        '반도체': ['반도체', '삼성전자', 'sk하이닉스', '메모리', '칩'],
        'IT': ['it', '소프트웨어', '개발자', '프로그래머', '코딩', '앱'],
        '제조': ['제조', '공장', '생산직', '기계', '자동차'],
        '서비스': ['서비스', '유통', '판매', '고객', '영업'],
        '금융': ['금융', '은행', '증권', '보험', '투자'],
        '건설': ['건설', '부동산', '건축', '토목', '인프라'],
        '바이오': ['바이오', '제약', '의료', '헬스케어', '병원'],
    }
    
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return '기타'

if __name__ == "__main__":
    main()
