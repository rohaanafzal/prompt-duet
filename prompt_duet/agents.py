from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class Critique(BaseModel):
    score: int = Field(description="Overall prompt quality from 1 to 10")
    strengths: list[str] = Field(description="What the prompt already does well")
    issues: list[str] = Field(description="Specific problems, most important first")
    suggestions: list[str] = Field(description="Concrete changes the refiner should make")


CRITIC_SYSTEM = """You are a strict prompt engineering reviewer.
Evaluate the prompt on clarity, specificity, context, output format, and constraints.
Bracketed placeholders like [target audience] are acceptable and should not be penalized.
Penalize prompts that are bloated or over-constrained.
Be concrete and do not rewrite the prompt yourself.
Only give a 9 or 10 if there is very little left to improve."""


REFINER_SYSTEM = """You are an expert prompt engineer.
Rewrite the prompt so it fixes every issue in the critique while keeping the user's original intent.
Do not invent details the user never gave. Use placeholders like [target audience] instead.
Return ONLY the improved prompt, with no explanation."""


def build_agents(model_name: str, temperature: float = 0.3):
    llm = init_chat_model(model_name, temperature=temperature)

    critic_prompt = ChatPromptTemplate.from_messages([
        ("system", CRITIC_SYSTEM),
        ("human", "Original goal:\n{goal}\n\nPrompt to review:\n{prompt}"),
    ])
    refiner_prompt = ChatPromptTemplate.from_messages([
        ("system", REFINER_SYSTEM),
        ("human", "Original goal:\n{goal}\n\nCurrent prompt:\n{prompt}\n\nCritique:\n{critique}"),
    ])

    critic = critic_prompt | llm.with_structured_output(Critique)
    refiner = refiner_prompt | llm | StrOutputParser()
    return critic, refiner