"""
등록권자 파라미터 테스트
"""

import requests
import xmltodict
from app.core.config import settings

def test_right_holder_params():
    """등록권자 파라미터 다양한 조합 테스트"""
    
    url = f"{settings.base_url}/getAdvancedSearch"
    
    # 다양한 등록권자 파라미터명 시도
    test_cases = [
        {"name": "rightHoler", "param": "rightHoler"},
        {"name": "rightHolder", "param": "rightHolder"}, 
        {"name": "applicant", "param": "applicant"},
        {"name": "rightHoldr", "param": "rightHoldr"},  # 오타 가능성
    ]
    
    for case in test_cases:
        print(f"=== {case['name']} 파라미터 테스트 ===")
        
        params = {
            case["param"]: "120140131250",
            "patent": "true",
            "utility": "true", 
            "pageNo": 1,
            "numOfRows": 3,
            "ServiceKey": settings.service_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            result = xmltodict.parse(response.content)
            
            print(f"파라미터: {params}")
            print(f"응답: {result}")
            
            # 응답에서 결과 확인
            body = result.get('response', {}).get('body', {})
            if 'count' in body:
                total_count = body['count'].get('totalCount', '0')
                print(f"검색 결과 수: {total_count}")
                if int(total_count) > 0:
                    print(f"✅ {case['name']} 파라미터로 검색 성공!")
                else:
                    print(f"❌ {case['name']} 파라미터로 검색 결과 없음")
            else:
                print(f"❌ {case['name']} 파라미터 응답 구조 이상")
                
        except Exception as e:
            print(f"❌ {case['name']} 파라미터 오류: {e}")
        
        print("-" * 50)
    
    # 특별 테스트: 등록권자명과 코드 함께 사용
    print("=== 등록권자명+코드 조합 테스트 ===")
    params_combo = {
        "rightHoler": "코스맥스 주식회사(120140131250)",
        "patent": "true",
        "utility": "true",
        "pageNo": 1, 
        "numOfRows": 3,
        "ServiceKey": settings.service_key
    }
    
    try:
        response = requests.get(url, params=params_combo, timeout=30)
        result = xmltodict.parse(response.content)
        
        print(f"파라미터: {params_combo}")
        print(f"응답: {result}")
        
        body = result.get('response', {}).get('body', {})
        if 'count' in body:
            total_count = body['count'].get('totalCount', '0')
            print(f"검색 결과 수: {total_count}")
            if int(total_count) > 0:
                print("✅ 등록권자명+코드 조합으로 검색 성공!")
            else:
                print("❌ 등록권자명+코드 조합으로 검색 결과 없음")
        else:
            print("❌ 등록권자명+코드 조합 응답 구조 이상")
            
    except Exception as e:
        print(f"❌ 등록권자명+코드 조합 오류: {e}")

if __name__ == "__main__":
    test_right_holder_params()
