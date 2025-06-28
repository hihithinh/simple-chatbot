from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select
import httpx
from bs4 import BeautifulSoup
from datetime import datetime

from app.db.models.data_source import DataSource
from app.db.models.crawled_content import CrawledContent
from app.db.database import get_db, engine
from app.schemas.data_source import DataSourceCreate, DataSourceRead, DataSourceWithContent

router = APIRouter()

@router.post("/", response_model=DataSourceRead)
def create_data_source(
    data_source: DataSourceCreate, 
    session: Session = Depends(get_db)
):
    db_data_source = DataSource.from_orm(data_source)
    session.add(db_data_source)
    session.commit()
    session.refresh(db_data_source)
    return db_data_source

@router.get("/", response_model=List[DataSourceRead])
def read_data_sources(
    skip: int = 0, 
    limit: int = 100, 
    session: Session = Depends(get_db)
):
    data_sources = session.exec(select(DataSource).offset(skip).limit(limit)).all()
    return data_sources

@router.get("/{data_source_id}/", response_model=DataSourceRead)
def read_data_source(
    data_source_id: int, 
    session: Session = Depends(get_db)
):
    data_source = session.get(DataSource, data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return data_source

@router.post("/crawl/", response_model=DataSourceWithContent)
def crawl_url(
    data: dict,
    session: Session = Depends(get_db)
):
    """
    Crawl content from a URL and create a data source and crawled content
    """
    url = data.get("url")
    name = data.get("name")
    description = data.get("description")
    
    if not url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL is required"
        )
    
    try:
        # Make the request to the URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = httpx.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the content div
        content_div = soup.find('div', {'id': 'content'})
        if not content_div:
            # Try to find any main content if specific div not found
            content_div = soup.find('main') or soup.find('article') or soup.find('body')
        
        if not content_div:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not find content in the webpage"
            )
        
        # Extract title
        title_tag = soup.find('title')
        title = title_tag.text if title_tag else url
        
        # Create data source
        data_source = DataSource(
            name=name or title,
            url=url,
            description=description or f"Content crawled from {url}",
            source_type="web"
        )
        session.add(data_source)
        session.commit()
        session.refresh(data_source)
        
        # Create crawled content
        content_html = str(content_div)  # Store HTML content directly
        crawled_content = CrawledContent(
            data_source_id=data_source.id,
            title=title,
            content=content_html,
            url=url
        )
        session.add(crawled_content)
        session.commit()
        session.refresh(crawled_content)
        
        return {
            "data_source": data_source,
            "crawled_content": crawled_content
        }
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error fetching URL: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/{data_source_id}/content/", response_model=DataSourceWithContent)
def get_data_source_with_content(
    data_source_id: int,
    session: Session = Depends(get_db)
):
    """
    Get a data source with its crawled content
    """
    data_source = session.get(DataSource, data_source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")
    
    # Get the most recent crawled content for this data source
    statement = select(CrawledContent).where(
        CrawledContent.data_source_id == data_source_id
    ).order_by(CrawledContent.created_at.desc()).limit(1)
    
    crawled_content = session.exec(statement).first()
    if not crawled_content:
        raise HTTPException(status_code=404, detail="No crawled content found for this data source")
    
    return {
        "data_source": data_source,
        "crawled_content": crawled_content
    }
