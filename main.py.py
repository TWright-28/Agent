from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor


load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

parser = PydanticOutputParser(pydantic_object=ResearchResponse)
prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    "You are an expert research assistant that will help generate a research paper. 
                    Answer the user query and use necessary tools to gather information.
                    Wrap the output in this format and provide no other text\n{{format_instructions}}
                    """,
                ),
                    ("placeholder", "{chat_history}"),
                    ("human", "{query}"),
                    ("placeholder", "{agent_scratchpad}"),
                    

            ]
        ).partial(format_instructions=parser.get_format_instructions())

agent = create_tool_calling_agent(
    llm=llm, 
    prompt=prompt,
    tools=[],
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=[],
    verbose=True, #thought process of agent
)   

raw_response = agent_executor.invoke({"query": "Write a brief research paper on intrinsic and extrinsic bugs."})

structured_response = parser.parse(raw_response.get("output")[0]["text"])

print(structured_response.topic)