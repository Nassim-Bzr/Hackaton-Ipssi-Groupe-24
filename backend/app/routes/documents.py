from fastapi import APIRouter, HTTPException

from app.services.mongo_service import get_all_documents, get_document_by_id

router = APIRouter()


@router.get("/documents")
def list_documents():
    """Retourne la liste de tous les documents traités."""
    documents = get_all_documents()
    return {"documents": documents, "total": len(documents)}


@router.get("/documents/{doc_id}")
def get_document(doc_id: str):
    """Retourne un document par son doc_id."""
    document = get_document_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document introuvable.")
    return document
