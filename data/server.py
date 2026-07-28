from fastapi import FastAPI
from sqlalchemy import create_engine, select
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
from sqlalchemy.orm import Session
from typing import Optional
import meilisearch
import os

# We also import the engine from build_db, you don't have to re-create it here
from build_db import Artwork,engine

CHROMA_PATH = os.environ.get("CHROMA_PATH", "./chroma_db")
MEILI_URL = os.environ.get("MEILI_URL", "http://localhost:7700")

app = FastAPI()
model = SentenceTransformer("clip-ViT-B-32")

collection = chromadb.PersistentClient(path=CHROMA_PATH).get_collection("artworks")

# client for meilisearch
client = meilisearch.Client(MEILI_URL)
index = client.index("artworks")
    

class Query(BaseModel):
    query: str
    style: Optional[str] = None
    genre: Optional[str] = None
    artist: Optional[str] = None
    mode: str = "semantic"

K_CONSTANT = 60

N_RESULTS = 20

# HELPER FUNCTIONS FOR SEARCH
def semantic_search(q: Query):
    vec = model.encode([q.query]).tolist()
    where_array = []
    if q.style: where_array.append({"style": q.style})
    if q.genre: where_array.append({"genre": q.genre})
    if q.artist: where_array.append({"artist": q.artist})

    if len(where_array) == 0:
        res = collection.query(query_embeddings=vec, n_results=N_RESULTS)
    elif len(where_array) == 1:
        res = collection.query(query_embeddings=vec, where = where_array[0], n_results=N_RESULTS)
    elif len(where_array) >= 2:
        res = collection.query(query_embeddings=vec, where = {"$and": where_array}, n_results=N_RESULTS)
    return res["metadatas"][0]

def keyword_search(q: Query):
    results = index.search(q.query, {"limit": 20})
    return results["hits"]

# Uses Reciprocal Rank Fusion (RRF)
def hybrid_search(semantic, keyword):
    scores = {}

    for i, res in enumerate(semantic, start=1):
        id = res["id"]
        scores[id] = scores.get(id, 0) + 1 / (K_CONSTANT + i)

    for i, res in enumerate(keyword, start=1):
        id = res["id"]
        scores[id] = scores.get(id, 0) + 1 / (K_CONSTANT + i)

    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top_k_results = []

    # Take the top 10 using SQL 
    with Session(engine) as session:
        for res in scores[:10]:
            id = res[0]
            top_k_results.append(session.get(Artwork, id))
    return top_k_results

# mode toggles between standard semantic search and hybrid search with meilisearch
@app.post("/search")
def search(q: Query):
    # standard semantic search
    if q.mode == "semantic":
        results = semantic_search(q)

    elif q.mode == "keyword":
        results = keyword_search(q)
        
    # hybrid search: semantic + keyword search
    elif q.mode == "hybrid": 
        # semantic search results
        semantic_results = semantic_search(q)
        
        # keyword search results
        keyword_results = keyword_search(q)

        results = hybrid_search(semantic_results, keyword_results)

    return {"results": results}


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

    
    