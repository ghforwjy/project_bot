import unittest
from unittest.mock import patch, MagicMock
from backend.core.intent_classifier import get_intent_classifier, Intent
from backend.core.route_handler import get_route_handler

class TestLangChainIntent(unittest.TestCase):
    def test_classify_intent_without_llm(self):
        """测试在没有LLM配置的情况下意图识别应该失败"""
        # 模拟没有OpenAI API密钥的情况
        with patch('backend.core.intent_classifier.os.getenv', side_effect=lambda key, default=None: None if key == 'OPENAI_API_KEY' else default):
            # 当没有API密钥时，创建IntentClassifier实例就应该失败
            with self.assertRaises(Exception):
                get_intent_classifier()
    
    def test_route_invalid_intent(self):
        """测试路由无效意图"""
        # 创建一个无效意图
        invalid_intent = Intent(intent="invalid_intent", confidence=0.9, data={})
        # 创建路由处理器
        route_handler = get_route_handler()
        # 创建一个模拟的数据库会话
        mock_db = MagicMock()
        # 测试路由无效意图，应该返回聊天处理结果
        result = route_handler.route(invalid_intent, mock_db)
        self.assertTrue(result["success"])
        self.assertIn("助手", result["message"])

if __name__ == '__main__':
    unittest.main()
