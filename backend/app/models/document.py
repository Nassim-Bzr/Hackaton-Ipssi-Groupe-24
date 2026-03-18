from typing import Optional, Dict, Any
from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    confidence_score: float
    engine: str
    source_file: str


class DocumentEntities(BaseModel):
    siret: Optional[str] = None
    siren: Optional[str] = None
    montant_ht: Optional[float] = None
    montant_ttc: Optional[float] = None
    tva: Optional[float] = None
    date_emission: Optional[str] = None
    date_expiration: Optional[str] = None
    nom_fournisseur: Optional[str] = None
    nom_client: Optional[str] = None
    iban: Optional[str] = None


class ValidationDetail(BaseModel):
    field: str
    valid: bool
    message: Optional[str] = None


class DocumentRecord(BaseModel):
    doc_id: str
    id: str
    nom: str
    document_type: str
    metadata: DocumentMetadata
    entities: DocumentEntities
    is_valid: bool
    validation_details: Dict[str, Any] = {}


class DocumentResponse(BaseModel):
    doc_id: str
    id: str
    nom: str
    document_type: str
    date_emission: Optional[str] = None
    is_valid: bool
    confidence_score: float
