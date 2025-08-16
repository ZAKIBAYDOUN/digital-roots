# === Dual Ingest for Green Hill Plans A & B ===
import os, glob, uuid, json, chromadb, logging
from chromadb.utils import embedding_functions


def read_docx(p):
    from docx import Document
    d = Document(p)
    return "\n".join(x.text for x in d.paragraphs)


def read_pdf(p, ocr_lang: str = "eng"):
    """Extract text from a PDF file with graceful fallbacks.

    The previous implementation relied solely on ``pypdf`` which fails for
    image-based PDFs.  This version first attempts to use ``PyMuPDF`` for
    high-quality text extraction and falls back to OCR (``pytesseract``) when
    a page contains no text.  If PyMuPDF is unavailable, it falls back to the
    original ``pypdf`` behaviour.
    """

    try:  # Preferred extraction via PyMuPDF
        import fitz  # type: ignore
        import io
        from PIL import Image
        try:
            import pytesseract
            ocr_available = True
        except Exception:  # pragma: no cover - optional dependency
            pytesseract = None
            ocr_available = False

        doc = fitz.open(p)
        parts = []
        for page in doc:
            txt = page.get_text("text") or ""
            if not txt.strip() and ocr_available:
                try:
                    pix = page.get_pixmap(dpi=200)
                    img = Image.open(io.BytesIO(pix.tobytes()))
                    txt = pytesseract.image_to_string(img, lang=ocr_lang)
                except Exception:
                    txt = ""
            parts.append(txt)
        text = "\n".join(parts)
        if text.strip():
            return text
    except Exception:
        pass  # Fall back to pypdf

    import pypdf  # fallback extractor
    with open(p, "rb") as fh:
        reader = pypdf.PdfReader(fh)
        return "\n".join((pg.extract_text() or "") for pg in reader.pages)


def read_txt(p):
    return open(p, "r", encoding="utf-8", errors="ignore").read()


def extract_file_text(p):
    e = os.path.splitext(p)[1].lower()
    try:
        return (
            read_docx(p)
            if e == ".docx"
            else read_pdf(p)
            if e == ".pdf"
            else read_txt(p)
            if e in (".txt", ".md")
            else ""
        )
    except Exception as err:
        logging.error("Failed to extract %s: %s", p, err)
        raise


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
            t = extract_file_text(fp)
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
