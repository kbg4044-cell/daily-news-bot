"""
카카오 Refresh Token 발급 스크립트
- 최초 1회만 실행
- REST API 키와 Refresh Token 발급
"""

import requests
import webbrowser
from urllib.parse import urlparse, parse_qs

def get_kakao_refresh_token():
    """카카오 Refresh Token 발급"""
    
    print("\n" + "="*70)
    print("🔑 카카오 Refresh Token 발급")
    print("="*70 + "\n")
    
    # 1. REST API 키 입력
    print("📝 Step 1: REST API 키 입력")
    print("   카카오 개발자센터 > 앱 > 앱 키 > REST API 키")
    rest_api_key = input("\n   REST API 키: ").strip()
    
    if not rest_api_key:
        print("❌ REST API 키를 입력해주세요!")
        return
    
    redirect_uri = "https://localhost"
    
    # 2. 인가 코드 받기
    print("\n" + "-"*70)
    print("📝 Step 2: 인가 코드 받기")
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    
    print("\n🌐 브라우저가 열립니다. 로그인 후 주소창의 URL을 복사해주세요!")
    print(f"\n만약 브라우저가 안 열리면 아래 URL을 직접 열어주세요:")
    print(f"{auth_url}\n")
    
    try:
        webbrowser.open(auth_url)
    except:
        pass
    
    input("   👆 Enter를 눌러 계속...")
    
    # 3. 리다이렉트 URL 입력
    print("\n" + "-"*70)
    print("📝 Step 3: 리다이렉트 URL 입력")
    print("\n   로그인 후 주소창이 다음과 같이 변경됩니다:")
    print("   https://localhost/?code=긴_영문숫자_조합")
    redirected_url = input("\n   전체 URL을 붙여넣으세요: ").strip()
    
    if not redirected_url or 'code=' not in redirected_url:
        print("❌ 올바른 URL을 입력해주세요!")
        return
    
    # 인가 코드 추출
    try:
        code = parse_qs(urlparse(redirected_url).query)['code'][0]
        print(f"\n   ✅ 인가 코드: {code[:20]}...")
    except:
        print("❌ 인가 코드 추출 실패!")
        return
    
    # 4. 토큰 발급
    print("\n" + "-"*70)
    print("📝 Step 4: 토큰 발급 중...")
    
    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": rest_api_key,
        "redirect_uri": redirect_uri,
        "code": code
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()
        
        refresh_token = tokens['refresh_token']
        
        # 결과 출력
        print("\n" + "="*70)
        print("✅ 토큰 발급 성공!")
        print("="*70 + "\n")
        
        print("📋 GitHub Secrets에 추가할 값:\n")
        print("-"*70)
        print(f"Name:   KAKAO_REST_API_KEY")
        print(f"Secret: {rest_api_key}")
        print("-"*70)
        print(f"Name:   KAKAO_REFRESH_TOKEN")
        print(f"Secret: {refresh_token}")
        print("-"*70 + "\n")
        
        print("⚠️ 다음 단계:")
        print("1. GitHub 저장소 > Settings > Secrets and variables > Actions")
        print("2. 'New repository secret' 클릭")
        print("3. 위의 2개 Secret 추가")
        print("4. GitHub Actions에서 테스트 실행!\n")
        
    except Exception as e:
        print(f"\n❌ 토큰 발급 실패: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"응답: {e.response.text}")

if __name__ == "__main__":
    get_kakao_refresh_token()
