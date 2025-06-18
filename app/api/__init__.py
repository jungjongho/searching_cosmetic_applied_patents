"""
API 라우터 초기화
"""

from .patents import router as patents_router

__all__ = ["patents_router"]
