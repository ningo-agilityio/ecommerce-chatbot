import logging
import sys
from langsmith import Client
from langsmith.schemas import Run, Example
from langsmith.evaluation import evaluate

sys.path.append('../../')
from app.chatbot.agent_executor import MainAgentChatbot
from datasets import chatbot_datasets

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv(), override=True) # read local .env file

client = Client()
main_agent_chatbot = MainAgentChatbot()

def get_inputs(dataset_item):
    return {
        "question": dataset_item["input"]
    }
def get_outputs(dataset_item):
    return {
        "expectation_values": dataset_item["expectation_values"],
        "expected_steps": dataset_item["output"]["expected_steps"]
    }
# Define dataset: these are your test cases

def create_dataset(dataset_name):
  dataset = client.create_dataset(dataset_name, description="Chatbot agent prompts.")
  client.create_examples(
    inputs=[

        get_inputs(x) for x in chatbot_datasets
    ],
    outputs=[
        get_outputs(x) for x in chatbot_datasets
    ],
    dataset_id=dataset.id,
  )
  return dataset

def init_dataset(dataset, name):
    logging.info(dataset)
    # Check if existing dataset
    if dataset is None:
       dataset = create_dataset(name)

def execution(inputs: dict) -> dict:
  response = main_agent_chatbot.run_with_memory(inputs["question"], None)
  # logging.info('====output====')
  # logging.info(response)
  return {"output": response}

# Define evaluators
def must_mention(run: Run, example: Example) -> dict:
  logging.info("======must_mention======")
  logging.info(run.outputs.get("output")['output'])
  response = run.outputs.get("output")['output'] or ""
  expectation_values = example.outputs.get("expectation_values") or []
  score = any(phrase in response.lower() for phrase in expectation_values)
  return {"key":"must_mention", "score": score}

def check_tools_call(run: Run, example: Example) -> dict:
  logging.info("======check_tools_call======")
  logging.info(run.outputs.get("output")["intermediate_steps"])
  prediction = run.outputs.get("output")["intermediate_steps"] or []
  expected_steps = example.outputs.get("expected_steps") or []
  tool_calls = [action.tool for action, _ in prediction]
  score = any(step in expected_steps for step in tool_calls)
  return {"key":"check_tools_call", "score": score}

def evaluate_agent(dataset_name):
    results = evaluate(
      execution, # Your AI system
      data=dataset_name, # The data to predict and grade over
      evaluators=[
          must_mention,
          check_tools_call
      ], # The evaluators to score the results
      experiment_prefix="rap-generator", # A prefix for your experiment names to easily identify them
      metadata={
        "version": "1.0.0",
      },
    )

    print(f"Evaluation Results: {results}")

if __name__ == "__main__":
    dataset_name = "Chatbot agent Dataset"
    dataset = client.list_datasets(dataset_name=dataset_name)
    dataset = init_dataset(dataset, dataset_name)
    evaluate_agent(dataset_name)
