import json
import sys

def my_prompt_function(context: dict) -> str:

  provider: dict = context['providers']
  provider_id: str = provider['id']  # ex. openai:gpt-4o or bedrock:anthropic.claude-3-sonnet-20240229-v1:0
  provider_label: str | None = provider.get('label') # exists if set in promptfoo config.

  variables: dict = context['vars'] # access the test case variables

  return (
      f"Describe {variables['topic']} concisely, comparing it to the Python"
      " programming language."
  )

if __name__ == "__main__":
    # If you don't specify a `function_name` in the provider string, it will run the main
    print(my_prompt_function(json.loads(sys.argv[1])))