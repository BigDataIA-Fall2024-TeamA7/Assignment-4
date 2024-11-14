# routers.py
from fastapi import APIRouter, HTTPException
from models import DocumentResponse, ArxivResult, WebSearchResult
from service import get_available_documents_from_gcs, fetch_arxiv, web_search

router = APIRouter()


@router.get("/documents", response_model=DocumentResponse)
async def select_documents():
    """Fetch available documents from GCS."""
    try:
        # Call the tool with invoke, passing an empty dictionary as `tool_input`
        documents = get_available_documents_from_gcs.invoke({})
        if documents is None:
            raise HTTPException(status_code=500, detail="Error fetching documents from GCS.")
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found in GCS.")
        return {"available_documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arxiv_search", response_model=list[ArxivResult])
async def arxiv_search(query: str):
    """Search for ArXiv papers based on a query."""
    results = fetch_arxiv(query)
    if not results or isinstance(results, str):
        raise HTTPException(status_code=500, detail="Error fetching Arxiv results")
    return results

@router.get("/web_search", response_model=list[WebSearchResult])
async def perform_web_search(query: str):
    """Perform a web search using SerpAPI."""
    results = web_search(query)
    if not results:
        raise HTTPException(status_code=500, detail="No results found")
    return results
