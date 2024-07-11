from dotenv import load_dotenv
import os

from ecologits import EcoLogits
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

load_dotenv()


def text_to_llm_prompt(onto_description: str) -> list[ChatMessage]:
    """Mistral ChatCompletion prompt for creating an OWL ontology based on the ontology textual description.

    Parameters
    ----------
    onto_description: str
        Text describing the ontology used as context in the prompt.

    Returns
    -------
    list[ChatMessage]
        Prompt with the context in the Mistral ChatCompletion format.
    """
    prompt = [
        ChatMessage(
            role="system",
            content="You are a helpful assistant in building an ontology. You are fluent in the W3C Semantic Web stack and RDF, RDFS, and OWL languages."
        ),
        ChatMessage(
            role="user",
            content=f"Use the given text to construct an OWL ontology in the Turtle format. Use this namespace: https://github.com/wikit-ai/olaf-llm-nlp4kgc2024/o/example#. Return only the turtle file. \n\n# Text:\n{onto_description}"
        )
    ]
    return prompt


def main() -> None:
    """Create OWL ontology from textual description with Mistral 7B model."""

    # with open(os.path.join(os.getenv("DATA_PATH"), "pizza_description.txt"), "r", encoding="utf8") as text_file:
    with open(os.path.join(os.getenv("DATA_PATH"), "defect_detection_description.txt"), "r", encoding="utf8") as text_file:
        onto_description = text_file.read()

    EcoLogits.init()

    client = MistralClient(api_key=os.getenv("MISTRAL_API_KEY"))
    response = client.chat(
        model="open-mistral-7b",
        temperature=0.0,
        messages=text_to_llm_prompt(onto_description)
    )
    llm_output = response.choices[0].message.content

    print(llm_output)

    # with open(os.path.join(os.getenv("RESULTS_PATH"), "llm_text_to_owl/llm_owl_pizza_onto_mistral.ttl"), "w", encoding="utf-8") as text_file:
    with open(os.path.join(os.getenv("RESULTS_PATH"), "llm_text_to_owl/llm_owl_defect_onto_mistral.ttl"), "w", encoding="utf-8") as text_file:
        text_file.write(llm_output)

    print(f"Energy consumption: {response.impacts.energy.value} kWh")
    print(f"GHG emissions: {response.impacts.gwp.value} kgCO2eq")


if __name__ == "__main__":
    main()
