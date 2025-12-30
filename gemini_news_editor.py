"""
Gemini AI 뉴스 편집기
- 뉴스 요약 및 인사이트 생성
- API 오류 처리 및 폴백
"""

import os
import time
from typing import Dict, List
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class GeminiNewsEditor:
    """Gemini AI 기반 뉴스 편집기"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY가 설정되지 않았습니다!")
        
        if genai is None:
            raise ImportError("❌ google-generativeai 패키지가 설치되지 않았습니다!")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def edit_single_news(self, news_item: Dict) -> Dict:
        """
        단일 뉴스 편집
        
        Args:
            news_item: 뉴스 데이터
        
        Returns:
            편집된 뉴스 (요약, 인사이트 추가)
        """
        title = news_item.get('title', '')
        description = news_item.get('description', '')
        industry = news_item.get('industry', '기타')
        
        prompt = f"""
다음 {industry} 산업 뉴스를 분석해주세요:

제목: {title}
내용: {description}

요구사항:
1. 핵심 내용을 50자 이내로 요약
2. 산업에 미치는 영향을 30자 이내로 설명

응답 형식:
요약: [50자 이내 요약]
영향: [30자 이내 영향 분석]
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = response.text.strip()
            
            # 파싱
            lines = result.split('\n')
            summary = ""
            insight = ""
            
            for line in lines:
                if line.startswith('요약:'):
                    summary = line.replace('요약:', '').strip()
                elif line.startswith('영향:'):
                    insight = line.replace('영향:', '').strip()
            
            news_item['summary'] = summary[:50] if summary else description[:50]
            news_item['insight'] = insight[:30] if insight else ""
            
            time.sleep(0.5)  # API 호출 제한 방지
            
        except Exception as e:
            print(f"⚠️ AI 편집 실패 (원본 사용): {str(e)}")
            news_item['summary'] = description[:50]
            news_item['insight'] = ""
        
        return news_item
    
    def edit_news_batch(self, news_list: List[Dict]) -> List[Dict]:
        """
        뉴스 배치 편집
        
        Args:
            news_list: 뉴스 리스트
        
        Returns:
            편집된 뉴스 리스트
        """
        edited_news = []
        
        for idx, news in enumerate(news_list, 1):
            try:
                edited = self.edit_single_news(news)
                edited_news.append(edited)
            except Exception as e:
                print(f"⚠️ 뉴스 {idx} 편집 실패: {str(e)}")
                edited_news.append(news)
        
        return edited_news

def test_editor():
    """테스트 실행"""
    print("\n" + "="*70)
    print("🧪 Gemini AI 편집기 테스트")
    print("="*70 + "\n")
    
    test_news = {
        'title': '삼성전자, 3분기 영업이익 10조원 돌파',
        'description': '삼성전자가 3분기 영업이익이 전년 대비 50% 증가한 10조원을 기록했다고 발표했다.',
        'industry': '반도체'
    }
    
    try:
        editor = GeminiNewsEditor()
        edited = editor.edit_single_news(test_news)
        
        print("✅ 편집 완료!")
        print(f"\n제목: {edited['title']}")
        print(f"요약: {edited.get('summary', '')}")
        print(f"영향: {edited.get('insight', '')}")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")

if __name__ == "__main__":
    test_editor()
