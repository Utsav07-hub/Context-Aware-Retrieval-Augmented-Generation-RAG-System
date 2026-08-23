from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TranscriptChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
    def split(self, snippets: list[dict], video_id: str) -> list[Document]:
        documents = []

        for snippet in snippets:
            document = Document(
                page_content=snippet["text"],
                metadata={
                    "video_id": video_id,
                    "start_time": snippet["start"],
                    "end_time": snippet["end"],
                },
            )

            documents.append(document)

        chunks = self.splitter.split_documents(documents)

        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index
            chunk.metadata["chunk_id"] = f"{video_id}:{index}"

        return chunks
