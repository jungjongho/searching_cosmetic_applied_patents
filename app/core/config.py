"""
설정 관리 모듈
"""

import json
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # API 설정
    service_key: str = "Qr1mK=WFuP/9i8ZIhJyRH=R2VpyxBo4fyA0pX6V72UE="
    base_url: str = "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice"
    timeout: int = 30
    
    # 검색 설정
    search_keyword: str = "조성물"
    right_holder: str = "코스맥스 주식회사"
    right_holder_code: str = "120140131250"
    max_patents: int = 20
    page_size: int = 100
    delay: float = 1.0
    
    # 출력 설정
    output_dir: str = "patent_results"
    save_search_results: bool = True
    save_claims: bool = True
    download_pdfs: bool = True
    
    # FastAPI 설정
    app_name: str = "화장품 특허 검색 API"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"


class ConfigManager:
    """설정 파일 관리자"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.settings = Settings()
        self.load_config()
    
    def load_config(self) -> None:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # API 설정
                api_settings = config_data.get('api_settings', {})
                self.settings.service_key = api_settings.get('service_key', self.settings.service_key)
                self.settings.base_url = api_settings.get('base_url', self.settings.base_url)
                self.settings.timeout = api_settings.get('timeout', self.settings.timeout)
                
                # 검색 설정
                search_settings = config_data.get('search_settings', {})
                self.settings.search_keyword = search_settings.get('search_keyword', self.settings.search_keyword)
                self.settings.right_holder = search_settings.get('right_holder', self.settings.right_holder)
                self.settings.right_holder_code = search_settings.get('right_holder_code', self.settings.right_holder_code)
                self.settings.max_patents = search_settings.get('max_patents_per_search', self.settings.max_patents)
                self.settings.page_size = search_settings.get('page_size', self.settings.page_size)
                self.settings.delay = search_settings.get('delay_between_requests', self.settings.delay)
                
                # 출력 설정
                output_settings = config_data.get('output_settings', {})
                self.settings.output_dir = output_settings.get('output_directory', self.settings.output_dir)
                self.settings.save_search_results = output_settings.get('save_search_results', self.settings.save_search_results)
                self.settings.save_claims = output_settings.get('save_claims', self.settings.save_claims)
                self.settings.download_pdfs = output_settings.get('download_pdfs', self.settings.download_pdfs)
                
                # FastAPI 설정
                app_settings = config_data.get('app_settings', {})
                self.settings.debug = app_settings.get('debug', self.settings.debug)
                self.settings.host = app_settings.get('host', self.settings.host)
                self.settings.port = app_settings.get('port', self.settings.port)
                
                print(f"설정 파일 '{self.config_file}' 로드 완료")
            else:
                print(f"설정 파일 '{self.config_file}'이 없습니다. 기본값을 사용합니다.")
                self.create_default_config()
                
        except Exception as e:
            print(f"설정 파일 로드 오류: {e}. 기본값을 사용합니다.")
            self.create_default_config()
    
    def create_default_config(self) -> None:
        """기본 설정 파일 생성"""
        default_config = {
            "api_settings": {
                "service_key": "",
                "base_url": "http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice",
                "timeout": 30
            },
            "search_settings": {
                "search_keyword": "조성물",
                "right_holder": "코스맥스 주식회사",
                "right_holder_code": "120140131250",
                "max_patents_per_search": 20,
                "page_size": 100,
                "delay_between_requests": 1.0
            },
            "output_settings": {
                "output_directory": "patent_results",
                "save_search_results": True,
                "save_claims": True,
                "download_pdfs": True
            },
            "app_settings": {
                "debug": False,
                "host": "0.0.0.0",
                "port": 8000
            }
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            print(f"기본 설정 파일 '{self.config_file}' 생성 완료")
        except Exception as e:
            print(f"설정 파일 생성 실패: {e}")
    
    def get_settings(self) -> Settings:
        """설정 반환"""
        return self.settings


# 전역 설정 인스턴스
config_manager = ConfigManager()
settings = config_manager.get_settings()
