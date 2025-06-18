"""
간단한 KIPRIS API 테스트 스크립트
"""

import requests
import xmltodict
from app.core.config import settings

def test_kipris_api():
    """KIPRIS API 테스트"""
    
    url = f"{settings.base_url}/getAdvancedSearch"
    
    # 테스트 1: 등록권자 코드만으로 검색
    print("=== 테스트 1: 등록권자 코드만 검색 ===")
    params1 = {
        "rightHoler": "120140131250",
        "patent": "true", 
        "utility": "true",
        "pageNo": 1,
        "numOfRows": 5,
        "sortSpec": "PD",
        "descSort": "true",
        "ServiceKey": settings.service_key
    }
    
    print(f"요청 URL: {url}")
    print(f"파라미터: {params1}")
    
    try:
        response = requests.get(url, params=params1, timeout=30)
        print(f"응답 상태 코드: {response.status_code}")
        print(f"실제 요청 URL: {response.url}")
        
        result = xmltodict.parse(response.content)
        print(f"전체 응답 구조: {result}")
        
        total_count = result['response']['body'].get('count', {}).get('totalCount', '0')
        print(f"검색 결과 수: {total_count}")
        
        if int(total_count) > 0:
            print("✅ 등록권자 코드로 검색 성공!")
        else:
            print("❌ 등록권자 코드로 검색 결과 없음")
            
    except Exception as e:
        print(f"오류: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 테스트 2: 키워드 + 등록권자 코드
    print("=== 테스트 2: 키워드 + 등록권자 코드 ===")
    params2 = {
        "word": "조성물",
        "rightHoler": "120140131250", 
        "patent": "true",
        "utility": "true", 
        "pageNo": 1,
        "numOfRows": 5,
        "sortSpec": "PD",
        "descSort": "true",
        "ServiceKey": settings.service_key
    }
    
    print(f"파라미터: {params2}")
    
    try:
        response = requests.get(url, params=params2, timeout=30)
        print(f"응답 상태 코드: {response.status_code}")
        print(f"실제 요청 URL: {response.url}")
        
        result = xmltodict.parse(response.content)
        print(f"전체 응답 구조: {result}")
        
        total_count = result['response']['body'].get('count', {}).get('totalCount', '0')
        print(f"검색 결과 수: {total_count}")
        
        if int(total_count) > 0:
            print("✅ 키워드 + 등록권자 코드로 검색 성공!")
        else:
            print("❌ 키워드 + 등록권자 코드로 검색 결과 없음")
            
    except Exception as e:
        print(f"오류: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 테스트 3: 발명명칭에서 키워드 검색 + 등록권자
    print("=== 테스트 3: 발명명칭 + 등록권자 ===")
    params3 = {
        "inventionTitle": "조성물",
        "rightHoler": "120140131250",
        "patent": "true",
        "utility": "true",
        "pageNo": 1, 
        "numOfRows": 5,
        "sortSpec": "PD",
        "descSort": "true",
        "ServiceKey": settings.service_key
    }
    
    print(f"파라미터: {params3}")
    
    try:
        response = requests.get(url, params=params3, timeout=30)
        print(f"응답 상태 코드: {response.status_code}")
        print(f"실제 요청 URL: {response.url}")
        
        result = xmltodict.parse(response.content)
        print(f"전체 응답 구조: {result}")
        
        total_count = result['response']['body'].get('count', {}).get('totalCount', '0')
        print(f"검색 결과 수: {total_count}")
        
        if int(total_count) > 0:
            print("✅ 발명명칭 + 등록권자로 검색 성공!")
        else:
            print("❌ 발명명칭 + 등록권자로 검색 결과 없음")
            
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    test_kipris_api()
