from fastapi import FastAPI
from sqlalchemy import create_engine, select
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from sqlalchemy.orm import Session
from typing import Optional

# We also import the engine from build_db, you don't have to re-create it here
from build_db import Artwork,engine


app = FastAPI()
model = SentenceTransformer("clip-ViT-B-32")

collection = chromadb.PersistentClient(path='./chromadb').get_collection("artworks")

class Query(BaseModel):
    query: str
    style: Optional[str] = None

@app.post("/search")
def search(q: Query):
    vec = model.encode([q.query]).tolist()
    where={"style": q.style} if q.style else None
    res = collection.query(query_embeddings=vec, where=where, n_results=5)
    return {"results": res["metadatas"][0]}

# --------------GET ENDPOINTS---------------

# The purpose of these GET endpoints is to return the possible field names
# These will be used for dropdown menus on the frontend later
@app.get("/genres")
def genres():
    with Session(engine) as session:
        return session.scalars(select(Artwork.genre).distinct()).all()

@app.get("/styles")
def styles():
    with Session(engine) as session:
        return session.scalars(select(Artwork.style).distinct()).all()

@app.get("/artists")
def artists():
    with Session(engine) as session:
        return session.scalars(select(Artwork.artist).distinct()).all()

    
    