"""
태스크 관리 서비스
"""

import uuid
import asyncio
import time
from datetime import datetime
from typing import Dict, Optional
from app.models.schemas import ProcessStatus, ProcessResult, PatentDetailInfo, ProcessRequest
from app.services.patent_processor import patent_processor
from app.core.config import settings


class TaskManager:
    """태스크 관리자"""
    
    def __init__(self):
        self.tasks: Dict[str, ProcessStatus] = {}
        self.results: Dict[str, ProcessResult] = {}
    
    def create_task(self, request: ProcessRequest) -> str:
        """
        새 태스크 생성
        
        Args:
            request: 처리 요청
            
        Returns:
            태스크 ID
        """
        task_id = str(uuid.uuid4())
        
        task_status = ProcessStatus(
            task_id=task_id,
            status="pending",
            progress=0,
            total_patents=0,
            processed_patents=0,
            message="태스크가 생성되었습니다.",
            start_time=datetime.now()
        )
        
        self.tasks[task_id] = task_status
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[ProcessStatus]:
        """
        태스크 상태 조회
        
        Args:
            task_id: 태스크 ID
            
        Returns:
            태스크 상태
        """
        return self.tasks.get(task_id)
    
    def get_task_result(self, task_id: str) -> Optional[ProcessResult]:
        """
        태스크 결과 조회
        
        Args:
            task_id: 태스크 ID
            
        Returns:
            태스크 결과
        """
        return self.results.get(task_id)
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        progress: int = None,
        message: str = None,
        total_patents: int = None,
        processed_patents: int = None
    ) -> None:
        """
        태스크 상태 업데이트
        
        Args:
            task_id: 태스크 ID
            status: 상태
            progress: 진행률
            message: 메시지
            total_patents: 총 특허 수
            processed_patents: 처리된 특허 수
        """
        if task_id not in self.tasks:
            return
        
        task = self.tasks[task_id]
        task.status = status
        
        if progress is not None:
            task.progress = progress
        if message is not None:
            task.message = message
        if total_patents is not None:
            task.total_patents = total_patents
        if processed_patents is not None:
            task.processed_patents = processed_patents
        
        if status == "completed" or status == "failed":
            task.end_time = datetime.now()
    
    async def process_patents_async(self, task_id: str, request: ProcessRequest) -> None:
        """
        비동기 특허 처리
        
        Args:
            task_id: 태스크 ID
            request: 처리 요청
        """
        try:
            self.update_task_status(task_id, "processing", 0, "특허 검색을 시작합니다...")
            
            # 기본값 설정
            search_keyword = request.search_keyword or settings.search_keyword
            right_holder = request.right_holder or settings.right_holder
            right_holder_code = request.right_holder_code or settings.right_holder_code
            max_patents = request.max_patents or settings.max_patents
            
            # 1. 특허 검색
            patents = patent_processor.search_and_extract_patents(
                search_keyword=search_keyword,
                right_holder=right_holder,
                right_holder_code=right_holder_code,
                max_patents=max_patents
            )
            
            if not patents:
                self.update_task_status(task_id, "failed", 0, "검색된 특허가 없습니다.")
                return
            
            self.update_task_status(
                task_id, 
                "processing", 
                10, 
                f"{len(patents)}건의 특허를 찾았습니다. 상세 정보를 처리합니다...",
                total_patents=len(patents)
            )
            
            # 2. 상세 정보 처리
            processed_patents = []
            claims_saved = 0
            pdfs_downloaded = 0
            
            for i, patent_info in enumerate(patents):
                # 상세 정보 처리
                detail_info = patent_processor.process_patent_details(
                    patent_info=patent_info,
                    include_claims=request.save_claims,
                    include_pdf=request.download_pdfs
                )
                
                processed_patents.append(detail_info)
                
                # 통계 업데이트
                if detail_info.claims:
                    claims_saved += 1
                if detail_info.pdf_url and request.download_pdfs:
                    pdfs_downloaded += 1
                
                # 진행률 업데이트
                progress = int(10 + (i + 1) / len(patents) * 80)
                self.update_task_status(
                    task_id,
                    "processing",
                    progress,
                    f"특허 처리 중... ({i + 1}/{len(patents)})",
                    processed_patents=i + 1
                )
                
                # API 호출 제한을 위한 지연
                if i < len(patents) - 1:
                    await asyncio.sleep(settings.delay)
            
            # 3. 요약 보고서 생성
            self.update_task_status(task_id, "processing", 95, "요약 보고서를 생성합니다...")
            
            summary_report_path = patent_processor.create_summary_report(
                patents=processed_patents,
                claims_saved=claims_saved,
                pdfs_downloaded=pdfs_downloaded,
                search_keyword=search_keyword,
                right_holder=right_holder,
                right_holder_code=right_holder_code
            )
            
            # 4. 결과 저장
            result = ProcessResult(
                task_id=task_id,
                patents=processed_patents,
                claims_saved=claims_saved,
                pdfs_downloaded=pdfs_downloaded,
                summary_report_path=summary_report_path,
                output_directory=patent_processor.output_dir
            )
            
            self.results[task_id] = result
            
            self.update_task_status(
                task_id,
                "completed",
                100,
                f"처리 완료! 총 {len(processed_patents)}건의 특허를 처리했습니다."
            )
            
        except Exception as e:
            self.update_task_status(
                task_id,
                "failed",
                message=f"처리 중 오류가 발생했습니다: {str(e)}"
            )
            print(f"태스크 {task_id} 처리 실패: {e}")
    
    def start_background_task(self, task_id: str, request: ProcessRequest) -> None:
        """
        백그라운드 태스크 시작
        
        Args:
            task_id: 태스크 ID
            request: 처리 요청
        """
        # 이벤트 루프에서 비동기 태스크 실행
        asyncio.create_task(self.process_patents_async(task_id, request))


# 전역 태스크 매니저 인스턴스
task_manager = TaskManager()
