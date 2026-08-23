class ContextCompressor:

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_n: int = 3,
        compressor=None,
    ):
        if compressor is not None:
            self.compressor = compressor
            return

        from langchain_community.cross_encoders import HuggingFaceCrossEncoder
        from langchain_community.document_compressors import CrossEncoderReranker

        model = HuggingFaceCrossEncoder(
            model_name=model_name
        )

        self.compressor = CrossEncoderReranker(
            model=model,
            top_n=top_n,
        )

    def compress(self, query, documents):

        return self.compressor.compress_documents(
            documents,
            query,
        )
