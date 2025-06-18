"""
KIPRIS API 서비스
"""

import requests
import xmltodict
from typing import Optional, Dict, List
from app.core.config import settings


class KiprisAPIService:
    """KIPRIS API 서비스 클래스"""
    
    def __init__(self):
        self.base_url = settings.base_url
        self.service_key = settings.service_key
        self.timeout = settings.timeout
    
    def search_patents(
        self,
        search_keyword: Optional[str] = None,
        right_holder: Optional[str] = None,
        right_holder_code: Optional[str] = None,
        page_no: int = 1,
        num_rows: int = 100
    ) -> Optional[Dict]:
        """
        특허 검색
        
        Args:
            search_keyword: 검색 키워드
            right_holder: 등록권자명
            right_holder_code: 등록권자 코드
            page_no: 페이지 번호
            num_rows: 페이지당 결과 수
            
        Returns:
            검색 결과 딕셔너리
        """
        url = f"{self.base_url}/getAdvancedSearch"
        
        params = {
            "patent": "true",
            "utility": "true",
            "pageNo": page_no,
            "numOfRows": min(num_rows, 500),
            "sortSpec": "PD",
            "descSort": "true",
            "ServiceKey": self.service_key
        }
        
        # 검색 조건 추가 - applicant 파라미터 사용 (실제 작동하는 파라미터)
        if search_keyword and right_holder_code:
            # 방법 1: word 파라미터에 키워드, applicant에 등록권자 코드
            params["word"] = search_keyword
            params["applicant"] = right_holder_code
        elif search_keyword:
            params["word"] = search_keyword
        elif right_holder_code:
            params["applicant"] = right_holder_code
        
        try:
            print(f"특허 검색 URL: {url}")
            print(f"검색 파라미터: {params}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            print(f"요청 URL: {response.url}")
            
            result = xmltodict.parse(response.content)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"특허 검색 요청 실패: {e}")
            return None
        except Exception as e:
            print(f"특허 검색 처리 실패: {e}")
            return None
    
    def search_patents_alternative(
        self,
        search_keyword: Optional[str] = None,
        right_holder_code: Optional[str] = None,
        page_no: int = 1,
        num_rows: int = 100
    ) -> Optional[Dict]:
        """
        대안 검색 방법 - 발명명칭과 초록에서 키워드 검색
        """
        url = f"{self.base_url}/getAdvancedSearch"
        
        params = {
            "patent": "true",
            "utility": "true",
            "pageNo": page_no,
            "numOfRows": min(num_rows, 500),
            "sortSpec": "PD",
            "descSort": "true",
            "ServiceKey": self.service_key
        }
        
        # 대안 검색 방법들 - applicant 파라미터 사용
        if search_keyword and right_holder_code:
            # 방법 1: 발명명칭과 초록에서 키워드 검색 + 등록권자 코드
            params["inventionTitle"] = search_keyword
            params["astrtCont"] = search_keyword
            params["applicant"] = right_holder_code
        elif search_keyword:
            params["inventionTitle"] = search_keyword
            params["astrtCont"] = search_keyword
        elif right_holder_code:
            params["applicant"] = right_holder_code
        
        try:
            print(f"대안 검색 URL: {url}")
            print(f"대안 검색 파라미터: {params}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            print(f"대안 검색 요청 URL: {response.url}")
            
            result = xmltodict.parse(response.content)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"대안 검색 요청 실패: {e}")
            return None
        except Exception as e:
            print(f"대안 검색 처리 실패: {e}")
            return None
    
    def get_patent_details(self, application_number: str) -> Optional[Dict]:
        """
        특허 상세 정보 조회
        
        Args:
            application_number: 출원번호
            
        Returns:
            특허 상세 정보 딕셔너리
        """
        url = f"{self.base_url}/getBibliographyDetailInfoSearch"
        
        params = {
            "applicationNumber": application_number,
            "ServiceKey": self.service_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = xmltodict.parse(response.content)
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"상세정보 조회 실패 ({application_number}): {e}")
            return None
        except Exception as e:
            print(f"상세정보 처리 실패 ({application_number}): {e}")
            return None
    
    def get_pdf_download_url(self, application_number: str) -> Optional[str]:
        """
        PDF 다운로드 URL 조회
        
        Args:
            application_number: 출원번호
            
        Returns:
            PDF 다운로드 URL
        """
        url = f"{self.base_url}/getPubFullTextInfoSearch"
        
        params = {
            "applicationNumber": application_number,
            "ServiceKey": self.service_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = xmltodict.parse(response.content)
            body = result['response']['body']
            
            if 'item' in body and body['item'] and 'path' in body['item']:
                return body['item']['path']
            else:
                print(f"PDF URL을 찾을 수 없습니다: {application_number}")
                return None
                
        except Exception as e:
            print(f"PDF URL 조회 실패 ({application_number}): {e}")
            return None


# 전역 API 서비스 인스턴스
kipris_api = KiprisAPIService()
