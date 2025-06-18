"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import patents_router
from app.core.config import settings
from app.models.schemas import HealthCheck

# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="화장품 특허 검색 및 분석 API",
    debug=settings.debug
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영 환경에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(patents_router)


@app.get("/", response_model=HealthCheck)
async def root():
    """루트 엔드포인트 - 헬스 체크"""
    return HealthCheck(
        status="healthy",
        version=settings.app_version
    )


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """헬스 체크 엔드포인트"""
    return HealthCheck(
        status="healthy",
        version=settings.app_version
    )


@app.get("/settings")
async def get_settings():
    """현재 설정 조회"""
    return {
        "search_keyword": settings.search_keyword,
        "right_holder": settings.right_holder,
        "right_holder_code": settings.right_holder_code,
        "max_patents": settings.max_patents,
        "output_dir": settings.output_dir,
        "save_claims": settings.save_claims,
        "download_pdfs": settings.download_pdfs
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
