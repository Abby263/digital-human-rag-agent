import ollama
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import json

from . import config

class LLMFactory:
    """A factory for creating and interacting with the LLM."""
    
    def __init__(self):
        """Initializes the LLMFactory with the specified model."""
        self.model_name = config.LLM_MODEL_ID
        self.llm = Ollama(model=self.model_name, format="json")

    def get_image_prompt(self, character_description: str) -> str:
        """
        Generates a detailed image prompt from a brief description.
        
        Args:
            character_description (str): A brief description of the character.
        
        Returns:
            str: A detailed prompt for the image generation model.
        """
        prompt_template = PromptTemplate.from_template(config.IMAGE_PROMPT_TEMPLATE)
        
        chain = prompt_template | self.llm
        
        detailed_instructions = (
            "Create a detailed, realistic, photorealistic, 4k, passport-style photograph of the following character. "
            "The image MUST be a clear, front-facing headshot with a neutral expression and a simple, plain background. "
            "Ensure the full face is visible without any obstructions."
        )
        
        response_str = chain.invoke({
            "character_description": character_description,
            "detailed_instructions": detailed_instructions
        })
        
        try:
            response_json = json.loads(str(response_str))
            prompt = response_json.get("prompt", "")
            if not prompt:
                raise ValueError("LLM returned empty prompt")
            return prompt
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: LLM did not return valid JSON prompt. Error: {e}. Using raw output as fallback.")
            return str(response_str).strip().replace("\n", " ").replace("```", "")


if __name__ == '__main__':
    # Example usage
    llm_factory = LLMFactory()
    description = "A wise, old wizard with a long white beard and a pointed hat."
    prompt = llm_factory.get_image_prompt(description)
    print(f"Generated Prompt: {prompt}") 