# === Dual Ingest for Green Hill Plans A & B ===
import os, glob, uuid, json, chromadb
from chromadb.utils import embedding_functions


def read_docx(p):
    from docx import Document
    d = Document(p)
    return "\n".join(x.text for x in d.paragraphs)


def read_pdf(p):
    import pypdf
    r = pypdf.PdfReader(open(p, "rb"))
    return "\n".join((pg.extract_text() or "") for pg in r.pages)


def read_txt(p):
    return open(p, "r", encoding="utf-8", errors="ignore").read()


def extract(p):
    e = os.path.splitext(p)[1].lower()
    return read_docx(p) if e == ".docx" else read_pdf(p) if e == ".pdf" else read_txt(p) if e in (".txt", ".md") else ""


def ingest(plan_dir, store_dir, collection, model="text-embedding-3-small"):
    api = os.getenv("OPENAI_API_KEY")
    assert api, "OPENAI_API_KEY missing"
    pats = ("**/*.docx", "**/*.pdf", "**/*.txt", "**/*.md")
    files = [f for pat in pats for f in glob.glob(os.path.join(plan_dir, pat), recursive=True) if os.path.isfile(f)]
    assert files, f"No documents found under {plan_dir}"

    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except Exception:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    chunks, metas = [], []
    for fp in files:
        try:
            t = extract(fp)
        except Exception as e:
            print("WARN skip", fp, ":", e)
            continue
        if t and len(t.strip()) >= 100:
            for i, ch in enumerate(splitter.split_text(t)):
                ch = ch.strip()
                if ch:
                    chunks.append(ch)
                    metas.append({"file": os.path.basename(fp), "chunk_index": i})
    assert chunks, "No chunks produced"

    client = chromadb.PersistentClient(path=store_dir)
    ef = embedding_functions.OpenAIEmbeddingFunction(api_key=api, model_name=model)

    embeds = []
    B = 64
    for i in range(0, len(chunks), B):
        embeds.extend(ef(chunks[i : i + B]))

    col = client.get_or_create_collection(name=collection, metadata={"hnsw:space": "cosine"})
    ids = [f"{collection}-{i}-{uuid.uuid4().hex[:8]}" for i in range(len(chunks))]
    for i in range(0, len(chunks), B):
        col.add(
            documents=chunks[i : i + B],
            metadatas=metas[i : i + B],
            ids=ids[i : i + B],
            embeddings=embeds[i : i + B],
        )
    return {"path": store_dir, "collection": collection, "count": col.count()}


def main():
    pa, sa, pb, sb = os.environ["PLAN_A"], os.environ["STORE_A"], os.environ["PLAN_B"], os.environ["STORE_B"]
    out = [ingest(pa, sa, "gh_plan_A"), ingest(pb, sb, "gh_plan_B")]
    print("✅ Dual Ingest Complete")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
