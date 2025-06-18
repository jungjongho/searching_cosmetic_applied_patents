"""
특허 처리 서비스
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from app.core.config import settings
from app.models.schemas import PatentBasicInfo, PatentDetailInfo
from app.services.kipris_api import kipris_api


class PatentProcessor:
    """특허 처리 서비스"""
    
    def __init__(self):
        self.output_dir = settings.output_dir
        self.create_output_directories()
    
    def create_output_directories(self) -> None:
        """결과 저장을 위한 디렉토리 생성"""
        directories = [self.output_dir]
        
        if settings.save_claims:
            directories.append(os.path.join(self.output_dir, "claims"))
        
        if settings.download_pdfs:
            directories.append(os.path.join(self.output_dir, "pdf_files"))
        
        if settings.save_search_results:
            directories.append(os.path.join(self.output_dir, "search_results"))
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def extract_patent_list(self, search_result: Dict) -> List[PatentBasicInfo]:
        """
        검색 결과에서 특허 목록 추출
        
        Args:
            search_result: 검색 결과 딕셔너리
            
        Returns:
            특허 기본 정보 리스트
        """
        try:
            body = search_result['response']['body']
            
            if 'items' not in body or not body['items']:
                return []
            
            items = body['items']['item']
            if isinstance(items, dict):
                items = [items]
            elif not isinstance(items, list):
                return []
            
            patents = []
            for item in items:
                patent_info = PatentBasicInfo(
                    application_number=item.get('applicationNumber', ''),
                    register_number=item.get('registerNumber', ''),
                    invention_title=item.get('inventionTitle', ''),
                    applicant_name=item.get('applicantName', ''),
                    register_date=item.get('registerDate', ''),
                    register_status=item.get('registerStatus', ''),
                    abstract=item.get('astrtCont', '')
                )
                patents.append(patent_info)
            
            return patents
            
        except Exception as e:
            print(f"특허 목록 추출 실패: {e}")
            return []
    
    def extract_claims(self, patent_details: Dict) -> List[str]:
        """
        특허 상세정보에서 청구항 추출
        
        Args:
            patent_details: 특허 상세정보 딕셔너리
            
        Returns:
            청구항 리스트
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
    
    def extract_ipc_codes(self, patent_details: Dict) -> List[str]:
        """IPC 코드 추출"""
        try:
            body = patent_details['response']['body']['item']
            
            if 'ipcInfoArray' not in body or not body['ipcInfoArray']:
                return []
            
            ipc_info_array = body['ipcInfoArray']
            if 'ipcInfo' not in ipc_info_array:
                return []
            
            ipc_info = ipc_info_array['ipcInfo']
            if isinstance(ipc_info, dict):
                ipc_info = [ipc_info]
            
            ipc_codes = []
            for ipc in ipc_info:
                if 'ipcNumber' in ipc and ipc['ipcNumber']:
                    ipc_codes.append(ipc['ipcNumber'])
            
            return ipc_codes
            
        except Exception as e:
            print(f"IPC 코드 추출 실패: {e}")
            return []
    
    def extract_inventors(self, patent_details: Dict) -> List[str]:
        """발명자 정보 추출"""
        try:
            body = patent_details['response']['body']['item']
            
            if 'inventorInfoArray' not in body or not body['inventorInfoArray']:
                return []
            
            inventor_info_array = body['inventorInfoArray']
            if 'inventorInfo' not in inventor_info_array:
                return []
            
            inventor_info = inventor_info_array['inventorInfo']
            if isinstance(inventor_info, dict):
                inventor_info = [inventor_info]
            
            inventors = []
            for inventor in inventor_info:
                if 'name' in inventor and inventor['name']:
                    inventors.append(inventor['name'])
            
            return inventors
            
        except Exception as e:
            print(f"발명자 정보 추출 실패: {e}")
            return []
    
    def save_claims_to_file(self, patent_info: PatentBasicInfo, claims: List[str]) -> None:
        """
        청구항을 파일로 저장
        
        Args:
            patent_info: 특허 기본 정보
            claims: 청구항 리스트
        """
        if not settings.save_claims:
            return
            
        try:
            safe_title = "".join(c for c in patent_info.invention_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            filename = f"{patent_info.application_number}_{safe_title}_청구항.txt"
            filepath = os.path.join(self.output_dir, "claims", filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"출원번호: {patent_info.application_number}\n")
                f.write(f"발명명칭: {patent_info.invention_title}\n")
                f.write(f"청구항 수: {len(claims)}개\n")
                f.write("="*80 + "\n\n")
                
                for i, claim in enumerate(claims, 1):
                    f.write(f"청구항 {i}:\n")
                    f.write(f"{claim}\n\n")
                    f.write("-"*60 + "\n\n")
            
            print(f"청구항 저장 완료: {filepath}")
            
        except Exception as e:
            print(f"청구항 저장 실패 ({patent_info.application_number}): {e}")
    
    def download_pdf_file(self, patent_info: PatentBasicInfo, pdf_url: str) -> bool:
        """
        PDF 파일 다운로드
        
        Args:
            patent_info: 특허 기본 정보
            pdf_url: PDF 다운로드 URL
            
        Returns:
            다운로드 성공 여부
        """
        if not settings.download_pdfs:
            return False
            
        try:
            safe_title = "".join(c for c in patent_info.invention_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            filename = f"{patent_info.application_number}_{safe_title}.pdf"
            filepath = os.path.join(self.output_dir, "pdf_files", filename)
            
            print(f"PDF 다운로드 중: {patent_info.application_number}")
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"PDF 다운로드 완료: {filepath}")
            return True
            
        except Exception as e:
            print(f"PDF 다운로드 실패 ({patent_info.application_number}): {e}")
            return False
    
    def save_search_results(self, search_result: Dict, search_keyword: str, right_holder_code: str) -> None:
        """검색 결과 저장"""
        if not settings.save_search_results:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            result_file = os.path.join(
                self.output_dir,
                "search_results",
                f"search_result_{search_keyword}_{right_holder_code}_{timestamp}.json"
            )
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(search_result, f, ensure_ascii=False, indent=2)
            
            print(f"검색 결과 저장: {result_file}")
            
        except Exception as e:
            print(f"검색 결과 저장 실패: {e}")
    
    def create_summary_report(
        self,
        patents: List[PatentDetailInfo],
        claims_saved: int,
        pdfs_downloaded: int,
        search_keyword: str,
        right_holder: str,
        right_holder_code: str
    ) -> str:
        """
        요약 보고서 생성
        
        Args:
            patents: 처리된 특허 목록
            claims_saved: 저장된 청구항 수
            pdfs_downloaded: 다운로드된 PDF 수
            search_keyword: 검색 키워드
            right_holder: 등록권자명
            right_holder_code: 등록권자 코드
            
        Returns:
            요약 보고서 파일 경로
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
                f.write(f"청구항 저장: {claims_saved}건\n")
                f.write(f"PDF 다운로드: {pdfs_downloaded}건\n")
                f.write("\n")
                
                # 등록상태별 통계
                status_count = {}
                for patent in patents:
                    status = patent.basic_info.register_status
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
                    f.write(f"{i}. {patent.basic_info.application_number}\n")
                    f.write(f"   발명명칭: {patent.basic_info.invention_title}\n")
                    f.write(f"   출원인: {patent.basic_info.applicant_name}\n")
                    f.write(f"   등록상태: {patent.basic_info.register_status}\n")
                    f.write(f"   등록일자: {patent.basic_info.register_date}\n")
                    f.write(f"   청구항 수: {len(patent.claims)}개\n\n")
            
            print(f"요약 보고서 생성: {report_file}")
            return report_file
            
        except Exception as e:
            print(f"요약 보고서 생성 실패: {e}")
            return ""
    
    def search_and_extract_patents(
        self,
        search_keyword: Optional[str] = None,
        right_holder: Optional[str] = None,
        right_holder_code: Optional[str] = None,
        max_patents: Optional[int] = None
    ) -> List[PatentBasicInfo]:
        """
        특허 검색 및 목록 추출
        
        Args:
            search_keyword: 검색 키워드
            right_holder: 등록권자명  
            right_holder_code: 등록권자 코드
            max_patents: 최대 특허 수
            
        Returns:
            특허 기본 정보 리스트
        """
        # 기본값 설정
        if search_keyword is None:
            search_keyword = settings.search_keyword
        if right_holder is None:
            right_holder = settings.right_holder
        if right_holder_code is None:
            right_holder_code = settings.right_holder_code
        if max_patents is None:
            max_patents = settings.max_patents
        
        # 첫 번째 방법으로 검색
        search_result = kipris_api.search_patents(
            search_keyword=search_keyword,
            right_holder=right_holder,
            right_holder_code=right_holder_code,
            num_rows=min(max_patents, 500)
        )
        
        patents = []
        if search_result:
            patents = self.extract_patent_list(search_result)
            self.save_search_results(search_result, search_keyword, right_holder_code)
        
        # 첫 번째 방법으로 결과가 없으면 대안 방법 시도
        if not patents:
            print("첫 번째 검색 방법으로 결과가 없습니다. 대안 방법을 시도합니다...")
            search_result = kipris_api.search_patents_alternative(
                search_keyword=search_keyword,
                right_holder_code=right_holder_code,
                num_rows=min(max_patents, 500)
            )
            
            if search_result:
                patents = self.extract_patent_list(search_result)
                self.save_search_results(search_result, f"{search_keyword}_alt", right_holder_code)
        
        # 최대 특허 수 제한
        patents = patents[:max_patents]
        
        return patents
    
    def process_patent_details(
        self,
        patent_info: PatentBasicInfo,
        include_claims: bool = True,
        include_pdf: bool = False
    ) -> PatentDetailInfo:
        """
        특허 상세 정보 처리
        
        Args:
            patent_info: 특허 기본 정보
            include_claims: 청구항 포함 여부
            include_pdf: PDF 다운로드 여부
            
        Returns:
            특허 상세 정보
        """
        detail_info = PatentDetailInfo(basic_info=patent_info)
        
        # 상세 정보 조회
        patent_details = kipris_api.get_patent_details(patent_info.application_number)
        if not patent_details:
            return detail_info
        
        # 청구항 추출
        if include_claims:
            claims = self.extract_claims(patent_details)
            detail_info.claims = claims
            
            if claims and settings.save_claims:
                self.save_claims_to_file(patent_info, claims)
        
        # IPC 코드 추출
        detail_info.ipc_codes = self.extract_ipc_codes(patent_details)
        
        # 발명자 정보 추출
        detail_info.inventors = self.extract_inventors(patent_details)
        
        # PDF 다운로드 (공개 상태인 경우에만 가능)
        if include_pdf:
            # 등록 상태 확인
            register_status = patent_info.register_status.strip()
            
            if register_status == '공개':
                pdf_url = kipris_api.get_pdf_download_url(patent_info.application_number)
                if pdf_url:
                    detail_info.pdf_url = pdf_url
                    if settings.download_pdfs:
                        success = self.download_pdf_file(patent_info, pdf_url)
                        if not success:
                            print(f"⚠️ PDF 다운로드 실패: {patent_info.application_number}")
                else:
                    print(f"⚠️ PDF URL을 찾을 수 없음: {patent_info.application_number}")
            else:
                print(f"📝 등록된 특허는 공개 전문 PDF가 제공되지 않음: {patent_info.application_number} (상태: {register_status})")
        
        return detail_info


# 전역 특허 처리기 인스턴스
patent_processor = PatentProcessor()
