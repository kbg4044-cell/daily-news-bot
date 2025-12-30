"""
산업뉴스봇 - 메인 실행 파일 (완전판)
- PC 없이 GitHub Actions에서 완전 자동 실행
- 카카오 토큰 자동 갱신
- 매일 오전 8시 자동 발송
"""

import os
import sys
from datetime import datetime
from typing import List, Dict
import traceback

# 자체 모듈 임포트
from naver_news_collector import NaverNewsCollector
from gemini_news_editor import GeminiNewsEditor
from kakao_sender import KakaoTokenManager, KakaoMessageSender

class DailyNewsBot:
    """산업뉴스봇 메인 클래스"""
    
    def __init__(self):
        print("\n" + "="*70)
        print("📰 산업뉴스봇 시작")
        print(f"⏰ 실행 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        # API 키 확인
        self.validate_api_keys()
        
        # 모듈 초기화
        self.news_collector = NaverNewsCollector()
        self.news_editor = GeminiNewsEditor()
        
        # 카카오 토큰 관리자 & 발송자
        try:
            self.token_manager = KakaoTokenManager()
            self.kakao_sender = KakaoMessageSender(self.token_manager)
            self.kakao_enabled = True
        except Exception as e:
            print(f"⚠️ 카카오 초기화 실패 (테스트 모드): {str(e)}")
            self.kakao_enabled = False
    
    def validate_api_keys(self):
        """API 키 검증"""
        required_keys = {
            'NAVER_CLIENT_ID': os.getenv('NAVER_CLIENT_ID'),
            'NAVER_CLIENT_SECRET': os.getenv('NAVER_CLIENT_SECRET'),
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY')
        }
        
        optional_keys = {
            'KAKAO_REST_API_KEY': os.getenv('KAKAO_REST_API_KEY'),
            'KAKAO_REFRESH_TOKEN': os.getenv('KAKAO_REFRESH_TOKEN')
        }
        
        missing_required = [key for key, value in required_keys.items() if not value]
        missing_optional = [key for key, value in optional_keys.items() if not value]
        
        if missing_required:
            print("❌ 필수 API 키가 설정되지 않았습니다:")
            for key in missing_required:
                print(f"   - {key}")
            raise ValueError("필수 API 키가 누락되었습니다!")
        
        print("✅ 필수 API 키 확인 완료")
        
        if missing_optional:
            print("⚠️ 선택 API 키 누락 (카카오 발송 비활성화):")
            for key in missing_optional:
                print(f"   - {key}")
        else:
            print("✅ 카카오 API 키 확인 완료")
        
        print()
    
    def collect_news(self) -> List[Dict]:
        """
        1단계: 네이버 뉴스 수집
        - 7개 산업별로 2개씩 총 14개 수집
        """
        print("📡 [1단계] 뉴스 수집 시작...")
        print("-" * 70)
        
        try:
            news_list = self.news_collector.collect_news_by_industry(news_per_industry=2)
            
            if not news_list:
                print("⚠️ 수집된 뉴스가 없습니다!")
                return []
            
            print(f"\n✅ 수집 완료: {len(news_list)}개 뉴스")
            
            # 산업별 분포 출력
            industries = {}
            for news in news_list:
                industry = news.get('industry', '기타')
                industries[industry] = industries.get(industry, 0) + 1
            
            print("\n📊 산업별 분포:")
            for industry, count in industries.items():
                print(f"   • {industry}: {count}개")
            
            print("-" * 70 + "\n")
            return news_list
            
        except Exception as e:
            print(f"❌ 뉴스 수집 실패: {str(e)}")
            traceback.print_exc()
            return []
    
    def edit_news_with_ai(self, news_list: List[Dict]) -> List[Dict]:
        """
        2단계: Gemini AI로 뉴스 편집
        - 요약 및 인사이트 추가
        """
        print("🤖 [2단계] Gemini AI 편집 시작...")
        print("-" * 70)
        
        try:
            edited_news = []
            for idx, news in enumerate(news_list, 1):
                print(f"   편집 중... ({idx}/{len(news_list)})")
                edited = self.news_editor.edit_single_news(news)
                edited_news.append(edited)
            
            print(f"\n✅ AI 편집 완료: {len(edited_news)}개")
            print("-" * 70 + "\n")
            return edited_news
            
        except Exception as e:
            print(f"⚠️ AI 편집 실패 (원본 사용): {str(e)}")
            traceback.print_exc()
            print("-" * 70 + "\n")
            return news_list
    
    def format_kakao_message(self, news_list: List[Dict]) -> str:
        """
        3단계: 카카오톡 메시지 포맷팅 (간결 버전)
        """
        print("📝 [3단계] 메시지 포맷팅...")
        print("-" * 70)
        
        # 산업 이모지 매핑
        industry_emoji = {
            '조선': '🚢',
            '반도체': '💾',
            '철강': '🏭',
            '금융': '💰',
            '식품': '🍜',
            '건설': '🏗️',
            '바이오': '💊'
        }
        
        # 헤더
        today = datetime.now().strftime('%m월 %d일')
        message = f"📰 산업뉴스 ({today})\n"
        message += "━" * 25 + "\n\n"
        
        # 뉴스 아이템 (최대 10개)
        for idx, news in enumerate(news_list[:10], 1):
            industry = news.get('industry', '기타')
            emoji = industry_emoji.get(industry, '📌')
            title = news.get('title', '제목없음')
            
            # 제목 길이 제한
            if len(title) > 35:
                title = title[:32] + "..."
            
            message += f"{emoji} {title}\n"
        
        # 푸터
        message += "\n━" * 25 + "\n"
        message += "⏰ 매일 오전 8시 발송\n"
        message += f"📊 총 {len(news_list)}개 산업뉴스"
        
        msg_length = len(message)
        print(f"✅ 포맷팅 완료 ({msg_length}자)")
        
        if msg_length > 1000:
            print(f"⚠️ 메시지가 너무 깁니다. 축소 중...")
            message = self.format_short_message(news_list[:7])
            print(f"✅ 축소 완료 ({len(message)}자)")
        
        print("-" * 70 + "\n")
        return message
    
    def format_short_message(self, news_list: List[Dict]) -> str:
        """초단축 메시지"""
        today = datetime.now().strftime('%m.%d')
        message = f"📰 산업뉴스 {today}\n\n"
        
        for idx, news in enumerate(news_list[:7], 1):
            industry = news.get('industry', '기타')
            title = news.get('title', '')[:30]
            message += f"{idx}. [{industry}] {title}...\n"
        
        message += f"\n⏰ 매일 오전 8시 | {len(news_list)}개 뉴스"
        return message
    
    def send_to_kakao(self, message: str) -> bool:
        """
        4단계: 카카오톡 발송
        """
        print("📤 [4단계] 카카오톡 발송...")
        print("-" * 70)
        
        if not self.kakao_enabled:
            print("⚠️ 카카오 발송 비활성화 (API 키 미설정)")
            print("📝 메시지 미리보기:")
            print("\n" + message + "\n")
            print("-" * 70 + "\n")
            return False
        
        try:
            success = self.kakao_sender.send_message_to_me(message)
            
            if success:
                print("✅ 발송 완료!")
            else:
                print("❌ 발송 실패")
            
            print("-" * 70 + "\n")
            return success
            
        except Exception as e:
            print(f"❌ 발송 오류: {str(e)}")
            traceback.print_exc()
            print("-" * 70 + "\n")
            return False
    
    def run(self):
        """메인 실행"""
        try:
            # 1. 뉴스 수집
            news_list = self.collect_news()
            if not news_list:
                print("⚠️ 수집된 뉴스가 없어 종료합니다.")
                return False
            
            # 2. AI 편집
            edited_news = self.edit_news_with_ai(news_list)
            
            # 3. 메시지 포맷팅
            message = self.format_kakao_message(edited_news)
            
            # 4. 카카오톡 발송
            success = self.send_to_kakao(message)
            
            # 완료
            print("="*70)
            if success:
                print("🎉 산업뉴스봇 실행 완료!")
            else:
                print("✅ 뉴스 수집 완료 (카카오 발송 스킵)")
            print("="*70 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 치명적 오류 발생: {str(e)}")
            traceback.print_exc()
            return False

def main():
    """메인 함수"""
    bot = DailyNewsBot()
    success = bot.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
