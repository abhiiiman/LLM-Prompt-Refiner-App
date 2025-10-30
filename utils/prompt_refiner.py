import litellm
import os
from dotenv import load_dotenv

load_dotenv()


def refine_prompt(user_prompt: str) -> str:
    """
    Refines a user-provided prompt for image generation or editing.

    Args:
        user_prompt (str): The user's raw input prompt.

    Returns:
        str: A refined, model-ready prompt optimized for image generation/editing.
    """
    # Define the system instruction for prompt refinement
    system_prompt = (
        "You are an AI prompt refiner specialized in writing high-quality prompts for all cases be it image generation or image editing or in general prompting."
        "Refine the given user prompt to optimize it for high-quality image generation or editing while staying strictly faithful to the user's original intent and vision. "
        "Enhance clarity, add relevant visual details, and improve structure, but never deviate from what the user requested. "
        "Avoid using double hyphenated words like this `--`."
        "Return only the refined prompt with no explanations, introductions, or additional text."
    )

    # Send request to the GPT OSS model hosted via LiteLLM
    try:
        response = litellm.completion(
            model=os.getenv("VLLM_MODEL"),
            api_base=os.getenv("VLLM_HOST_API"),
            temperature=0.7,
            max_tokens=512,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"User Prompt: {user_prompt}",
                },
            ],
        )

        # Extract the refined prompt
        refined_content = response["choices"][0]["message"]["content"]

        # Handle None or empty responses
        if refined_content is None or refined_content.strip() == "":
            raise ValueError(
                "Unable to refine your prompt, double check and try again."
            )

        return refined_content.strip()

    except Exception as e:
        # Re-raise with more context if it's not already a ValueError
        if isinstance(e, ValueError):
            raise
        raise RuntimeError(f"Failed to refine prompt: {str(e)}")


def main():
    # Example usage
    user_prompt = "A beautiful landscape with mountains and a river"
    refined_prompt = refine_prompt(user_prompt)
    print("Refined Prompt:", refined_prompt)


# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        try:
            refined = refine_prompt(user_input)
            print("Refined Prompt:\n", refined)
        except ValueError as e:
            print(e)
