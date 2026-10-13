from multi_agent_system.config import settings
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from multi_agent_system.agents.tools.document_tools import compare_documents


model = init_chat_model("gpt-5-nano",
                        openai_api_key=settings.openai_api_key.get_secret_value()
                        )

agent = create_agent(
    model=model,
    tools=[compare_documents]
)

result = agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": (
                "Vergleiche die Dokumente der "
                "Rechnungsnummer 2079344."
            ),
        }
    ]
})


print(result["messages"][-1].content)