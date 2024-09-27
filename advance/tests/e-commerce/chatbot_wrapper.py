import sys
import os
from typing import Any, Dict
sys.path.append('../../')
from chatbot.prompt_parser import initialize_chain

class EcommerceChatbot:
    def __init__(self, options: Dict[str, Any]):
        # The caller may override Provider ID (e.g. when using multiple instances of the same provider)
        self.providerId = options.get('id', 'E-commerce chatbot provider')

        # The config object contains any options passed to the provider in the config file.
        self.config = options.get('config', {})
        
        # Initialize the chatbot (with your chains, models, etc.)
        self.chain = initialize_chain()
        pass

    def get_response(self, user_input):
        return self.chain.invoke({
            "input": user_input,
            "chat_history": {}
        })

    def id(self) -> str:
        return self.providerId
  
    def call_api(self, prompt, *args, **kwargs) -> Dict[str, Any]:
        response = self.get_response(prompt)
        return {
            'output': response['text']
        }
    
def call_api(prompt, *args, **kwargs) -> Dict[str, Any]:
    bot = EcommerceChatbot({
        'config': {},
        'id': 'E-commerce chatbot provider'
    })
    return bot.call_api(prompt)
