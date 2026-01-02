import os
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()

def generate_tag(text: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    examples = """
    Input: Helloo kids, today we are learning about biology
    Output: Biology class

    Input: The capital city of America is Washington D.C
    Output: Geography class

    Input: We will solve equations involving quadratic functions
    Output: Math class

    Input: Shakespeare wrote many famous plays
    Output: Literature class
    """

    prompt = PromptTemplate(
        input_variables=["sentence"],
        template=(
            "Generate a short 2–3 (3 would be better) word title describing the following text.\n\n"
            f"{examples}\n"
            "Input: {sentence}\n"
            "Output:"
        ),
    )

    llm = ChatOpenAI(
        api_key=api_key,
        model="gpt-4o-mini",
        temperature=0,
    )

    chain = prompt | llm | StrOutputParser()
    return chain.invoke({"sentence": text}).strip()
