"""
데이터 모델 정의
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PatentBasicInfo(BaseModel):
    """특허 기본 정보"""
    application_number: str = Field(..., description="출원번호")
    register_number: Optional[str] = Field(None, description="등록번호")
    invention_title: str = Field(..., description="발명명칭")
    applicant_name: str = Field(..., description="출원인명")
    register_date: Optional[str] = Field(None, description="등록일자")
    register_status: str = Field(..., description="등록상태")
    abstract: Optional[str] = Field(None, description="초록")


class PatentDetailInfo(BaseModel):
    """특허 상세 정보"""
    basic_info: PatentBasicInfo
    claims: List[str] = Field(default_factory=list, description="청구항 목록")
    ipc_codes: List[str] = Field(default_factory=list, description="IPC 코드")
    inventors: List[str] = Field(default_factory=list, description="발명자 목록")
    pdf_url: Optional[str] = Field(None, description="PDF 다운로드 URL")


class SearchRequest(BaseModel):
    """검색 요청"""
    search_keyword: Optional[str] = Field(None, description="검색 키워드")
    right_holder: Optional[str] = Field(None, description="등록권자명")
    right_holder_code: Optional[str] = Field(None, description="등록권자 코드")
    max_patents: Optional[int] = Field(None, description="최대 특허 수", gt=0, le=500)
    page_no: int = Field(1, description="페이지 번호", gt=0)
    include_claims: bool = Field(True, description="청구항 포함 여부")
    include_pdf: bool = Field(False, description="PDF 다운로드 여부")


class SearchResponse(BaseModel):
    """검색 응답"""
    total_count: int = Field(..., description="총 검색 결과 수")
    current_page: int = Field(..., description="현재 페이지")
    patents: List[PatentBasicInfo] = Field(..., description="특허 목록")
    search_time: datetime = Field(default_factory=datetime.now, description="검색 시간")


class ProcessRequest(BaseModel):
    """처리 요청"""
    search_keyword: Optional[str] = Field(None, description="검색 키워드")
    right_holder: Optional[str] = Field(None, description="등록권자명")
    right_holder_code: Optional[str] = Field(None, description="등록권자 코드")
    max_patents: Optional[int] = Field(None, description="최대 특리 수", gt=0, le=500)
    save_claims: bool = Field(True, description="청구항 저장 여부")
    download_pdfs: bool = Field(False, description="PDF 다운로드 여부")


class ProcessStatus(BaseModel):
    """처리 상태"""
    task_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="상태: pending, processing, completed, failed")
    progress: int = Field(0, description="진행률 (0-100)")
    total_patents: int = Field(0, description="총 특허 수")
    processed_patents: int = Field(0, description="처리된 특허 수")
    message: str = Field("", description="메시지")
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")


class ProcessResult(BaseModel):
    """처리 결과"""
    task_id: str = Field(..., description="작업 ID")
    patents: List[PatentDetailInfo] = Field(..., description="처리된 특허 목록")
    claims_saved: int = Field(0, description="저장된 청구항 수")
    pdfs_downloaded: int = Field(0, description="다운로드된 PDF 수")
    summary_report_path: Optional[str] = Field(None, description="요약 보고서 경로")
    output_directory: str = Field(..., description="결과 저장 디렉토리")


class APIResponse(BaseModel):
    """API 응답 기본 형식"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="메시지")
    data: Optional[dict] = Field(None, description="데이터")
    error: Optional[str] = Field(None, description="오류 메시지")


class HealthCheck(BaseModel):
    """헬스 체크"""
    status: str = Field("healthy", description="상태")
    timestamp: datetime = Field(default_factory=datetime.now, description="확인 시간")
    version: str = Field("1.0.0", description="버전")
