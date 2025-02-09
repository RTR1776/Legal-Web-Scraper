from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime

from app.database import get_db
from app.models import Document, User
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.scraper import run_scraper
from app.embedding import add_document_embedding, semantic_search_documents
from app.fine_tuning import export_dataset
from pydantic import BaseModel

router = APIRouter()

# ---------- Pydantic Schemas ----------

class DocumentOut(BaseModel):
    id: int
    jurisdiction: str
    document_type: str
    title: str
    metadata: dict
    content: str
    source_url: str
    date_scraped: datetime.datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

# ---------- Authentication Endpoints ----------

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# ---------- Scraping Endpoint ----------

@router.post("/scrape")
async def trigger_scraping(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to run scraper")
    new_docs = run_scraper()
    for doc in new_docs:
        existing_doc = db.query(Document).filter(Document.source_url == doc["source_url"]).first()
        if existing_doc:
            existing_doc.content = doc["content"]
            existing_doc.date_scraped = datetime.datetime.utcnow()
        else:
            new_document = Document(
                jurisdiction=doc.get("jurisdiction", ""),
                document_type=doc.get("document_type", ""),
                title=doc.get("title", ""),
                metadata=doc.get("metadata", {}),
                content=doc.get("content", ""),
                source_url=doc.get("source_url", ""),
                date_scraped=datetime.datetime.utcnow()
            )
            db.add(new_document)
            db.flush()
            add_document_embedding(new_document)
    db.commit()
    return {"status": "scraping completed"}

# ---------- Keyword Search Endpoint ----------

@router.get("/search", response_model=List[DocumentOut])
async def search_documents(q: str, jurisdiction: Optional[str] = None, doc_type: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Document).filter(Document.content.ilike(f"%{q}%"))
    if jurisdiction:
        query = query.filter(Document.jurisdiction == jurisdiction)
    if doc_type:
        query = query.filter(Document.document_type == doc_type)
    results = query.all()
    return results

# ---------- Semantic Search Endpoint ----------

@router.get("/semantic_search", response_model=List[DocumentOut])
async def semantic_search(q: str, top_k: int = 5, db: Session = Depends(get_db)):
    doc_ids = semantic_search_documents(q, top_k=top_k)
    results = db.query(Document).filter(Document.id.in_(doc_ids)).all()
    return results

# ---------- Document Retrieval Endpoint ----------

@router.get("/documents/{doc_id}", response_model=DocumentOut)
async def get_document(doc_id: int, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

# ---------- Document Upload Endpoint ----------

@router.post("/documents/upload", response_model=DocumentOut)
async def upload_document(
    title: str = Form(...),
    jurisdiction: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    content = ""
    if file.content_type == "application/pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file.file)
        for page in reader.pages:
            content += page.extract_text() or ""
    else:
        content = (await file.read()).decode("utf-8")
    new_doc = Document(
        jurisdiction=jurisdiction,
        document_type=document_type,
        title=title,
        metadata={},
        content=content,
        source_url="uploaded",
        date_scraped=datetime.datetime.utcnow()
    )
    db.add(new_doc)
    db.commit()
    db.refresh(new_doc)
    add_document_embedding(new_doc)
    return new_doc

# ---------- Admin Export Endpoint for Fine-Tuning ----------

@router.get("/export")
async def export_data(format: str = "jsonl", task: str = "qa", current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    export_file = export_dataset(db, format=format, task=task)
    return {"export_file": export_file}