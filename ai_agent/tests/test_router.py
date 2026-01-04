import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from handlers.router import Router

class TestRouter(unittest.IsolatedAsyncioTestCase):
    async def test_route_chat(self):
        gemini_mock = MagicMock()
        gemini_mock.analyze_task = AsyncMock(return_value={"action": "chat", "reasoning": "conversation"})

        router = Router(gemini_mock)
        result = await router.route("Hello")

        self.assertEqual(result["action"], "chat")

    async def test_route_code(self):
        gemini_mock = MagicMock()
        gemini_mock.analyze_task = AsyncMock(return_value={"action": "code", "reasoning": "calc"})

        router = Router(gemini_mock)
        result = await router.route("Calculate pi")

        self.assertEqual(result["action"], "code")

    async def test_route_tool(self):
        gemini_mock = MagicMock()
        gemini_mock.analyze_task = AsyncMock(return_value={"action": "tool", "tool_name": "fpl_news"})

        router = Router(gemini_mock)
        result = await router.route("FPL news")

        self.assertEqual(result["action"], "tool")
        self.assertEqual(result["tool_name"], "fpl_news")

if __name__ == '__main__':
    unittest.main()
