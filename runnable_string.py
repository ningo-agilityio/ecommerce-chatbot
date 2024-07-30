from typing import Any, Optional

from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableParallel
from langchain_core.runnables import (
    ConfigurableField,
    RunnableConfig,
    RunnableSerializable,
)

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
print(response)
print(type(response))