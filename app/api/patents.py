"""
특허 검색 API 라우터
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.models.schemas import (
    SearchRequest, SearchResponse, ProcessRequest, ProcessStatus, 
    ProcessResult, APIResponse, PatentBasicInfo
)
from app.services import patent_processor, task_manager
from app.core.config import settings

router = APIRouter(prefix="/patents", tags=["특허 검색"])


@router.post("/search", response_model=SearchResponse)
async def search_patents(request: SearchRequest):
    """
    특허 검색
    
    Args:
        request: 검색 요청
        
    Returns:
        검색 결과
    """
    try:
        # 기본값 설정
        search_keyword = request.search_keyword or settings.search_keyword
        right_holder = request.right_holder or settings.right_holder
        right_holder_code = request.right_holder_code or settings.right_holder_code
        max_patents = request.max_patents or settings.max_patents
        
        # 특허 검색
        patents = patent_processor.search_and_extract_patents(
            search_keyword=search_keyword,
            right_holder=right_holder,
            right_holder_code=right_holder_code,
            max_patents=max_patents
        )
        
        if not patents:
            raise HTTPException(status_code=404, detail="검색된 특허가 없습니다.")
        
        return SearchResponse(
            total_count=len(patents),
            current_page=request.page_no,
            patents=patents
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 실패: {str(e)}")


@router.get("/search/{application_number}")
async def get_patent_detail(application_number: str):
    """
    특허 상세 정보 조회
    
    Args:
        application_number: 출원번호
        
    Returns:
        특허 상세 정보
    """
    try:
        from app.services.kipris_api import kipris_api
        
        # 기본 정보 생성 (실제로는 검색에서 가져와야 함)
        basic_info = PatentBasicInfo(
            application_number=application_number,
            invention_title="상세 조회",
            applicant_name="",
            register_status="",
        )
        
        # 상세 정보 처리
        detail_info = patent_processor.process_patent_details(
            patent_info=basic_info,
            include_claims=True,
            include_pdf=False
        )
        
        return detail_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상세 정보 조회 실패: {str(e)}")


@router.post("/process", response_model=APIResponse)
async def start_patent_processing(
    request: ProcessRequest,
    background_tasks: BackgroundTasks
):
    """
    특허 처리 시작 (비동기)
    
    Args:
        request: 처리 요청
        background_tasks: 백그라운드 태스크
        
    Returns:
        태스크 ID를 포함한 응답
    """
    try:
        # 태스크 생성
        task_id = task_manager.create_task(request)
        
        # 백그라운드에서 처리 시작
        background_tasks.add_task(
            task_manager.start_background_task,
            task_id,
            request
        )
        
        return APIResponse(
            success=True,
            message="특허 처리가 시작되었습니다.",
            data={"task_id": task_id}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 시작 실패: {str(e)}")


@router.get("/process/{task_id}/status", response_model=ProcessStatus)
async def get_processing_status(task_id: str):
    """
    처리 상태 조회
    
    Args:
        task_id: 태스크 ID
        
    Returns:
        처리 상태
    """
    status = task_manager.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")
    
    return status


@router.get("/process/{task_id}/result", response_model=ProcessResult)
async def get_processing_result(task_id: str):
    """
    처리 결과 조회
    
    Args:
        task_id: 태스크 ID
        
    Returns:
        처리 결과
    """
    result = task_manager.get_task_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    
    return result


@router.get("/download/pdf/{application_number}")
async def get_pdf_download_url(application_number: str):
    """
    PDF 다운로드 URL 조회
    
    Args:
        application_number: 출원번호
        
    Returns:
        PDF 다운로드 URL
    """
    try:
        from app.services.kipris_api import kipris_api
        
        pdf_url = kipris_api.get_pdf_download_url(application_number)
        if not pdf_url:
            raise HTTPException(status_code=404, detail="PDF URL을 찾을 수 없습니다.")
        
        return APIResponse(
            success=True,
            message="PDF URL 조회 성공",
            data={"pdf_url": pdf_url}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF URL 조회 실패: {str(e)}")
