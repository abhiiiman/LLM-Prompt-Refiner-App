import streamlit as st
import requests
import json

# Configure the page
st.set_page_config(
    page_title="LLM Prompt Refiner",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="expanded",
)

# API endpoint configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .refined-prompt-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-top: 1rem;
        color: #000000;
        font-size: 1rem;
        line-height: 1.6;
    }
    .stTextArea textarea {
        font-size: 1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown(
    '<div class="main-header">✨ LLM Prompt Refiner</div>', unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">Transform your prompts into high-quality, model-ready descriptions</div>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    api_url = st.text_input(
        "API Endpoint", value=API_BASE_URL, help="FastAPI backend URL"
    )

    st.divider()

    st.header("ℹ️ About")
    st.markdown(
        """
    This tool refines your prompts for:
    - **Image Generation** (Stable Diffusion 3.5)
    - **Image Editing** (Qwen Image Edit)
    
    Simply enter your prompt, select the app type, and get an optimized version!
    """
    )

    st.divider()

    # Check API health
    if st.button("🔍 Check API Status"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API is healthy!")
            else:
                st.error(f"❌ API returned status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error(
                "❌ Cannot connect to API. Make sure the FastAPI server is running."
            )
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📝 Your Prompt")

with col2:
    app_type = st.selectbox(
        "App Type",
        options=["image_gen", "image_edit"],
        format_func=lambda x: (
            "🖼️ Image Generation" if x == "image_gen" else "✏️ Image Editing"
        ),
        help="Select the type of model you're using",
    )

# Text area for user prompt
user_prompt = st.text_area(
    "Enter your prompt below:",
    height=150,
    placeholder="Example: A beautiful landscape with mountains and a river at sunset...",
    help="Enter the prompt you want to refine",
)

# Refine button
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    refine_button = st.button(
        "✨ Refine Prompt", type="primary", use_container_width=True
    )

# Handle refinement
if refine_button:
    if not user_prompt.strip():
        st.error("⚠️ Please enter a prompt to refine.")
    else:
        with st.spinner("🔄 Refining your prompt..."):
            try:
                # Make API request
                response = requests.post(
                    f"{api_url}/refine",
                    json={"user_prompt": user_prompt, "app_type": app_type},
                    timeout=30,
                )

                if response.status_code == 200:
                    result = response.json()
                    refined_prompt = result.get("refined_prompt", "")

                    # Display refined prompt
                    st.success("✅ Prompt refined successfully!")

                    st.subheader("🎯 Refined Prompt")
                    st.markdown(
                        f'<div class="refined-prompt-box">{refined_prompt}</div>',
                        unsafe_allow_html=True,
                    )

                    # Copy button
                    st.code(refined_prompt, language=None)

                    # Download button
                    st.download_button(
                        label="💾 Download Refined Prompt",
                        data=refined_prompt,
                        file_name="refined_prompt.txt",
                        mime="text/plain",
                    )

                    # Comparison
                    with st.expander("📊 Compare Original vs Refined"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Original Prompt:**")
                            st.info(user_prompt)
                        with col2:
                            st.markdown("**Refined Prompt:**")
                            st.success(refined_prompt)

                elif response.status_code == 400:
                    error_detail = response.json().get("detail", "Invalid request")
                    st.error(f"❌ {error_detail}")
                else:
                    st.error(
                        f"❌ Error: API returned status code {response.status_code}"
                    )

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Cannot connect to the API. Please ensure the FastAPI server is running at "
                    + api_url
                )
                st.info(
                    "💡 Start the server with: `python backend/main.py` or `uvicorn backend.main:app --reload`"
                )
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. Please try again.")
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")

# Footer
# st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        Made with ❤️ by <a href='https://linkedin.com/in/abhiiiman' target='_blank'>AbhiiiMan</a> | 
        <a href='http://localhost:8000/docs' target='_blank'>View API Docs</a>
    </div>
""",
    unsafe_allow_html=True,
)
