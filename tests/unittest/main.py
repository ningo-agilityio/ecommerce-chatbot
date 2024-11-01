import logging
import sys

import unittest
sys.path.append('../../')
from app.chatbot.agent_executor import MainAgentChatbot
from datasets import chatbot_datasets

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(), override=True) # read local .env file

main_agent_chatbot = MainAgentChatbot()

class ChatbotTestCases(unittest.TestCase):
    # def tearDown(self):
    #     # Clean up after each test if necessary
    #     self.main_agent_chatbot.me.clear()

    def expect_response(self, response, dataset):
        logging.info(f"Question: {response['input']}")
        logging.info(f"Output: {response['output']}")
        
        self.assertEqual(any(x.lower() in response['output'].lower() for x in dataset['expectation_values']), True)
        if 'intermediate_steps' in response:
            intermediate_steps = response["intermediate_steps"]
            tool_calls = [action.tool for action, _ in intermediate_steps]
            logging.info(f"Intermediate_steps: {tool_calls}")
            self.assertEqual(any(x in set(tool_calls) for x in dataset['output']['expected_steps']), True)

    # Test search_wikipedia tools: FAIL
    def test_01_search_wikipedia(self):
        """
        Question: "What is LangChain?"
        Expected output: ["LangChain", "framework", "generative ai", "chain", "llm"]
        """
        response = main_agent_chatbot.run_with_memory(chatbot_datasets[0]['input'], None)
        self.expect_response(response, chatbot_datasets[0])
    
    # Test search_on_local_assets tools: PASS
    def test_02_search_on_local_assets(self):
      """
      Question: "What is the payment methods?"
      Expected output: ["Credit/Debit Card", "PayPal", "Apple Pay", "Google Pay"]
      """
      response = main_agent_chatbot.run_with_memory(chatbot_datasets[1]['input'], None)
      self.expect_response(response, chatbot_datasets[1])
          
    # Test search_sql_data tools: PASS
    def test_03_search_sql_data(self):
      """
      Question: "What is the information of Strawberry Shortcake?"
      Expected output: ["14.99"]
      """
      response = main_agent_chatbot.run_with_memory(chatbot_datasets[3]['input'], None)
      self.expect_response(response, chatbot_datasets[3])

     # Test search_online_products tools: FAIL
    def test_04_search_online_products(self):
        """
        Question: "Can you give me information about Mini Cake with Chocolate?"
        Expected output: ["10.99", "in stock"]
        """
        print(chatbot_datasets[2])
        response = main_agent_chatbot.run_with_memory(chatbot_datasets[4]['input'], None)
        self.expect_response(response, chatbot_datasets[4])

if __name__ == '__main__':
    test_order = [
        "test_01_search_wikipedia",
        "test_02_search_on_local_assets",
        "test_03_search_sql_data",
        "test_04_search_online_products"
    ] 
    test_loader = unittest.TestLoader()
    test_loader.sortTestMethodsUsing = lambda x, y: test_order.index(x) - test_order.index(y)
    unittest.main(testLoader=test_loader)