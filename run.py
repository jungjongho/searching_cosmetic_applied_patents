"""
화장품 특허 검색 시스템 실행 파일
"""

import sys
import os
import argparse
import uvicorn
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import app
from app.core.config import settings
from app.services.patent_processor import patent_processor


def run_api_server():
    """FastAPI 서버 실행"""
    print(f"🚀 {settings.app_name} 시작")
    print(f"📍 서버 주소: http://{settings.host}:{settings.port}")
    print(f"📖 API 문서: http://{settings.host}:{settings.port}/docs")
    print(f"🔧 디버그 모드: {settings.debug}")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )


def run_cli_search(
    search_keyword: str = None,
    right_holder: str = None,
    right_holder_code: str = None,
    max_patents: int = None
):
    """CLI로 특허 검색 실행"""
    print("🔍 CLI 모드로 특허 검색을 시작합니다.")
    print("-" * 50)
    
    try:
        # 기본값 설정
        if search_keyword is None:
            search_keyword = settings.search_keyword
        if right_holder is None:
            right_holder = settings.right_holder
        if right_holder_code is None:
            right_holder_code = settings.right_holder_code
        if max_patents is None:
            max_patents = settings.max_patents
        
        print(f"검색 키워드: {search_keyword}")
        print(f"등록권자: {right_holder}({right_holder_code})")
        print(f"최대 특허 수: {max_patents}")
        print("-" * 50)
        
        # 검색 실행
        patents = patent_processor.search_and_extract_patents(
            search_keyword=search_keyword,
            right_holder=right_holder,
            right_holder_code=right_holder_code,
            max_patents=max_patents
        )
        
        if not patents:
            print("❌ 검색된 특허가 없습니다.")
            return
        
        print(f"✅ {len(patents)}건의 특허를 찾았습니다.")
        
        # 상세 정보 처리
        claims_saved = 0
        pdfs_downloaded = 0
        processed_patents = []
        
        for i, patent_info in enumerate(patents, 1):
            print(f"\n[{i}/{len(patents)}] 처리 중: {patent_info.application_number}")
            print(f"  📄 발명명칭: {patent_info.invention_title}")
            
            detail_info = patent_processor.process_patent_details(
                patent_info=patent_info,
                include_claims=settings.save_claims,
                include_pdf=settings.download_pdfs
            )
            
            processed_patents.append(detail_info)
            
            if detail_info.claims:
                claims_saved += 1
            if detail_info.pdf_url and settings.download_pdfs:
                pdfs_downloaded += 1
        
        # 요약 보고서 생성
        summary_report = patent_processor.create_summary_report(
            patents=processed_patents,
            claims_saved=claims_saved,
            pdfs_downloaded=pdfs_downloaded,
            search_keyword=search_keyword,
            right_holder=right_holder,
            right_holder_code=right_holder_code
        )
        
        # 결과 출력
        print("\n" + "="*60)
        print("✅ 처리 완료!")
        print(f"📊 총 처리된 특허: {len(processed_patents)}건")
        if settings.save_claims:
            print(f"📝 청구항 저장: {claims_saved}건")
        if settings.download_pdfs:
            print(f"📁 PDF 다운로드: {pdfs_downloaded}건")
        print(f"📂 결과 저장 위치: {os.path.abspath(patent_processor.output_dir)}")
        if summary_report:
            print(f"📋 요약 보고서: {summary_report}")
        print("="*60)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description="화장품 특허 검색 시스템",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # API 서버 실행
  python run.py api
  
  # CLI로 기본 설정으로 검색
  python run.py cli
  
  # CLI로 특정 키워드 검색
  python run.py cli --keyword "조성물" --max-patents 10
  
  # CLI로 특정 등록권자 검색
  python run.py cli --right-holder "코스맥스 주식회사" --right-holder-code "120140131250"
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='실행 모드')
    
    # API 서버 모드
    api_parser = subparsers.add_parser('api', help='FastAPI 서버 실행')
    api_parser.add_argument('--host', default=settings.host, help='서버 호스트')
    api_parser.add_argument('--port', type=int, default=settings.port, help='서버 포트')
    api_parser.add_argument('--debug', action='store_true', help='디버그 모드')
    
    # CLI 모드
    cli_parser = subparsers.add_parser('cli', help='CLI 모드로 검색 실행')
    cli_parser.add_argument('--keyword', '-k', help='검색 키워드')
    cli_parser.add_argument('--right-holder', '-r', help='등록권자명')
    cli_parser.add_argument('--right-holder-code', '-c', help='등록권자 코드')
    cli_parser.add_argument('--max-patents', '-m', type=int, help='최대 특허 수')
    
    args = parser.parse_args()
    
    if args.mode == 'api':
        # API 서버 실행
        if args.debug:
            settings.debug = True
        if args.host:
            settings.host = args.host
        if args.port:
            settings.port = args.port
        
        run_api_server()
        
    elif args.mode == 'cli':
        # CLI 모드 실행
        run_cli_search(
            search_keyword=args.keyword,
            right_holder=args.right_holder,
            right_holder_code=args.right_holder_code,
            max_patents=args.max_patents
        )
        
    else:
        # 모드가 지정되지 않은 경우 도움말 표시
        parser.print_help()
        print("\n💡 tip: 'python run.py api' 또는 'python run.py cli'로 실행하세요.")


if __name__ == "__main__":
    main()
