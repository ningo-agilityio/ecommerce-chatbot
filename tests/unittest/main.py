import sys

import unittest
sys.path.append('../../')
from app.chatbot.agent_executor import MainAgentChatbot
from datasets import chatbot_datasets

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(), override=True) # read local .env file

class ChatbotTestCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This will run once before all the test methods
        cls.main_agent_chatbot = MainAgentChatbot()

    # def tearDown(self):
    #     # Clean up after each test if necessary
    #     self.agent_executor.memory.clear()

    def expect_response(self, response, dataset):
        for key_word in dataset['expectation_values']:
            self.assertIn(key_word.lower(), response['output'].lower())
        print(response)
    #   intermediate_steps = response["intermediate_steps"]
    #   tool_calls = [action.tool for action, _ in intermediate_steps]
    #   for key_word in dataset['output']['expected_steps']:
    #       self.assertIn(key_word, tool_calls)

    # Test search_wikipedia tools
    # def test_search_wikipedia(self):
    #     """
    #     Question: "What is LangChain?"
    #     Expected output: ["LangChain", "framework", "generative ai", "chain", "llm"]
    #     """
    #     response = run_with_memory(chatbot_datasets[0]['input'], None)
    #     self.expect_response(response, chatbot_datasets[0])
    
    # Test search_on_local_assets tools
    # def test_search_on_local_assets(self):
    #   """
    #   Question: "What is the payment methods?"
    #   Expected output: ["Credit/Debit Card", "PayPal", "Apple Pay", "Google Pay"]
    #   """
    #   response = run_with_memory(chatbot_datasets[1]['input'], None)
      
    #   for key_word in chatbot_datasets[1]['expectation_values']:
    #       self.assertIn(key_word.lower(), response['output'].lower())
      
    #   intermediate_steps = response["intermediate_steps"]
    #   tool_calls = [action.tool for action, _ in intermediate_steps]
    #   for key_word in chatbot_datasets[0]['output']['expected_steps']:
    #       self.assertIn(key_word, tool_calls)

    # Test search_online_products tools
    # def test_search_online_products(self):
    #     """
    #     Question: "Can you give me information about Mini Cake with Chocolate?"
    #     Expected output: ["10.99", "in stock"]
    #     """
    #     response = run_with_memory("Can you give me information about Mini Cake with Chocolate?", None)
    #     self.expect_response(response, chatbot_datasets[2])

          
    # Test search_sql_data tools
    def test_search_sql_data(self):
      """
      Question: "What is the information of Strawberry Shortcake?"
      Expected output: ["14.99"]
      """
      response = self.main_agent_chatbot.run_with_memory("What is the information of Strawberry Shortcake?", None)
      self.expect_response(response, chatbot_datasets[3])

if __name__ == '__main__':
    unittest.main()