from typing import Any, Optional

from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableParallel
from langchain_core.runnables import (
    ConfigurableField,
    RunnableConfig,
    RunnableSerializable,
)

class CustomAgentExecutor(AgentExecutor):
    @property
    def output_keys(self) -> List[str]:
        return ["text"]

    def run(self, input: Any, **kwargs: Any) -> Dict[str, Any]:
        result = super().run(input, **kwargs)
        return {"text": result["output"]}

class AgentLLMChain(LLMChain):
    def __init__(self, agent_executor: AgentExecutor, **kwargs: Any):
        super().__init__(**kwargs)
        self.agent_executor = agent_executor

    def run(self, input: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.agent_executor.run(input, **kwargs)

def _handle_error(error) -> str:
    print("_handle_error")
    return str(error)[:50]

# agent = create_react_agent(first_chain, tools, hub_prompt)
# agent_executor = AgentExecutor(
#     agent=agent,
#     tools=tools,
#     verbose=True,
#     handle_parsing_errors=_handle_error,
# )
# chain = AgentLLMChain(CustomAgentExecutor(agent_executor))

class ListRunnable(RunnableSerializable[Any, list]):
    def invoke(
        self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list:
        return self._call_with_config(self.listify, input, config, **kwargs)

    def listify(self, input: Any) -> list:
        return [input]


class StrRunnable(RunnableSerializable[Any, str]):
    def invoke(
        self, input: Any, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> list:
        return self._call_with_config(self.strify, input, config, **kwargs)

    def strify(self, input: Any) -> str:
        return str(input)

runnable1 = RunnableLambda(lambda x: {"foo": x})

configurable_runnable = ListRunnable().configurable_alternatives(
    ConfigurableField(id="next_step"), default_key="list", string=StrRunnable()
)
chain = runnable1 | configurable_runnable

response = chain.invoke(7, config={"configurable": {"next_step": "string"}})
