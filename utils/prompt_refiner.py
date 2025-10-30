import litellm
import os
from dotenv import load_dotenv

load_dotenv()


def refine_prompt(user_prompt: str, app_type: str) -> str:
    """
    Refines a user-provided prompt for either image generation or image editing.

    Args:
        user_prompt (str): The user's raw input prompt.
        app_type (str): The type of app - "image_gen" or "image_edit".

    Returns:
        str: A refined, model-ready prompt optimized for Stable Diffusion 3.5 (image_gen)
             or Qwen Image Edit model (image_edit).
    """
    if app_type not in ["image_gen", "image_edit"]:
        raise ValueError("Invalid app_type. Choose 'image_gen' or 'image_edit'.")

    # Define the system instruction for prompt refinement
    system_prompt = (
        "You are an AI prompt refiner. Refine the given user prompt to make it optimal for "
        "high-quality image generation with Stable Diffusion 3.5 large if app_type=image_gen, "
        "or for precise, realistic image editing using Qwen Image Edit if app_type=image_edit. "
        "Do not include any filler words, explanations, or introductions — strictly return only the refined prompt."
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
                    "content": f"App Type: {app_type}\nUser Prompt: {user_prompt}",
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
    app_type = "image_gen"
    refined_prompt = refine_prompt(user_prompt, app_type)
    print("Refined Prompt:", refined_prompt)


# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("Enter your prompt (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        app_type_input = input("Enter app type ('image_gen' or 'image_edit'): ")
        try:
            refined = refine_prompt(user_input, app_type_input)
            print("Refined Prompt:\n", refined)
        except ValueError as e:
            print(e)
