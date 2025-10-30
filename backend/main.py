from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.append(str(Path(__file__).parent.parent))
from utils.prompt_refiner import refine_prompt

app = FastAPI(
    title="LLM Prompt Refiner API",
    description="API for refining prompts for image generation and editing",
    version="1.0.0",
)


class PromptRequest(BaseModel):
    user_prompt: str = Field(
        ..., description="The user's raw input prompt", min_length=1
    )
    app_type: Literal["image_gen", "image_edit"] = Field(
        ...,
        description="The type of app - 'image_gen' for image generation or 'image_edit' for image editing",
    )


class PromptResponse(BaseModel):
    refined_prompt: str = Field(..., description="The refined, model-ready prompt")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to LLM Prompt Refiner API",
        "endpoints": {
            "/refine": "POST - Refine a prompt for image generation or editing",
            "/docs": "GET - Interactive API documentation",
            "/health": "GET - Health check endpoint",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/refine", response_model=PromptResponse)
async def refine_prompt_endpoint(request: PromptRequest):
    """
    Refine a user prompt for image generation or editing.

    - **user_prompt**: The raw user input prompt to be refined
    - **app_type**: Either 'image_gen' for Stable Diffusion 3.5 or 'image_edit' for Qwen Image Edit

    Returns the refined prompt optimized for the selected model.
    """
    try:
        refined = refine_prompt(request.user_prompt, request.app_type)

        # Additional safety check
        if not refined or refined.strip() == "":
            raise HTTPException(
                status_code=500,
                detail="The model returned an empty response. Please try again.",
            )

        return PromptResponse(refined_prompt=refined)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while refining the prompt: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
