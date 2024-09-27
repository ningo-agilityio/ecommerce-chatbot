import json
import re
from langchain_core.exceptions import OutputParserException

# json_data = r'
# {
#     "destination": "faqs",
#     "next_inputs": "Learn this context about faqs, order process, products information, returns and refunds and shipping information\n    Context:\n    [Document(metadata={\'doc_id\': \'ed17204f-f7c5-4bf8-abed-5d1be41c38b9\'}, page_content=\"I\'m sorry, but I am unable to provide the full content from a document as it may be copyrighted. However, if you have a specific question or need help with something, feel free to ask and I\'ll do my best to assist you.\"), Document(metadata={\'doc_id\': \'f6969b01-7a00-4d03-8857-0f2407a9f4c3\'}, page_content=\"I\'m sorry, but I cannot provide the full content of a document as it may be protected by copyright. However, if you provide me with specific details or questions from the document, I would be happy to help with that.\"), Document(metadata={\'doc_id\': \'4d0f0f51-1fac-4a35-906a-090fc3507eda\'}, page_content=\'Unfortunately, I cannot provide the full content of a document as it may be protected by copyright law. However, if you provide me with specific information or questions from the document, I would be happy to help with that.'), Document(metadata={\'doc_id\': \'f3aa1810-8b0b-40c9-a282-39fb50ca8e8e\'}, page_content=\"- Books & Media\\n\\nWelcome to our Books & Media section, where you can find a wide range of books, magazines, and other media products. Whether you\'re looking for the latest bestseller, a classic novel, or a magazine to keep you entertained on your commute, we have something for everyone.\\n\\nOur collection includes fiction, non-fiction, self-help, cookbooks, children\'s books, and much more. We also have a selection of DVDs, CDs, and audiobooks for those who prefer to listen or watch their favorite stories.\\n\\nIf you\'re not sure what you\'re looking for, our knowledgeable staff is always happy to help you find the perfect book or media product. So come on in and browse our shelves, you never know what hidden gem you might discover.\\n\\nHappy reading and happy watching!\")]\n\n    Chat history: [AIMessage(content=\'Hello, I am an e-commerce chatbot. How can I help you?\'), HumanMessage(content=\'tell me about faqs\')]\n\n    Question: tell me about faqs\n    Result:"
# }'
# p = re.compile('(?<!\\\\)\'')
# clean_escape = p.sub('\"', json_str)
# clean_escape = clean_escape.replace('\\"', '').replace("\\'", "'").replace("\"'", '')
# formatted_str = ast.literal_eval(json.dumps(clean_escape))
# formatted_str = f"r\'{formatted_str.replace("'", "\'")}\'"
# formatted_str = "r'{}'".format(formatted_str.replace("'", "\'"))
# formatted_str = ast.literal_eval(json.dumps(html.unescape(clean_escape)))
dummy_response = r'{"overriding_parameters": {"jar_params": ["{\"aggregationType\":\"Type1\",\"startDate\":\"2022-05-10\",\"endDate\":\"2022-05-10\"}"]}}'
# match = re.search(r"""```       # match first occuring triple backticks
#                     (?:json)? # zero or one match of string json in non-capturing group
#                     (.*)```   # greedy match to last triple backticks""", json_data, flags=re.DOTALL|re.VERBOSE)

# # If no match found, assume the entire string is a JSON string
# if match is None:
#     json_str = json_data
# else:
#     # If match found, use the content within the backticks
#     json_str = match.group(1)
# json_str = json_str.strip()
# p = re.compile('(?<!\\\\)\'')
# clean_escape = p.sub('\"', json_str)
# format = f"r\'{clean_escape.replace('\\"', '')}\'"
# print(format)
try:
    loaded_data = json.loads(dummy_response)
    print(loaded_data)
except Exception as e:
    raise OutputParserException(
        f"Parsing parse_json_markdown \n raised following error:\n{dummy_response}"
    )

