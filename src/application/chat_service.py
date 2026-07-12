from langchain_core.messages import HumanMessage

from llm.agent import ChatAgent


class ChatService:
    def __init__(self, agent: ChatAgent):
        self.agent = agent

    async def answer(self, message: str, thread_id: str):

        cleaned_message = message.strip()

        if not cleaned_message:
            raise ValueError("Message must not be empty.")

        messages = [
            HumanMessage(content=cleaned_message),
        ]

        async for chunk in self.agent.stream(messages, thread_id=thread_id):
            yield chunk

    async def resume_tool(
        self,
        thread_id: str,
        interrupt_id: str,
        decisions: list[dict[str, str]],
    ):
        async for chunk in self.agent.resume(
            thread_id=thread_id,
            interrupt_id=interrupt_id,
            decisions=decisions,
        ):
            yield chunk
