"""
화장품 특허 검색 및 분석 시스템 (설정 파일 버전) - 수정된 버전
- 특허 검색 (올바른 API 파라미터 사용)
- 청구항 정리
- 전문 PDF 다운로드
"""

import requests
import xmltodict
import os
import json
from urllib.parse import urlparse
import time
from datetime import datetime

class CosmeticsPatentSearcherWithConfig:
    def __init__(self, config_file="config.json"):
        """
        화장품 특허 검색기 초기화 (설정 파일 사용)
        
        Args:
            config_file (str): 설정 파일 경로
        """
        self.load_config(config_file)
        self.create_output_directories()
    
    def load_config(self, config_file):
        """설정 파일 로드"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # API 설정
            api_settings = config.get('api_settings', {})
            self.service_key = api_settings.get('service_key', '')
            self.base_url = api_settings.get('base_url', 'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice')
            self.timeout = api_settings.get('timeout', 30)
            
            # 검색 설정 - 수정된 부분
            search_settings = config.get('search_settings', {})
            self.search_keyword = search_settings.get('search_keyword', '조성물')
            self.right_holder = search_settings.get('right_holder', '코스맥스 주식회사')
            self.right_holder_code = search_settings.get('right_holder_code', '120140131250')
            self.max_patents = search_settings.get('max_patents_per_search', 20)
            self.page_size = search_settings.get('page_size', 100)
            self.delay = search_settings.get('delay_between_requests', 1)
            
            # 출력 설정
            output_settings = config.get('output_settings', {})
            self.output_dir = output_settings.get('output_directory', 'patent_results')
            self.save_search_results = output_settings.get('save_search_results', True)
            self.save_claims = output_settings.get('save_claims', True)
            self.download_pdfs = output_settings.get('download_pdfs', True)
            
            print(f"설정 파일 '{config_file}' 로드 완료")
            
        except FileNotFoundError:
            print(f"설정 파일 '{config_file}'을 찾을 수 없습니다. 기본값을 사용합니다.")
            self.use_default_config()
        except json.JSONDecodeError as e:
            print(f"설정 파일 파싱 오류: {e}. 기본값을 사용합니다.")
            self.use_default_config()
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}. 기본값을 사용합니다.")
            self.use_default_config()
    
    def use_default_config(self):
        """기본 설정 사용"""
        self.service_key = ''
        self.base_url = 'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice'
        self.timeout = 30
        self.search_keyword = '조성물'
        self.right_holder = '코스맥스 주식회사'
        self.right_holder_code = '120140131250'
        self.max_patents = 20
        self.page_size = 100
        self.delay = 1
        self.output_dir = 'patent_results'
        self.save_search_results = True
        self.save_claims = True
        self.download_pdfs = True
    
    def create_output_directories(self):
        """결과 저장을 위한 디렉토리 생성"""
        directories = [self.output_dir]
        
        if self.save_claims:
            directories.append(os.path.join(self.output_dir, "claims"))
        
        if self.download_pdfs:
            directories.append(os.path.join(self.output_dir, "pdf_files"))
        
        if self.save_search_results:
            directories.append(os.path.join(self.output_dir, "search_results"))
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def search_patents(self, search_keyword=None, right_holder=None, right_holder_code=None, num_rows=None, page_no=1):
        """
        특허 검색 수행 - 수정된 버전
        
        Args:
            search_keyword (str): 검색 키워드 (None이면 기본값 사용)
            right_holder (str): 등록권자명 (None이면 기본값 사용)
            right_holder_code (str): 등록권자 코드 (None이면 기본값 사용)
            num_rows (int): 페이지당 결과 수 (None이면 기본값 사용)
            page_no (int): 페이지 번호
            
        Returns:
            dict: 검색 결과
        """
        if search_keyword is None:
            search_keyword = self.search_keyword
        
        if right_holder is None:
            right_holder = self.right_holder
            
        if right_holder_code is None:
            right_holder_code = self.right_holder_code
        
        if num_rows is None:
            num_rows = min(self.page_size, 500)
        
        url = f"{self.base_url}/getAdvancedSearch"
        
        # 올바른 API 파라미터 구성
        params = {
            "word": search_keyword,  # 자유검색으로 키워드 검색
            "rightHoler": f"{right_holder}({right_holder_code})",  # 등록권자 정보
            "patent": "true",
            "utility": "true", 
            "pageNo": page_no,
            "numOfRows": num_rows,
            "sortSpec": "PD",  # 공고일자 기준 정렬
            "descSort": "true",  # 내림차순
            "ServiceKey": self.service_key
        }
        
        try:
            print(f"특허 검색 중:")
            print(f"  - 키워드: {search_keyword}")
            print(f"  - 등록권자: {right_holder}({right_holder_code})")
            print(f"  - 페이지: {page_no}, 결과수: {num_rows}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            # XML을 딕셔너리로 변환
            result = xmltodict.parse(response.content)
            
            # 검색 결과 저장
            if self.save_search_results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_file = os.path.join(
                    self.output_dir, 
                    "search_results", 
                    f"search_result_{search_keyword}_{right_holder_code}_{timestamp}.json"
                )
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"검색 결과 저장: {result_file}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"검색 요청 실패: {e}")
            return None
        except Exception as e:
            print(f"검색 처리 실패: {e}")
            return None
    
    def search_patents_alternative(self, search_keyword=None, right_holder_code=None, num_rows=None, page_no=1):
        """
        대안 검색 방법 - 발명의명칭이나 초록에서 키워드 검색
        
        Args:
            search_keyword (str): 검색 키워드
            right_holder_code (str): 등록권자 코드
            num_rows (int): 페이지당 결과 수
            page_no (int): 페이지 번호
            
        Returns:
            dict: 검색 결과
        """
        if search_keyword is None:
            search_keyword = self.search_keyword
            
        if right_holder_code is None:
            right_holder_code = self.right_holder_code
        
        if num_rows is None:
            num_rows = min(self.page_size, 500)
        
        url = f"{self.base_url}/getAdvancedSearch"
        
        # 대안 파라미터 구성 - 발명의명칭과 초록에서 키워드 검색
        params = {
            "inventionTitle": search_keyword,  # 발명의명칭에서 검색
            "astrtCont": search_keyword,       # 초록에서 검색
            "rightHoler": right_holder_code,   # 등록권자 코드만 사용
            "patent": "true",
            "utility": "true", 
            "pageNo": page_no,
            "numOfRows": num_rows,
            "sortSpec": "PD",
            "descSort": "true",
            "ServiceKey": self.service_key
        }
        
        try:
            print(f"대안 검색 방법 시도:")
            print(f"  - 키워드: {search_keyword}")
            print(f"  - 등록권자 코드: {right_holder_code}")
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            result = xmltodict.parse(response.content)
            
            # 검색 결과 저장
            if self.save_search_results:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                result_file = os.path.join(
                    self.output_dir, 
                    "search_results", 
                    f"search_result_alt_{search_keyword}_{right_holder_code}_{timestamp}.json"
                )
                
                with open(result_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                
                print(f"대안 검색 결과 저장: {result_file}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"대안 검색 요청 실패: {e}")
            return None
        except Exception as e:
            print(f"대안 검색 처리 실패: {e}")
            return None
    
    def extract_patent_list(self, search_result):
        """
        검색 결과에서 특허 목록 추출
        
        Args:
            search_result (dict): 검색 결과
            
        Returns:
            list: 특허 정보 리스트
        """
        try:
            body = search_result['response']['body']
            
            if 'items' not in body or not body['items']:
                print("검색 결과가 없습니다.")
                return []
            
            # items가 단일 항목인지 리스트인지 확인
            items = body['items']['item']
            if isinstance(items, dict):
                items = [items]
            elif not isinstance(items, list):
                print("예상하지 못한 데이터 형식입니다.")
                return []
            
            patents = []
            for item in items:
                patent_info = {
                    'application_number': item.get('applicationNumber', ''),
                    'register_number': item.get('registerNumber', ''),
                    'invention_title': item.get('inventionTitle', ''),
                    'applicant_name': item.get('applicantName', ''),
                    'register_date': item.get('registerDate', ''),
                    'register_status': item.get('registerStatus', ''),
                    'abstract': item.get('astrtCont', '')
                }
                patents.append(patent_info)
            
            total_count = body.get('count', {}).get('totalCount', 0)
            print(f"총 {total_count}건의 특허가 검색되었습니다.")
            print(f"현재 페이지에서 {len(patents)}건을 추출했습니다.")
            
            return patents
            
        except Exception as e:
            print(f"특허 목록 추출 실패: {e}")
            return []
    
    def get_patent_details(self, application_number):
        """
        특허의 상세 정보 조회 (청구항 포함)
        
        Args:
            application_number (str): 출원번호
            
        Returns:
            dict: 특허 상세 정보
        """
        url = f"{self.base_url}/getBibliographyDetailInfoSearch"
        
        params = {
            "applicationNumber": application_number,
            "ServiceKey": self.service_key
        }
        
        try:
            print(f"특허 상세정보 조회 중: {application_number}")
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
    
    def extract_claims(self, patent_details):
        """
        특허 상세정보에서 청구항 추출
        
        Args:
            patent_details (dict): 특허 상세정보
            
        Returns:
            list: 청구항 리스트
        """
        try:
            body = patent_details['response']['body']['item']
            
            if 'claimInfoArray' not in body or not body['claimInfoArray']:
                return []
            
            claim_info_array = body['claimInfoArray']
            if 'claimInfo' not in claim_info_array:
                return []
            
            claim_info = claim_info_array['claimInfo']
            if isinstance(claim_info, dict):
                claim_info = [claim_info]
            
            claims = []
            for claim in claim_info:
                if 'claim' in claim and claim['claim']:
                    claims.append(claim['claim'])
            
            return claims
            
        except Exception as e:
            print(f"청구항 추출 실패: {e}")
            return []
    
    def save_claims_to_file(self, application_number, invention_title, claims):
        """
        청구항을 파일로 저장
        
        Args:
            application_number (str): 출원번호
            invention_title (str): 발명명칭
            claims (list): 청구항 리스트
        """
        if not self.save_claims:
            return
            
        try:
            # 파일명에서 특수문자 제거
            safe_title = "".join(c for c in invention_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            filename = f"{application_number}_{safe_title}_청구항.txt"
            filepath = os.path.join(self.output_dir, "claims", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"출원번호: {application_number}\n")
                f.write(f"발명명칭: {invention_title}\n")
                f.write(f"청구항 수: {len(claims)}개\n")
                f.write("="*80 + "\n\n")
                
                for i, claim in enumerate(claims, 1):
                    f.write(f"청구항 {i}:\n")
                    f.write(f"{claim}\n\n")
                    f.write("-"*60 + "\n\n")
            
            print(f"청구항 저장 완료: {filepath}")
            
        except Exception as e:
            print(f"청구항 저장 실패 ({application_number}): {e}")
    
    def get_pdf_download_url(self, application_number):
        """
        특허 전문 PDF 다운로드 URL 조회
        
        Args:
            application_number (str): 출원번호
            
        Returns:
            str: PDF 다운로드 URL
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
    
    def download_pdf_file(self, application_number, invention_title, pdf_url):
        """
        PDF 파일 다운로드
        
        Args:
            application_number (str): 출원번호
            invention_title (str): 발명명칭
            pdf_url (str): PDF 다운로드 URL
        """
        if not self.download_pdfs:
            return
            
        try:
            # 파일명에서 특수문자 제거
            safe_title = "".join(c for c in invention_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            filename = f"{application_number}_{safe_title}.pdf"
            filepath = os.path.join(self.output_dir, "pdf_files", filename)
            
            print(f"PDF 다운로드 중: {application_number}")
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"PDF 다운로드 완료: {filepath}")
            
        except Exception as e:
            print(f"PDF 다운로드 실패 ({application_number}): {e}")
    
    def process_patents(self, search_keyword=None, right_holder=None, right_holder_code=None, max_patents=None):
        """
        특허 검색부터 청구항 정리 및 PDF 다운로드까지 전체 프로세스 실행
        
        Args:
            search_keyword (str): 검색 키워드 (None이면 기본값 사용)
            right_holder (str): 등록권자명 (None이면 기본값 사용)
            right_holder_code (str): 등록권자 코드 (None이면 기본값 사용)
            max_patents (int): 처리할 최대 특허 수 (None이면 기본값 사용)
        """
        if search_keyword is None:
            search_keyword = self.search_keyword
            
        if right_holder is None:
            right_holder = self.right_holder
            
        if right_holder_code is None:
            right_holder_code = self.right_holder_code
            
        if max_patents is None:
            max_patents = self.max_patents
        
        print("="*80)
        print("화장품 특허 검색 및 분석 시작")
        print(f"검색 키워드: {search_keyword}")
        print(f"등록권자: {right_holder}({right_holder_code})")
        print(f"최대 처리 특허 수: {max_patents}")
        print("="*80)
        
        if not self.service_key:
            print("경고: KIPRIS API 서비스 키가 설정되지 않았습니다.")
            print("config.json 파일의 service_key를 설정해주세요.")
            return
        
        # 1. 첫 번째 방법으로 특허 검색
        search_result = self.search_patents(search_keyword, right_holder, right_holder_code, num_rows=min(max_patents, 500))
        patents = []
        
        if search_result:
            patents = self.extract_patent_list(search_result)
        
        # 첫 번째 방법으로 결과가 없으면 대안 방법 시도
        if not patents:
            print("\n첫 번째 검색 방법으로 결과가 없습니다. 대안 방법을 시도합니다...")
            search_result = self.search_patents_alternative(search_keyword, right_holder_code, num_rows=min(max_patents, 500))
            if search_result:
                patents = self.extract_patent_list(search_result)
        
        if not patents:
            print("검색된 특허가 없습니다.")
            return
        
        # 처리할 특허 수 제한
        patents = patents[:max_patents]
        
        print(f"\n{len(patents)}건의 특허를 처리합니다.")
        
        # 결과 요약을 위한 변수
        claims_saved = 0
        pdfs_downloaded = 0
        
        # 3. 각 특허에 대해 상세정보 조회 및 처리
        for i, patent in enumerate(patents, 1):
            print(f"\n[{i}/{len(patents)}] 처리 중: {patent['application_number']}")
            print(f"발명명칭: {patent['invention_title']}")
            print(f"출원인: {patent['applicant_name']}")
            print(f"등록상태: {patent['register_status']}")
            
            # 상세정보 조회
            details = self.get_patent_details(patent['application_number'])
            if not details:
                print("상세정보 조회 실패, 다음 특허로 이동")
                continue
            
            # 청구항 추출 및 저장
            if self.save_claims:
                claims = self.extract_claims(details)
                if claims:
                    self.save_claims_to_file(
                        patent['application_number'], 
                        patent['invention_title'], 
                        claims
                    )
                    claims_saved += 1
                else:
                    print("청구항을 찾을 수 없습니다.")
            
            # PDF 다운로드
            if self.download_pdfs:
                pdf_url = self.get_pdf_download_url(patent['application_number'])
                if pdf_url:
                    self.download_pdf_file(
                        patent['application_number'], 
                        patent['invention_title'], 
                        pdf_url
                    )
                    pdfs_downloaded += 1
                else:
                    print("PDF를 다운로드할 수 없습니다.")
            
            # API 호출 간격 조정 (과부하 방지)
            if i < len(patents):  # 마지막이 아닌 경우에만 지연
                time.sleep(self.delay)
        
        # 요약 보고서 생성
        self.create_summary_report(patents, claims_saved, pdfs_downloaded, search_keyword, right_holder, right_holder_code)
        
        # 결과 요약 출력
        print("\n" + "="*80)
        print("처리 완료!")
        print(f"총 처리된 특허: {len(patents)}건")
        if self.save_claims:
            print(f"청구항 저장: {claims_saved}건")
        if self.download_pdfs:
            print(f"PDF 다운로드: {pdfs_downloaded}건")
        print(f"결과 저장 위치: {os.path.abspath(self.output_dir)}")
        print("="*80)
    
    def create_summary_report(self, patents, claims_saved, pdfs_downloaded, search_keyword, right_holder, right_holder_code):
        """
        처리된 특허들의 요약 보고서 생성
        
        Args:
            patents (list): 특허 정보 리스트
            claims_saved (int): 저장된 청구항 수
            pdfs_downloaded (int): 다운로드된 PDF 수
            search_keyword (str): 검색 키워드
            right_holder (str): 등록권자명
            right_holder_code (str): 등록권자 코드
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(self.output_dir, f"summary_report_{timestamp}.txt")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("화장품 특허 검색 결과 요약 보고서\n")
                f.write("="*80 + "\n\n")
                f.write(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"검색 키워드: {search_keyword}\n")
                f.write(f"등록권자: {right_holder}({right_holder_code})\n")
                f.write(f"총 특허 수: {len(patents)}건\n")
                if self.save_claims:
                    f.write(f"청구항 저장: {claims_saved}건\n")
                if self.download_pdfs:
                    f.write(f"PDF 다운로드: {pdfs_downloaded}건\n")
                f.write("\n")
                
                # 등록상태별 통계
                status_count = {}
                for patent in patents:
                    status = patent['register_status']
                    status_count[status] = status_count.get(status, 0) + 1
                
                f.write("등록상태별 분포:\n")
                f.write("-"*40 + "\n")
                for status, count in status_count.items():
                    f.write(f"{status}: {count}건\n")
                f.write("\n")
                
                # 상세 목록
                f.write("상세 목록:\n")
                f.write("-"*40 + "\n")
                for i, patent in enumerate(patents, 1):
                    f.write(f"{i}. {patent['application_number']}\n")
                    f.write(f"   발명명칭: {patent['invention_title']}\n")
                    f.write(f"   출원인: {patent['applicant_name']}\n")
                    f.write(f"   등록상태: {patent['register_status']}\n")
                    f.write(f"   등록일자: {patent['register_date']}\n\n")
            
            print(f"요약 보고서 생성: {report_file}")
            
        except Exception as e:
            print(f"요약 보고서 생성 실패: {e}")


def main():
    """메인 실행 함수"""
    print("화장품 특허 검색 시스템 시작 (수정된 버전)")
    print("설정 파일: config.json")
    
    # 검색기 생성 및 실행
    searcher = CosmeticsPatentSearcherWithConfig()
    
    # 사용자 입력으로 검색어와 최대 특허 수 설정 가능
    import sys
    
    search_keyword = None
    right_holder = None
    right_holder_code = None
    max_patents = None
    
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        search_keyword = sys.argv[1]
    if len(sys.argv) > 2:
        right_holder = sys.argv[2]
    if len(sys.argv) > 3:
        right_holder_code = sys.argv[3]
    if len(sys.argv) > 4:
        try:
            max_patents = int(sys.argv[4])
        except ValueError:
            print("최대 특허 수는 숫자여야 합니다. 기본값을 사용합니다.")
    
    # 검색 및 처리 실행
    searcher.process_patents(search_keyword, right_holder, right_holder_code, max_patents)


if __name__ == "__main__":
    main()
