import chromadb
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import os
from sqlalchemy import create_engine, select
from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

 # Defines what type of database language we're using 
engine = create_engine("sqlite:///artworks.db", echo=True)

class Base(DeclarativeBase):
    pass

class Artwork(Base):
    __tablename__ = "artworks"
    id: Mapped[int] = mapped_column(primary_key=True)
    artist: Mapped[str]
    genre: Mapped[str]
    style: Mapped[str]
    path: Mapped[str]

def populate():
    # ----------------CHROMADB----------------
    model = SentenceTransformer("clip-ViT-B-32")

    ds = load_dataset("huggan/wikiart", split="train", streaming=True)

    rows = list(ds.take(500))
    feats = ds.features

    os.makedirs("images", exist_ok=True)
    paths=[]

    for i, r in enumerate(rows):
        p = f"images/{i}.jpg"; r["image"].save(p); paths.append(p)

    client = chromadb.PersistentClient(path='./chromadb')
    collection = client.get_or_create_collection("artworks")

    collection.upsert(
        ids=[str(i) for i in range(len(rows))],
        embeddings = model.encode([r["image"] for r in rows]).tolist(),
        metadatas=[{
            "artist": feats["artist"].int2str(r["artist"]),
            "genre": feats["genre"].int2str(r["genre"]),
            "style": feats["style"].int2str(r["style"]),
            "path": paths[i]
        } for i, r in enumerate(rows)]
    )

    q = model.encode(["a story seascape in dark blues"]).tolist()
    res = collection.query(query_embeddings=q, n_results=5)

    for m in res["metadatas"][0]:
        print(m["artist"], "-", m["style"], "->", m["path"])

    # -------------SQLALCHEMY--------------

    # Create the table
    Base.metadata.create_all(engine)

    # load the rows for the images
    ds = load_dataset("huggan/wikiart", split="train", streaming=True)

    rows = list(ds.take(500))
    feats = ds.features

    # Open a session to add all the images as rows to the database
    with Session(engine) as session:
        session.add_all([Artwork(id=i, artist=feats["artist"].int2str(r["artist"]),
                                genre=feats["genre"].int2str(r["genre"]),
                                style=feats["style"].int2str(r["style"]),
                                path=f"images/{i}.jpg") for i,r in enumerate(rows)])
        # You need to commit at the end of the session for the changes to happen
        session.commit()

if __name__ == "__main__":
    populate()