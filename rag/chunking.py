import re
from pathlib import Path
from typing import List, Tuple

# Optional: use tiktoken for accurate token counting; fall back to simple whitespace split if unavailable
try:
    import tiktoken
    _encoding = tiktoken.get_encoding("cl100k_base")
    def _count_tokens(text: str) -> int:
        return len(_encoding.encode(text))
except Exception:
    # simple approximate token count (1 token ~ 4 characters)
    def _count_tokens(text: str) -> int:
        return max(1, len(text) // 4)

def _split_into_sentences(text: str) -> List[str]:
    """Very simple sentence splitter – splits on punctuation followed by whitespace.
    This is sufficient for our short personal docs.
    """
    # Preserve delimiters
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s]

def chunk_text(
    text: str,
    chunk_size: int = 200,
    overlap: int = 50,
) -> List[Tuple[str, int, int]]:
    """Split *text* into token‑based overlapping chunks.

    Returns a list of tuples ``(chunk_text, start_char, end_char)`` where the
    character offsets refer to the original *text* string.

    The algorithm works by first splitting the document into sentences, then
    greedily adding sentences to the current chunk until the token limit is
    reached. When a chunk is yielded, the next chunk starts ``overlap`` tokens
    before the end of the previous chunk (by walking back to the nearest
    sentence boundary).
    """
    sentences = _split_into_sentences(text)
    chunks: List[Tuple[str, int, int]] = []
    current_chunk: List[str] = []
    current_tokens = 0
    start_idx = 0
    char_pointer = 0
    for sent in sentences:
        sent_tokens = _count_tokens(sent)
        if current_tokens + sent_tokens > chunk_size and current_chunk:
            # form chunk
            chunk_str = " ".join(current_chunk)
            end_idx = char_pointer - 1  # last char of previous sentence
            chunks.append((chunk_str, start_idx, end_idx))
            # compute overlap start by walking back tokens
            # simple approach: keep last few sentences that approximate overlap tokens
            overlap_sentences: List[str] = []
            overlap_tokens = 0
            for rev_sent in reversed(current_chunk):
                rev_tokens = _count_tokens(rev_sent)
                if overlap_tokens + rev_tokens > overlap:
                    break
                overlap_sentences.insert(0, rev_sent)
                overlap_tokens += rev_tokens
            current_chunk = overlap_sentences.copy()
            current_tokens = overlap_tokens
            # reset start index to the character position of first overlap sentence
            # Find its position in original text
            start_idx = text.find(current_chunk[0]) if current_chunk else char_pointer
        # add sentence
        current_chunk.append(sent)
        current_tokens += sent_tokens
        char_pointer = text.find(sent, char_pointer) + len(sent)
    # final chunk
    if current_chunk:
        chunk_str = " ".join(current_chunk)
        end_idx = len(text)
        chunks.append((chunk_str, start_idx, end_idx))
    return chunks

if __name__ == "__main__":
    sample = Path(__file__).read_text(encoding="utf-8")
    for c, s, e in chunk_text(sample):
        print(f"Chunk ({s}-{e}) tokens={_count_tokens(c)}\n{c[:100]}...\n")
