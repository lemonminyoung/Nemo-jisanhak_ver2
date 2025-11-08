"""
Version 2 (Gemini Only) 테스트 스크립트 - 새 포맷용
"""

import requests
import json
import time

# 서버 URL
BASE_URL = "http://localhost:8000"

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)
    else:
        print("="*70)


def test_health_check():
    """헬스 체크 테스트"""
    print_separator("1. Health Check Test")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("[OK] Server is healthy")
            print(f"Version: {data.get('version')}")
            print(f"AI Provider: {data.get('ai_provider')}")
        else:
            print(f"[FAIL] Status code: {response.status_code}")

    except Exception as e:
        print(f"[ERROR] {e}")
        print("\nPlease make sure the server is running:")
        print("  python backend_gemini_only.py")


def test_hybrid_analyze_simple():
    """간단한 화학물질 조합 테스트 (2개)"""
    print_separator("2. Simple Test (2 substances)")

    payload = {
        "substances": [
            "Bleach",
            "Ammonia"
        ],
        "use_ai": True
    }

    print(f"Testing: {', '.join(payload['substances'])}")
    print("Analyzing... (this may take 2-5 minutes)")

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/hybrid-analyze",
            json=payload,
            timeout=600  # 10분
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"\n[OK] Analysis complete in {elapsed:.1f} seconds")

            # 새 포맷: simple_response
            simple_resp = result.get('simple_response', {})
            print(f"\nRisk Level: {simple_resp.get('risk_level', 'N/A')}")
            print(f"\nAI Message:")
            print("-" * 70)
            print(simple_resp.get('message', 'No message'))
            print("-" * 70)

            # 안전 링크
            if result.get('safety_links'):
                links = result['safety_links']
                print(f"\nSafety Links:")
                msds = links.get('msds_links', [])
                resources = links.get('general_resources', [])
                print(f"  - MSDS links: {len(msds)}개")
                if msds:
                    for m in msds[:2]:
                        print(f"    • {m.get('title')}")
                print(f"  - General resources: {len(resources)}개")

        else:
            print(f"[FAIL] Status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("[TIMEOUT] Request took too long")
    except Exception as e:
        print(f"[ERROR] {e}")


def test_hybrid_analyze_complex():
    """복잡한 화학물질 조합 테스트 (3개)"""
    print_separator("3. Complex Test (3 substances)")

    payload = {
        "substances": [
            "Hydrochloric Acid",
            "Sodium Hydroxide",
            "Hydrogen Peroxide"
        ],
        "use_ai": True
    }

    print(f"Testing: {', '.join(payload['substances'])}")
    print("Analyzing... (this may take 3-7 minutes)")

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/hybrid-analyze",
            json=payload,
            timeout=600
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"\n[OK] Analysis complete in {elapsed:.1f} seconds")

            simple_resp = result.get('simple_response', {})
            print(f"\nRisk Level: {simple_resp.get('risk_level', 'N/A')}")
            print(f"\nAI Message:")
            print("-" * 70)
            print(simple_resp.get('message', 'No message'))
            print("-" * 70)

            # 결과를 파일로 저장
            output_file = "test_v2_result_new.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"\nFull result saved to: {output_file}")

        else:
            print(f"[FAIL] Status code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.Timeout:
        print("[TIMEOUT] Request took too long")
    except Exception as e:
        print(f"[ERROR] {e}")


def test_without_ai():
    """AI 없이 규칙 기반만 테스트"""
    print_separator("4. Test without AI (rules only)")

    payload = {
        "substances": [
            "Vinegar",
            "Baking Soda"
        ],
        "use_ai": False
    }

    print(f"Testing: {', '.join(payload['substances'])}")
    print("Analyzing... (rules only, faster)")

    start_time = time.time()

    try:
        response = requests.post(
            f"{BASE_URL}/hybrid-analyze",
            json=payload,
            timeout=300
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"\n[OK] Analysis complete in {elapsed:.1f} seconds")

            simple_resp = result.get('simple_response', {})
            print(f"\nRisk Level: {simple_resp.get('risk_level', 'N/A')}")
            print(f"\nMessage (rule-based):")
            print("-" * 70)
            print(simple_resp.get('message', 'No message'))
            print("-" * 70)

        else:
            print(f"[FAIL] Status code: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"[ERROR] {e}")


def main():
    """메인 테스트 실행"""
    print_separator("Chemical Safety Analyzer - Version 2 Test Suite (New Format)")
    print("Testing Gemini-only implementation with Nemo-jisanhak format")

    # 1. 헬스 체크
    test_health_check()

    # 사용자에게 계속할지 물어보기
    print_separator()
    response = input("\nProceed with analysis tests? (y/n): ")

    if response.lower() != 'y':
        print("Test cancelled.")
        return

    # 2. 간단한 테스트
    test_hybrid_analyze_simple()

    # 3. 복잡한 테스트 (선택)
    print_separator()
    response = input("\nRun complex test? (y/n): ")

    if response.lower() == 'y':
        test_hybrid_analyze_complex()

    # 4. AI 없이 테스트
    print_separator()
    response = input("\nRun test without AI? (y/n): ")

    if response.lower() == 'y':
        test_without_ai()

    print_separator("All tests completed!")


if __name__ == "__main__":
    main()
