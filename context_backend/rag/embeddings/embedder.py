try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    HuggingFaceEmbeddings = None


class EmbeddingModel:

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        global HuggingFaceEmbeddings

        if HuggingFaceEmbeddings is None:
            from langchain_huggingface import HuggingFaceEmbeddings

        self.model = HuggingFaceEmbeddings(
            model_name=model_name
        )

    def get_model(self):
        return self.model
