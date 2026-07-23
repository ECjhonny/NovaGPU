import unittest
from unittest.mock import patch

try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

from app.rag import vectorstore


class VectorStoreFlowTests(unittest.TestCase):
    def test_index_documents_handles_embedding_failures(self):
        fake_doc = Document(page_content="demo", metadata={"source": "test"})

        class FakeVectorStore:
            def add_documents(self, documents):
                raise RuntimeError("simulated embedding failure")

        with patch.object(vectorstore, "get_vectorstore", return_value=FakeVectorStore()):
            with self.assertRaises(RuntimeError):
                vectorstore.index_documents([fake_doc])


if __name__ == "__main__":
    unittest.main()
