"""
특정 출원번호의 PDF 다운로드 URL 확인
"""

import requests
import xmltodict
from app.core.config import settings

def test_pdf_download(application_number):
    """특정 출원번호의 PDF 다운로드 테스트"""
    
    url = f"{settings.base_url}/getPubFullTextInfoSearch"
    
    params = {
        "applicationNumber": application_number,
        "ServiceKey": settings.service_key
    }
    
    print(f"=== PDF 다운로드 URL 조회: {application_number} ===")
    print(f"요청 URL: {url}")
    print(f"파라미터: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"응답 상태 코드: {response.status_code}")
        print(f"실제 요청 URL: {response.url}")
        
        result = xmltodict.parse(response.content)
        print(f"전체 응답: {result}")
        
        # 응답 분석
        header = result.get('response', {}).get('header', {})
        body = result.get('response', {}).get('body', {})
        
        print(f"응답 헤더: {header}")
        print(f"응답 바디: {body}")
        
        # PDF URL 확인
        if 'item' in body and body['item']:
            item = body['item']
            if 'path' in item:
                pdf_url = item['path']
                print(f"✅ PDF URL 발견: {pdf_url}")
                
                # PDF 파일명도 확인
                if 'docName' in item:
                    print(f"📄 PDF 파일명: {item['docName']}")
                    
                return pdf_url
            else:
                print(f"❌ item에 path 키가 없음. item 내용: {item}")
        else:
            print(f"❌ 응답에 item이 없거나 비어있음")
            
        return None
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

def test_patent_details(application_number):
    """특허 상세 정보도 함께 확인"""
    
    url = f"{settings.base_url}/getBibliographyDetailInfoSearch"
    
    params = {
        "applicationNumber": application_number,
        "ServiceKey": settings.service_key
    }
    
    print(f"\n=== 특허 상세 정보 조회: {application_number} ===")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        result = xmltodict.parse(response.content)
        
        body = result.get('response', {}).get('body', {})
        if 'item' in body:
            item = body['item']
            
            # 기본 정보 확인
            biblio_info = item.get('biblioSummaryInfoArray', {}).get('biblioSummaryInfo', {})
            if biblio_info:
                print(f"발명명칭: {biblio_info.get('inventionTitle', 'N/A')}")
                print(f"출원일자: {biblio_info.get('applicationDate', 'N/A')}")
                print(f"공개일자: {biblio_info.get('openDate', 'N/A')}")
                print(f"공개번호: {biblio_info.get('openNumber', 'N/A')}")
                print(f"등록상태: {biblio_info.get('registerStatus', 'N/A')}")
                print(f"등록일자: {biblio_info.get('registerDate', 'N/A')}")
                print(f"등록번호: {biblio_info.get('registerNumber', 'N/A')}")
            
            # 이미지 경로 정보 확인
            image_info = item.get('imagePathInfo', {})
            if image_info:
                print(f"📸 이미지 정보: {image_info}")
            
        return result
        
    except Exception as e:
        print(f"❌ 상세 정보 조회 오류: {e}")
        return None

if __name__ == "__main__":
    # 테스트할 출원번호
    test_applications = [
        "1020230152949",  # 문제의 출원번호
        "1020230085505",  # 비교용 (테스트에서 정상 조회된 것)
        "1020230019541"   # 비교용
    ]
    
    for app_num in test_applications:
        print("="*80)
        
        # 1. 특허 상세 정보 확인
        patent_details = test_patent_details(app_num)
        
        # 2. PDF 다운로드 URL 확인
        pdf_url = test_pdf_download(app_num)
        
        print("="*80)
        print()
