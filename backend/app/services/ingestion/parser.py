import io
import re
from typing import Any, Dict, List

from pypdf import PdfReader


class PDFParser:
    QUESTION_PATTERNS = [
        re.compile(
            r"^(?:Q(?:uestion)?\.?\s*\d+[\.\:]?|\d+[\.\)]\s+|Problem\s+\d+|Exercise\s+\d+)",
            re.IGNORECASE,
        ),
        re.compile(
            r"\b(?:Find the|Calculate the|Evaluate|Prove that|Show that|Solve for|Determine)\b",
            re.IGNORECASE,
        ),
    ]

    SOLUTION_PATTERNS = [
        re.compile(r"^(?:Solution|Ans(?:wer)?|Proof)[\:\.]?", re.IGNORECASE),
    ]

    @classmethod
    def validate_pdf_bytes(cls, content: bytes) -> bool:
        if len(content) < 10:
            return False
        # PDF magic bytes
        return content.startswith(b"%PDF-")

    @classmethod
    def parse_pdf_pages(cls, content: bytes) -> List[Dict[str, Any]]:
        """
        Extracts raw text per page from PDF bytes.
        """
        stream = io.BytesIO(content)
        reader = PdfReader(stream)
        pages_data = []

        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages_data.append(
                {
                    "page_number": idx + 1,
                    "text": text.strip(),
                }
            )

        return pages_data

    @classmethod
    def chunk_page_content(cls, page_number: int, text: str) -> List[Dict[str, Any]]:
        """
        Structure-aware chunker that divides page text into clean semantic units.
        Classifies chunk kind as 'theory', 'question', or 'solution'.
        """
        if not text:
            return []

        # Split on double newlines or major section indicators
        raw_paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks = []

        for p in raw_paragraphs:
            # Determine kind
            kind = "theory"
            if any(pat.search(p) for pat in cls.SOLUTION_PATTERNS):
                kind = "solution"
            elif any(pat.search(p) for pat in cls.QUESTION_PATTERNS):
                kind = "question"

            # If paragraph is very long, break into sub-chunks of ~500 chars
            if len(p) > 900:
                sentences = re.split(r"(?<=[.!?])\s+", p)
                current_sub = ""
                for s in sentences:
                    if len(current_sub) + len(s) > 600 and current_sub:
                        chunks.append(
                            {
                                "page_number": page_number,
                                "content": current_sub.strip(),
                                "kind": kind,
                            }
                        )
                        current_sub = s
                    else:
                        current_sub = f"{current_sub} {s}".strip()
                if current_sub:
                    chunks.append(
                        {
                            "page_number": page_number,
                            "content": current_sub.strip(),
                            "kind": kind,
                        }
                    )
            else:
                chunks.append(
                    {
                        "page_number": page_number,
                        "content": p,
                        "kind": kind,
                    }
                )

        return chunks


pdf_parser = PDFParser()
