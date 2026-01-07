#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고용24 채용공고봇 - 실행 파일 (Selenium Stealth 전용)
"""

import os
from datetime import datetime
from kakao_sender import KakaoSender

def main():
    print("=" * 50)
    print("🏢 고용24 채용공고봇 시작")
    print(f"실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    jobs_data = None
    
    # [1] Selenium Stealth 크롤링 실행
    print("\n[단계 1] 크롤러 실행 중...")
    try:
        from work24_stealth import Work24StealthCrawler
        
        crawler = Work24StealthCrawler()
        jobs_data = crawler.collect_jobs(max_jobs=15)
        
        total_count = sum(len(jobs) for jobs in jobs_data.values())
        print(f"✓ 크롤링 결과: 총 {total_count}개 공고 발견")
        
    except Exception as e:
        print(f"❌ 크롤링 실행 실패: {e}")
        return

    # [2] 결과 확인 및 메시지 발송
    if total_count == 0:
        print("\n[결과] 오늘 등록된 공고가 없거나, 필터링에 걸린 공고가 없습니다.")
        # 공고가 없다는 메시지도 보내고 싶으면 아래 주석 해제
        # send_empty_message() 
        return
    
    # [3] 메시지 포맷팅
    print("\n[단계 2] 메시지 포맷팅 중...")
    message = format_work24_message(jobs_data)
    
    # [4] 카카오톡 발송
    print("\n[단계 3] 카카오톡 발송 시도...")
    try:
        # 환경변수에서 키 가져오기 (GitHub Actions Secrets)
        api_key = os.environ.get('KAKAO_REST_API_KEY')
        refresh_token = os.environ.get('KAKAO_REFRESH_TOKEN')

        if not api_key or not refresh_token:
            print("❌ 오류: KAKAO API KEY 또는 TOKEN이 설정되지 않았습니다.")
            return

        sender = KakaoSender(rest_api_key=api_key, refresh_token=refresh_token)
        result = sender.send_message(message)
        
        if result:
            print("✓ [성공] 카카오톡 발송 완료!")
        else:
            print("❌ [실패] 카카오톡 발송 실패")
            
    except Exception as e:
        print(f"❌ 발송 중 에러 발생: {e}")

    print("\n" + "=" * 50)

def format_work24_message(jobs_data):
    """카카오톡 메시지 예쁘게 꾸미기"""
    header = f"🏢 오늘의 채용공고 ({datetime.now().strftime('%m월 %d일')})\n"
    header += "=" * 20 + "\n\n"
    
    category_icons = {"대기업": "🏆", "중견기업": "💼", "외국계": "🌏", "강소기업": "⭐"}
    sections = []
    
    for category, jobs in jobs_data.items():
        if not jobs: continue
        icon = category_icons.get(category, "📌")
        
        # 카테고리 제목
        section = f"{icon} {category} ({len(jobs)}건)\n"
        # 공고 내용 (너무 길면 잘릴 수 있으니 상위 5개만)
        section += "\n".join(jobs[:5]) + "\n"
        sections.append(section)
    
    full_message = header + "\n".join(sections)
    
    # 카카오톡 글자수 제한 고려 (대략 1000자 끊기)
    return full_message[:1500]

def send_empty_message():
    """공고 없음 알림 (선택사항)"""
    msg = f"🏢 알림 ({datetime.now().strftime('%m/%d')})\n오늘은 조건에 맞는 새 채용공고가 없습니다."
    try:
        sender = KakaoSender(os.environ['KAKAO_REST_API_KEY'], os.environ['KAKAO_REFRESH_TOKEN'])
        sender.send_message(msg)
    except: pass

if __name__ == "__main__":
    main()
