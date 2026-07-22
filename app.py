import fitz  # PyMuPDF
import json
import logging
import os
import streamlit as st

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="PDF Parser",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PDF_Parser")

MAX_FILE_SIZE_MB = 25

def validate_pdf_bytes(file_bytes: bytes, file_name: str) -> tuple[bool, str]:
    """
    Validates file integrity, extension, size, and magic header bytes (%PDF-).
    """
    if not file_name.lower().endswith(".pdf"):
        return False, "File validation error: Uploaded file must have a .pdf extension."

    file_size = len(file_bytes)
    if file_size == 0:
        return False, "File validation error: Uploaded file is empty (0 bytes)."
    
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File validation error: Exceeds maximum allowed size of {MAX_FILE_SIZE_MB} MB."

    # Magic Header Check (%PDF-)
    if not file_bytes.startswith(b"%PDF-"):
        return False, "File validation error: Header mismatch (%PDF- missing). Not a valid PDF document."

    return True, "Valid PDF"


def parse_pdf_stream(file_bytes: bytes, file_name: str) -> str:
    """
    Parses PDF bytes stream, extracts metadata, text, and metrics into JSON.
    """
    is_valid, validation_msg = validate_pdf_bytes(file_bytes, file_name)
    if not is_valid:
        return json.dumps({
            "status": "rejected",
            "error_type": "ValidationError",
            "message": validation_msg
        }, indent=2)

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        
        # Edge Case: Password Protection
        if doc.is_encrypted:
            return json.dumps({
                "status": "error",
                "error_type": "EncryptedPDF",
                "message": "Document is password protected or encrypted. Please unlock it before uploading."
            }, indent=2)

        # Edge Case: 0 Pages
        if len(doc) == 0:
            return json.dumps({
                "status": "error",
                "error_type": "CorruptedPDF",
                "message": "Document contains 0 pages."
            }, indent=2)

        metadata = doc.metadata or {}
        pages_data = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()
            
            pages_data.append({
                "page_number": page_num + 1,
                "character_count": len(text),
                "word_count": len(text.split()),
                "text": text if text else "[EMPTY PAGE OR SCANNED IMAGE WITHOUT OCR]"
            })

        summary_json = {
            "status": "success",
            "document_summary": {
                "file_name": file_name,
                "total_pages": len(doc),
                "is_encrypted": doc.is_encrypted,
                "metadata": {
                    "title": metadata.get("title", "").strip() or None,
                    "author": metadata.get("author", "").strip() or None,
                    "subject": metadata.get("subject", "").strip() or None,
                    "producer": metadata.get("producer", "").strip() or None,
                    "creation_date": metadata.get("creationDate", "").strip() or None
                }
            },
            "pages": pages_data
        }

        doc.close()
        return json.dumps(summary_json, indent=2, ensure_ascii=False)

    except fitz.FileDataError:
        logger.error(f"PyMuPDF failed to parse corrupted stream: {file_name}")
        return json.dumps({
            "status": "error",
            "error_type": "CorruptedFile",
            "message": "Failed to parse file. The PDF file structure appears corrupted."
        }, indent=2)

    except Exception as e:
        logger.error(f"Unhandled exception during PDF parsing: {str(e)}")
        return json.dumps({
            "status": "error",
            "error_type": "InternalError",
            "message": f"An unexpected error occurred: {str(e)}"
        }, indent=2)


# Streamlit UI Header
st.markdown("<h1 style='text-align: center;'>📄 PDF Parser</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>High-performance PDF scraper & structured JSON extractor</p>", unsafe_allow_html=True)
st.divider()

# Grid Layout
col1, col2 = st.columns([1, 1.2], gap="large")

with col1:
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=["pdf"], 
        accept_multiple_files=False
    )
    
    parse_triggered = st.button("Extract & Scrape PDF", type="primary", use_container_width=True)

with col2:
    st.subheader("Parsed JSON Output")
    
    if uploaded_file is not None and (parse_triggered or uploaded_file):
        with st.spinner("Processing PDF..."):
            file_bytes = uploaded_file.getvalue()
            parsed_json = parse_pdf_stream(file_bytes, uploaded_file.name)
            
            # Interactive JSON Viewer
            st.json(parsed_json)
            
            # Download Button for the resulting JSON
            st.download_button(
                label="📥 Download JSON",
                data=parsed_json,
                file_name=f"{os.path.splitext(uploaded_file.name)[0]}_parsed.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("Upload a PDF file to extract structured metadata and page text.")
