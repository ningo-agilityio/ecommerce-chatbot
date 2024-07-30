import json
import re
import langchain
from typing import Any, Dict, Type
from langchain_core.exceptions import OutputParserException

def parse_json_markdown(json_string: str) -> dict:
        # Try to find JSON string within first and last triple backticks
        match = re.search(r"""```       # match first occuring triple backticks
                            (?:json)? # zero or one match of string json in non-capturing group
                            (.*)```   # greedy match to last triple backticks""", json_string, flags=re.DOTALL|re.VERBOSE)

        # If no match found, assume the entire string is a JSON string
        if match is None:
            json_str = json_string
        else:
            # If match found, use the content within the backticks
            json_str = match.group(1)

        # Strip whitespace and newlines from the start and end
        json_str = json_str.strip()
       
        print("after format")
        print(json_str)
        # Parse the JSON string into a Python dictionary while allowing control characters by setting strict to False
        try: 
            return json.loads(json_str)
        except Exception as e:
            raise OutputParserException(
                f"Parsing parse_json_markdown \n raised following error:\n{e}"
            )
        
class CustomizeRouterOutputParser(langchain.schema.BaseOutputParser[Dict[str, str]]):
    """Parser for output of router chain int he multi-prompt chain."""
    # expected_keys = ["destination", "next_inputs"]

    default_destination: str = "DEFAULT"
    next_inputs_type: Type = str
    next_inputs_inner_key: str = "input"

    def parse(self, text: str) -> Dict[str, Any]:
        try:
            parsed = parse_json_markdown(text) ### this line is changed
            if not isinstance(parsed["destination"], str):
                raise ValueError("Expected 'destination' to be a string.")
            if not isinstance(parsed["next_inputs"], self.next_inputs_type):
                raise ValueError(
                    f"Expected 'next_inputs' to be {self.next_inputs_type}."
                )
            parsed["next_inputs"] = {self.next_inputs_inner_key: parsed["next_inputs"]}
            if (
                parsed["destination"].strip().lower()
                == self.default_destination.lower()
            ):
                parsed["destination"] = None
            else:
                parsed["destination"] = parsed["destination"].strip()
            return parsed
        except Exception as e:
            print(f"Parsing text\n{text}\n raised following error:\n{e}")
        