from typing import List, Optional, Dict
from datetime import datetime
import httpx
import xml.etree.ElementTree as ET


ARXIV_API_URL = "https://export.arxiv.org/api/query"

# 한 번 검색에 paper 10개
async def fetch_arxiv_results(
    query: str,
    page: int = 1,
    page_size: int = 10,
    sort_by: Optional[str] = "relevance",
    sort_order: Optional[str] = "descending") -> List[Dict]:
    
    params = {
        "search_query": f"all:{query}",
        "start": (page - 1)* page_size,
        "max_results": page_size,
        "sortBy": sort_by,
        "sortOrder": sort_order
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(ARXIV_API_URL, params=params)
        response.raise_for_status()
    
    root = ET.fromstring(response.text)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = entry.find("atom:title", ns).text.strip()
        authors = [author.find("atom:name", ns).text for author in entry.findall("atom:author", ns)]
        summary = entry.find("atom:summary", ns).text.strip()
        link = entry.find("atom:id", ns).text
        
        published_str = entry.find("atom:published", ns).text
        published = datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ") # %Y-%m-%dT%H:%M:%SZ는 arxivAPI 날짜 문자열 포맷
        updated_str = entry.find("atom:updated", ns).text
        updated = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ")
        categories = [cat.attrib['term'] for cat in entry.findall("atom:category", ns)]
        doi_elem = entry.find("atom:doi", ns)
        doi = doi_elem.text if doi_elem is not None else None # 해당 논문이 정식으로 출판되지 않으면 doi 없음
        arxiv_id = entry.find("atom:id", ns).text.split("/")[-1].split("v")[0]# arxiv 전용 논문 index(신버전 : http://arxiv.org/abs/2101.00001v3, 구버전 : hep-th/9901001)
        papers.append({
            "title": title,
            "authors": authors,
            "summary": summary,
            "link": link,
            "published": published,
            "publish_updated": updated,
            "categories": categories,
            "doi": doi,
            "arxiv_id": arxiv_id
        })
        
    return papers