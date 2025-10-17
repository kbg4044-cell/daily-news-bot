#!/usr/bin/env python3
"""
Daily News Bot - 자동 뉴스 수집 및 카카오톡 발송 시스템
GitHub Actions에서 매일 오전 8시에 자동 실행됩니다.
"""

import os
import sys
import json
import traceback
from datetime import datetime
from typing import List, Dict

# 로컬 모듈 import
from naver_news_collector import NaverNewsCollector
from gemini_news_editor import GeminiNewsEditor
from kakao_business_sender import KakaoBusinessSender, NewsMessageFormatter

class DailyNewsBot:
    """일간 뉴스 봇 - 전체 프로세스 통합 관리"""
    
    def __init__(self):
        # 환경 변수에서 API 키 로드
        self.naver_client_id = os.getenv('NAVER_CLIENT_ID', 'i_ExQRquc2oFsTFDyLoz')
        self.naver_client_secret = os.getenv('NAVER_CLIENT_SECRET', 'eJpNFD4w1Z')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', 'YOUR_KAKAO_API_KEY_HERE')
        self.kakao_api_key = os.getenv('KAKAO_API_KEY', 'YOUR_KAKAO_API_KEY_HERE')
        
        # 각 모듈 초기화
        self.news_collector = NaverNewsCollector(self.naver_client_id, self.naver_client_secret)
        self.gemini_editor = GeminiNewsEditor(self.gemini_api_key)
        self.kakao_sender = KakaoBusinessSender(self.kakao_api_key)
        self.formatter = NewsMessageFormatter()
        
        # 실행 결과 저장용
        self.execution_log = {
            "timestamp": datetime.now().isoformat(),
            "status": "started",
            "steps": [],
            "final_result": None,
            "error": None
        }
    
    def log_step(self, step_name: str, status: str, details: Dict = None):
        """실행 단계 로깅"""
        step_log = {
            "step": step_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.execution_log["steps"].append(step_log)
        print(f"📝 [{step_name}] {status}")
        if details:
            for key, value in details.items():
                print(f"   - {key}: {value}")
    
    def collect_news(self) -> List[Dict]:
        """1단계: 뉴스 수집"""
        try:
            print("🚀 1단계: 뉴스 수집 시작")
            
            # 뉴스 수집
            all_news = self.news_collector.collect_all_news()
            
            # 상위 5개 선별
            top_news = self.news_collector.filter_and_rank_news(all_news, 5)
            
            self.log_step("news_collection", "success", {
                "total_collected": len(all_news),
                "filtered_count": len(top_news),
                "categories": list(set([news['category'] for news in top_news]))
            })
            
            return top_news
            
        except Exception as e:
            self.log_step("news_collection", "failed", {"error": str(e)})
            raise
    
    def edit_news(self, news_list: List[Dict]) -> List[Dict]:
        """2단계: AI 편집"""
        try:
            print("🤖 2단계: Gemini AI 편집 시작")
            
            edited_news = []
            success_count = 0
            
            for i, news in enumerate(news_list, 1):
                print(f"  ✏️  {i}/{len(news_list)} 편집 중: {news['title'][:30]}...")
                
                # Gemini로 요약문 재편집
                edited_summary = self.gemini_editor.edit_news_summary(news)
                
                # 편집된 내용으로 업데이트
                news['original_description'] = news.get('description', '')
                news['description'] = edited_summary
                news['edited_by'] = 'Gemini'
                
                edited_news.append(news)
                success_count += 1
            
            # 일간 인사이트 생성
            daily_insight = self.gemini_editor.generate_daily_insight(edited_news)
            
            self.log_step("ai_editing", "success", {
                "edited_count": success_count,
                "total_count": len(news_list),
                "insight_generated": bool(daily_insight)
            })
            
            return edited_news, daily_insight
            
        except Exception as e:
            self.log_step("ai_editing", "failed", {"error": str(e)})
            # AI 편집 실패 시에도 원본 뉴스는 발송
            return news_list, "📊 채용 시장 활성화 신호 감지\n💡 이력서 업데이트하고 기회 탐색하세요"
    
    def format_message(self, news_list: List[Dict], insight: str) -> str:
        """3단계: 카카오톡 메시지 포맷팅"""
        try:
            print("📱 3단계: 카카오톡 메시지 포맷팅")
            
            # 메시지 생성
            message = self.formatter.format_for_kakao(news_list, insight)
            
            # 길이 체크
            length_check = self.formatter.check_message_length(message)
            
            self.log_step("message_formatting", "success", {
                "message_length": length_check["length"],
                "is_valid": length_check["is_valid"],
                "max_length": length_check["max_length"]
            })
            
            return message
            
        except Exception as e:
            self.log_step("message_formatting", "failed", {"error": str(e)})
            raise
    
    def send_messages(self, message: str) -> Dict:
        """4단계: 카카오톡 발송"""
        try:
            print("📲 4단계: 카카오톡 메시지 발송")
            
            # 연결 테스트
            connection_ok = self.kakao_sender.test_connection()
            
            if not connection_ok:
                print("⚠️  카카오 API 연결 실패 - 테스트 모드로 실행")
            
            # 메시지 발송 (현재는 테스트 모드)
            if self.kakao_api_key == 'YOUR_KAKAO_API_KEY_HERE':
                # 테스트 모드: 콘솔에 출력
                print("🧪 테스트 모드: 메시지 미리보기")
                result = {"success_count": 1, "fail_count": 0, "total_count": 1}
            else:
                # 실제 발송
                result = self.kakao_sender.send_to_subscribers(message)
            
            self.log_step("message_sending", "success", result)
            return result
            
        except Exception as e:
            self.log_step("message_sending", "failed", {"error": str(e)})
            raise
    
    def save_result(self, news_list: List[Dict], message: str, send_result: Dict):
        """실행 결과 저장"""
        try:
            result_data = {
                "execution_log": self.execution_log,
                "news_data": news_list,
                "final_message": message,
                "send_result": send_result,
                "statistics": {
                    "news_count": len(news_list),
                    "success_rate": send_result.get("success_count", 0) / max(send_result.get("total_count", 1), 1) * 100,
                    "total_characters": len(message)
                }
            }
            
            # JSON 파일로 저장
            with open('daily_news_result.json', 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            
            print("💾 실행 결과가 daily_news_result.json에 저장되었습니다")
            
        except Exception as e:
            print(f"결과 저장 중 오류: {str(e)}")
    
    def run(self) -> bool:
        """전체 프로세스 실행"""
        try:
            print("🌅 Daily News Bot 실행 시작!")
            print("=" * 60)
            print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🔑 API 키 상태:")
            print(f"   - 네이버: {'✅' if self.naver_client_id != 'YOUR_NAVER_KEY' else '❌'}")
            print(f"   - Gemini: {'✅' if self.gemini_api_key != 'YOUR_GEMINI_KEY' else '❌'}")  
            print(f"   - 카카오: {'✅' if self.kakao_api_key != 'YOUR_KAKAO_API_KEY_HERE' else '⚠️  테스트 모드'}")
            print("=" * 60)
            
            # 1단계: 뉴스 수집
            news_list = self.collect_news()
            if not news_list:
                raise Exception("뉴스 수집 실패 - 선별된 뉴스가 없습니다")
            
            # 2단계: AI 편집  
            edited_news, insight = self.edit_news(news_list)
            
            # 3단계: 메시지 포맷팅
            message = self.format_message(edited_news, insight)
            
            # 4단계: 카카오톡 발송
            send_result = self.send_messages(message)
            
            # 결과 저장
            self.save_result(edited_news, message, send_result)
            
            # 최종 결과
            self.execution_log["status"] = "completed"
            self.execution_log["final_result"] = {
                "news_count": len(edited_news),
                "message_sent": send_result.get("success_count", 0) > 0,
                "send_statistics": send_result
            }
            
            print("\n🎉 Daily News Bot 실행 완료!")
            print("=" * 60)
            print(f"📊 최종 결과:")
            print(f"   - 수집된 뉴스: {len(edited_news)}개")
            print(f"   - 발송 성공: {send_result.get('success_count', 0)}명")
            print(f"   - 발송 실패: {send_result.get('fail_count', 0)}명")
            print(f"   - 메시지 길이: {len(message)}자")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Daily News Bot 실행 실패!")
            print(f"오류: {str(e)}")
            print("\n🔍 상세 오류 정보:")
            traceback.print_exc()
            
            self.execution_log["status"] = "failed"
            self.execution_log["error"] = str(e)
            
            return False

def main():
    """메인 실행 함수"""
    try:
        # 봇 인스턴스 생성 및 실행
        bot = DailyNewsBot()
        success = bot.run()
        
        # 종료 코드 설정
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류 발생: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
