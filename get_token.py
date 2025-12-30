"""
카카오 Refresh Token 발급 (쉬운 버전)
- 단계별 안내
- 오류 시 계속 진행
- 결과를 파일로 저장
"""

import sys
import webbrowser
from urllib.parse import urlparse, parse_qs

def print_separator():
    print("\n" + "="*70)

def print_step(step_num, title):
    print_separator()
    print(f"📝 Step {step_num}: {title}")
    print("="*70 + "\n")

def main():
    print_separator()
    print("🔑 카카오 Refresh Token 발급 (쉬운 버전)")
    print_separator()
    
    # Step 1: REST API 키 입력
    print_step(1, "REST API 키 입력")
    print("💡 카카오 개발자센터에서 확인:")
    print("   https://developers.kakao.com")
    print("   내 애플리케이션 > 앱 선택 > 앱 키 > REST API 키\n")
    
    rest_api_key = input("REST API 키를 입력하세요: ").strip()
    
    if not rest_api_key:
        print("\n❌ REST API 키를 입력하지 않았습니다!")
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
    
    print(f"\n✅ REST API 키: {rest_api_key[:20]}...")
    
    # Step 2: 인가 코드 받기
    print_step(2, "인가 코드 받기")
    
    redirect_uri = "https://localhost"
    auth_url = f"https://kauth.kakao.com/oauth/authorize?client_id={rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    
    print("🌐 잠시 후 브라우저가 열립니다.")
    print("   브라우저가 안 열리면 아래 URL을 복사해서 직접 여세요:\n")
    print(f"   {auth_url}\n")
    
    input("👆 준비되면 엔터를 누르세요...")
    
    try:
        webbrowser.open(auth_url)
        print("\n✅ 브라우저가 열렸습니다!")
    except:
        print("\n⚠️ 브라우저를 자동으로 열 수 없습니다.")
        print("   위의 URL을 직접 복사해서 브라우저에 붙여넣으세요.")
    
    # Step 3: 리다이렉트 URL 입력
    print_step(3, "리다이렉트 URL 입력")
    
    print("📋 브라우저에서 로그인하면 주소창이 다음과 같이 변경됩니다:")
    print("   https://localhost/?code=긴_영문숫자_조합")
    print("\n⚠️ 주의: '이 사이트에 연결할 수 없음' 오류가 나도 정상입니다!")
    print("   주소창의 URL 전체를 복사해서 붙여넣으세요.\n")
    
    redirected_url = input("리다이렉트된 URL 전체를 붙여넣으세요: ").strip()
    
    if not redirected_url or 'code=' not in redirected_url:
        print("\n❌ 올바른 URL이 아닙니다!")
        print("   URL에 'code='가 포함되어야 합니다.")
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
    
    # 인가 코드 추출
    try:
        parsed_url = urlparse(redirected_url)
        code = parse_qs(parsed_url.query)['code'][0]
        print(f"\n✅ 인가 코드: {code[:30]}...")
    except Exception as e:
        print(f"\n❌ 인가 코드 추출 실패: {str(e)}")
        print("   URL을 다시 확인해주세요.")
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
    
    # Step 4: 토큰 발급
    print_step(4, "토큰 발급 중...")
    
    try:
        import requests
    except ImportError:
        print("❌ requests 패키지가 설치되지 않았습니다!")
        print("   다음 명령어를 실행하세요:")
        print("   pip install requests")
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
    
    token_url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": rest_api_key,
        "redirect_uri": redirect_uri,
        "code": code
    }
    
    try:
        import requests
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        tokens = response.json()
        
        refresh_token = tokens['refresh_token']
        access_token = tokens.get('access_token', '')
        
        # 결과 출력
        print_separator()
        print("✅ 토큰 발급 성공!")
        print_separator()
        
        result_text = f"""
📋 GitHub Secrets에 추가할 값:

{"="*70}
Name:   KAKAO_REST_API_KEY
Secret: {rest_api_key}
{"="*70}
Name:   KAKAO_REFRESH_TOKEN
Secret: {refresh_token}
{"="*70}

⚠️ 다음 단계:
1. GitHub 저장소 > Settings > Secrets and variables > Actions
2. 'New repository secret' 클릭
3. 위의 2개 Secret 추가 (Name과 Secret 복사)
4. GitHub Actions에서 테스트 실행!

💾 이 정보는 'kakao_tokens.txt' 파일에도 저장됩니다.
"""
        
        print(result_text)
        
        # 파일로 저장
        try:
            with open('kakao_tokens.txt', 'w', encoding='utf-8') as f:
                f.write(result_text)
            print("✅ 'kakao_tokens.txt' 파일에 저장 완료!")
        except:
            print("⚠️ 파일 저장 실패 (위의 내용을 직접 복사하세요)")
        
    except Exception as e:
        print(f"\n❌ 토큰 발급 실패: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   서버 응답: {e.response.text}")
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
    
    print_separator()
    input("\n완료! 엔터를 눌러 종료...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 사용자가 취소했습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {str(e)}")
        import traceback
        traceback.print_exc()
        input("\n엔터를 눌러 종료...")
        sys.exit(1)
