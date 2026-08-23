from langchain_core.prompts import ChatPromptTemplate


class RAGPrompt:

    def __init__(self):

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
You answer questions about a YouTube lecture.
Use only the supplied lecture context.
Do not invent information or guess.
If the answer is not supported by the context,
say that the information is not available in the provided lecture.
When useful, cite source numbers and timestamps from the context.
Distinguish uncertainty clearly.

Context:

{context}
"""
                ),
                (
                    "human",
                    "{question}"
                ),
            ]
        )

    def get_prompt(self):

        return self.prompt
