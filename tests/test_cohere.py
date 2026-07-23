import unittest
from unittest.mock import patch, MagicMock

from app.rag import embeddings
from app.services import chat


class CohereProviderTests(unittest.TestCase):
    @patch("app.rag.embeddings.EMBEDDINGS_PROVIDER", "cohere")
    @patch("app.rag.embeddings.COHERE_API_KEY", "")
    @patch("app.rag.embeddings.GEMINI_API_KEY", "")
    def test_embeddings_missing_keys_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            embeddings.get_embeddings()
        self.assertIn("COHERE_API_KEY no está definida", str(ctx.exception))

    @patch("app.rag.embeddings.EMBEDDINGS_PROVIDER", "cohere")
    @patch("app.rag.embeddings.COHERE_API_KEY", "")
    @patch("app.rag.embeddings.GEMINI_API_KEY", "AIzaSyFakeGeminiKey")
    @patch("app.rag.embeddings.GoogleGenerativeAIEmbeddings")
    def test_embeddings_fallback_to_gemini(self, mock_gemini_embeddings):
        mock_instance = MagicMock()
        mock_gemini_embeddings.return_value = mock_instance
        res = embeddings.get_embeddings()
        self.assertEqual(res, mock_instance)
        mock_gemini_embeddings.assert_called_once()

    @patch("app.services.chat.LLM_PROVIDER", "cohere")
    @patch("app.services.chat.COHERE_API_KEY", "")
    @patch("app.services.chat.GEMINI_API_KEY", "")
    @patch("app.services.chat.GROQ_API_KEY", "")
    def test_chat_llm_missing_keys_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            chat._get_llm()
        self.assertIn("COHERE_API_KEY no está definida", str(ctx.exception))

    @patch("app.services.chat.LLM_PROVIDER", "cohere")
    @patch("app.services.chat.COHERE_API_KEY", "")
    @patch("app.services.chat.GEMINI_API_KEY", "AIzaSyFakeGeminiKey")
    @patch("app.services.chat.ChatGoogleGenerativeAI")
    def test_chat_llm_fallback_to_gemini(self, mock_gemini_chat):
        mock_instance = MagicMock()
        mock_gemini_chat.return_value = mock_instance
        res = chat._get_llm()
        self.assertEqual(res, mock_instance)
        mock_gemini_chat.assert_called_once()


if __name__ == "__main__":
    unittest.main()
