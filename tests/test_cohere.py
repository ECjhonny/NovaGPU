import unittest
from unittest.mock import patch, MagicMock

from app.rag import embeddings
from app.services import chat


class ProvidersTests(unittest.TestCase):
    @patch("app.rag.embeddings.EMBEDDINGS_PROVIDER", "cohere")
    @patch("app.rag.embeddings.COHERE_API_KEY", "")
    @patch("app.rag.embeddings.GEMINI_API_KEY", "")
    @patch("app.rag.embeddings.VOYAGE_API_KEY", "")
    @patch("app.rag.embeddings.OPENROUTER_API_KEY", "")
    def test_embeddings_missing_keys_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            embeddings.get_embeddings()
        self.assertIn("No hay API Key configurada para embeddings", str(ctx.exception))

    @patch("app.rag.embeddings.EMBEDDINGS_PROVIDER", "voyage")
    @patch("app.rag.embeddings.VOYAGE_API_KEY", "pa-fake-key")
    @patch("app.rag.embeddings.VoyageAIEmbeddings")
    def test_embeddings_voyage_provider(self, mock_voyage):
        mock_instance = MagicMock()
        mock_voyage.return_value = mock_instance
        res = embeddings.get_embeddings()
        self.assertEqual(res, mock_instance)
        mock_voyage.assert_called_once()

    @patch("app.rag.embeddings.EMBEDDINGS_PROVIDER", "openrouter")
    @patch("app.rag.embeddings.OPENROUTER_API_KEY", "sk-or-fake-key")
    @patch("app.rag.embeddings.OpenAIEmbeddings")
    def test_embeddings_openrouter_provider(self, mock_openrouter_embeddings):
        mock_instance = MagicMock()
        mock_openrouter_embeddings.return_value = mock_instance
        res = embeddings.get_embeddings()
        self.assertEqual(res, mock_instance)
        mock_openrouter_embeddings.assert_called_once()

    @patch("app.services.chat.LLM_PROVIDER", "openrouter")
    @patch("app.services.chat.OPENROUTER_API_KEY", "")
    @patch("app.services.chat.COHERE_API_KEY", "")
    @patch("app.services.chat.GEMINI_API_KEY", "")
    @patch("app.services.chat.GROQ_API_KEY", "")
    def test_chat_llm_missing_keys_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            chat._get_all_llms()
        self.assertIn("No se encontró ninguna API Key válida configurada", str(ctx.exception))

    @patch("app.services.chat.LLM_PROVIDER", "openrouter")
    @patch("app.services.chat.OPENROUTER_API_KEY", "sk-or-fake-key")
    @patch("app.services.chat.ChatOpenAI")
    def test_chat_llm_openrouter_provider(self, mock_chat_openai):
        mock_instance = MagicMock()
        mock_chat_openai.return_value = mock_instance
        all_llms = chat._get_all_llms()
        self.assertTrue(len(all_llms) > 0)
        provider_name, instance = all_llms[0]
        self.assertIn("OpenRouter", provider_name)
        self.assertEqual(instance, mock_instance)


if __name__ == "__main__":
    unittest.main()
