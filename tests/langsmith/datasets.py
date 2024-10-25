questions = [
  "What is LangChain?", 
  "What is the payment methods?",
  "What are the FAQs about cake products?",
  "What is the information of Strawberry Shortcake?",
  "Can you give me information about Mini Cake with Chocolate?",
  "Can you guide me how to order a Mini Cake?",
  "What is the information about a Black Forest Cake and return policy?"
]

chatbot_datasets = [
  {
    "input": "What is LangChain?",
    "expectation_values": ["LangChain", "framework", "generative ai", "chain", "llm"],
    "output": {
      "answer": "LangChain is a software framework that helps facilitate the integration of large language models (LLMs) into applications, with use cases such as document analysis, chatbots, and code analysis.",
      "expected_steps": ["search_wikipedia"]
    }
  },
  {
    "input": "What is the payment methods?",
    "expectation_values": ["Credit/Debit Card", "PayPal", "Apple Pay", "Google Pay"],
    "output": {
      "answer": "The payment methods can vary depending on the eCommerce platform or store but common options typically include: Credit/Debit Card, Digital Wallets, Bank Transfers, Buy Now, Pay Later, Cash on Delivery (COD)",
      "expected_steps": ["search_on_local_assets"]
    }
  },
  {
    "input": "Tell me about faqs",
    "expectation_values": ["payment methods", "return policy", "shipping"],
    "output": {
      "answer": "What are the shipping options?",
      "expected_steps": ["search_on_local_assets", "search_wikipedia"],
    }
  },
  {
    "input": "What is the information of Strawberry Shortcake?",
    "expectation_values": ["$14.99"],
    "output": {
      "answer": "The Strawberry Shortcake is priced at $14.99 and consists of layers of sponge cake with fresh strawberries and whipped cream.",
      "expected_steps": ["search_sql_data"],
    }
  },
  {
    "input": "Can you give me information about Mini Cake with Chocolate?",
    "expectation_values": ["$10.99", "in stock"],
    "output": {
      "answer": "The Mini Cake with Chocolate is priced at $10.99 and is described simply as a Mini Cake with Chocolate",
      "expected_steps": ["search_sql_data", "search_online_products"],
    }
  },
  {
    "input": "Can you guide me how to order a Mini Cake?",
    "expectation_values": ["Browse", "checkout", "payment method", "confirm"],
    "output": {
      "answer": "To order a Mini Cake, follow these steps: Browse the Options, Select Your Cake, Add to Cart, Review Your Order, Provide Delivery Information, Enter Payment Details, Confirm Your Order",
      "expected_steps": ["search_on_local_assets"],
    }
  },
  {
    "input": "What is the information about a Black Forest Cake and return policy?",
    "expectation_values": ["$18.99", "whipped cream", "cherries", "chocolate"],
    "output": {
      "answer": "Cakes generally have a very limited return window, often allowing returns only on the same day of purchase or if they are in their original condition. It is advisable to check with the specific retailer for their exact return policy regarding cakes.",
      "expected_steps": ["search_sql_data", "search_on_local_assets"],
    }
  },
]