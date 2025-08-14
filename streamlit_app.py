import os
from dotenv import load_dotenv
import streamlit as st
from openai import AzureOpenAI
import requests
import time
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

# Load environment variables
load_dotenv()

# Read Azure OpenAI settings from environment
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
DEFAULT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
DEFAULT_VIDEO_API_VERSION = os.getenv("AZURE_OPENAI_VIDEO_API_VERSION", "preview")

# If endpoint points to video jobs API, disable chat UI (SDK would fail on that URL)
DISABLE_CHAT = "/video/generations/jobs" in (AZURE_OPENAI_ENDPOINT or "")

# Helper: build jobs URL with a specific api-version
def build_jobs_url_with_version(endpoint: str, api_version: str) -> str:
    if not endpoint:
        return ""
    parsed = urlparse(endpoint)
    path = parsed.path.rstrip("/")
    query = parse_qs(parsed.query)
    query["api-version"] = [api_version]

    if "/video/generations/jobs" in path:
        new_path = path
    else:
        # assume base endpoint; append the jobs path
        new_path = f"{path}/openai/v1/video/generations/jobs" if path else "/openai/v1/video/generations/jobs"

    return urlunparse((parsed.scheme, parsed.netloc, new_path, parsed.params, urlencode(query, doseq=True), parsed.fragment))

# Lazy client (only if chat enabled)
_client = None

def get_client():
    global _client
    if _client is None:
        _client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )
    return _client

# --- UI Config ---
st.set_page_config(page_title="Azure OpenAI Video Generator", page_icon="🎬", layout="wide")

# Chat UI (optional)
if not DISABLE_CHAT:
    # Sidebar: parameters and actions
    with st.sidebar:
        st.header("Settings")
        deployment = st.text_input("Deployment name", value=DEFAULT_DEPLOYMENT, help="Your Azure OpenAI deployment (model) name")
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        top_p = st.slider("Top P", min_value=0.1, max_value=1.0, value=1.0, step=0.05)
        max_tokens = st.number_input("Max tokens", min_value=1, max_value=8192, value=500, step=50)
        keep_last_pairs = st.slider("Keep last N pairs", min_value=2, max_value=50, value=20, step=1, help="Prunes old turns to stay within context limits")

        if st.button("Clear chat", type="secondary"):
            st.session_state.pop("history", None)
            st.session_state.pop("global_context", None)
            st.rerun()

    # Main: title and global context editor
    st.title("💬 Azure OpenAI Chat UI")
    st.caption("Simple, configurable chat interface with streaming and adjustable parameters.")

    with st.expander("Global context (applies to every response)", expanded=True):
        default_ctx = (
            st.session_state.get("global_context")
            or "You are a helpful assistant for a small financial institution. Keep responses concise, cite assumptions, and ask clarifying questions when needed."
        )
        global_context = st.text_area("Context", value=default_ctx, height=140, placeholder="Add audience, tone, constraints, domain guidance, etc.")
        st.session_state["global_context"] = global_context

    # Initialize history (user/assistant turns only)
    if "history" not in st.session_state:
        st.session_state.history = []

    # Helper to build messages with a single system prompt
    def build_messages():
        base_system = "You are a helpful assistant."
        if global_context.strip():
            base_system += f"\n\nContext to follow for every response:\n{global_context.strip()}"

        messages = [{"role": "system", "content": base_system}]
        messages.extend(st.session_state.history)
        return messages

    # Helper to prune history (keeps only user/assistant turns)
    def prune_history(max_pairs: int):
        turns = st.session_state.history
        # Keep the last 2 * max_pairs messages
        st.session_state.history = turns[-(2 * max_pairs):]

    # Display existing chat
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    prompt = st.chat_input("Message the assistant…")

    # Basic validation
    env_ok = all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT])
    if not env_ok:
        st.warning("Missing one or more environment variables: AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT. Set them in your .env file.")

    if prompt is not None and prompt.strip():
        if not env_ok:
            st.stop()
        if not deployment:
            st.error("Please provide a deployment name in Settings.")
            st.stop()

        # Append user message to history
        user_msg = {"role": "user", "content": prompt.strip()}
        st.session_state.history.append(user_msg)
        with st.chat_message("user"):
            st.markdown(user_msg["content"])

        # Prepare and stream assistant response
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_text = ""
            try:
                client = get_client()
                response = client.chat.completions.create(
                    model=deployment,
                    messages=build_messages(),
                    temperature=float(temperature),
                    top_p=float(top_p),
                    max_tokens=int(max_tokens),
                    stream=True,
                )
                for chunk in response:
                    # Each chunk contains a delta with partial content
                    try:
                        delta = chunk.choices[0].delta
                        content = getattr(delta, "content", None)
                    except Exception:
                        content = None
                    if content:
                        full_text += content
                        placeholder.markdown(full_text)
            except Exception as e:
                st.error(f"Error from Azure OpenAI: {e}")
                st.stop()

        # Save assistant message and prune
        st.session_state.history.append({"role": "assistant", "content": full_text})
        prune_history(keep_last_pairs)

        # Rerun to render the updated history cleanly
        st.rerun()
else:
    st.title("🎬 Azure OpenAI Video Generator")
    st.info("Chat is disabled because AZURE_OPENAI_ENDPOINT points to the video jobs API. Use the Video Generator below.")

# =============================
# Video Generator Section
# =============================
st.markdown("---")
st.header("🎬 Video Generator")
st.caption("Generate a single video from your prompt. No data is persisted between sessions.")

# Base endpoint and API version
st.write("Endpoint (from .env):", AZURE_OPENAI_ENDPOINT or "<not set>")
video_api_version = st.text_input("Video API version", value=DEFAULT_VIDEO_API_VERSION, help="Example: 2024-12-01-preview or preview (depends on your region/preview)")

# Show the computed jobs URL for debugging
jobs_url_preview = build_jobs_url_with_version(AZURE_OPENAI_ENDPOINT, video_api_version)
st.write("📍 Jobs URL:", jobs_url_preview or "<will be computed>")

# Video deployment name (e.g., sora)
video_deployment = st.text_input(
    "Video deployment name",
    value=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "sora"),
    help="Azure OpenAI video model deployment (e.g., sora)",
)

# Prompt and parameters
video_prompt = st.text_area(
    "Describe your video",
    height=140,
    placeholder="e.g., A cinematic shot of a neon-lit futuristic city street in the rain, slow pan, dramatic lighting",
)

# Dimensions (multiples of 64, max 1080x1080)
col1, col2 = st.columns(2)
with col1:
    width = st.number_input("Width", min_value=64, max_value=1080, value=1080, step=64)
with col2:
    height = st.number_input("Height", min_value=64, max_value=1080, value=1080, step=64)

duration_s = st.slider("Duration (seconds)", min_value=1, max_value=60, value=5, step=1)

# Helper to build the status URL from the create URL and job_id
def build_status_url(create_url: str, job_id: str) -> str:
    if not create_url:
        return ""
    parsed = urlparse(create_url)
    # Replace trailing /jobs with /jobs/{id}; preserve query
    path = parsed.path
    if path.endswith("/jobs"):
        path = f"{path}/{job_id}"
    elif "/jobs?" in create_url or path.endswith("/jobs/"):
        # Fallback if already has query right after jobs
        path = path.rstrip("/") + f"/{job_id}"
    # Rebuild URL with same query
    new_url = urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, parsed.query, parsed.fragment))
    return new_url

# Start job
col_btn, col_help = st.columns([1, 3])
with col_btn:
    start_video = st.button("Generate Video", type="primary", use_container_width=True)
with col_help:
    st.write("One video at a time. The app will create a job and poll until it completes.")

if start_video:
    jobs_url = build_jobs_url_with_version(AZURE_OPENAI_ENDPOINT, video_api_version)
    if not jobs_url:
        st.error("AZURE_OPENAI_ENDPOINT is missing. Set it to your base resource endpoint or the jobs endpoint.")
    elif not video_deployment:
        st.error("Please provide a video deployment name (e.g., sora).")
    elif not video_prompt.strip():
        st.error("Please enter a prompt for your video.")
    else:
        headers = {
            "api-key": AZURE_OPENAI_API_KEY or "",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Use the exact API schema from your sample
        payload = {
            "model": video_deployment,
            "prompt": video_prompt.strip(),
            "height": str(height),
            "width": str(width), 
            "n_seconds": str(duration_s),
            "n_variants": "1",
        }

        def submit(url, payload):
            return requests.post(url, json=payload, headers=headers, timeout=60)

        try:
            with st.status("Submitting video job…", expanded=False) as status:
                resp = submit(jobs_url, payload)
                if resp.status_code >= 400:
                    st.error(f"Create job failed: {resp.status_code} {resp.text}")
                    st.stop()
                job = resp.json() or {}
                job_id = job.get("id") or job.get("job_id") or job.get("data", {}).get("id")
                if not job_id:
                    st.error(f"Could not read job id from response: {job}")
                    st.stop()
                status.update(label="Job created. Polling for completion…", state="running")

            # Poll for completion
            status_url = build_status_url(jobs_url, job_id)
            start_time = time.time()
            video_url = None
            last_msg = ""
            while True:
                time.sleep(3)
                try:
                    r = requests.get(status_url, headers=headers, timeout=30)
                    content_type = r.headers.get("content-type", "")
                    data = r.json() if content_type.startswith("application/json") else {}
                except Exception as e:
                    last_msg = f"Polling error: {e}"
                    continue

                # Read status/state
                state = data.get("status") or data.get("state") or data.get("job_status")
                
                # Check if job has completed
                if state in {"succeeded", "completed", "done"}:
                    break
                if state in {"failed", "error", "cancelled"}:
                    st.error(f"Job ended with status: {state}. Details: {data}")
                    st.stop()
                # Timeout after 10 minutes
                if time.time() - start_time > 600:
                    st.error("Timed out waiting for the video job to complete.")
                    st.stop()
                with st.spinner("Generating…"):
                    pass

            # Fetch video content using the exact pattern from Azure OpenAI docs
            generations = data.get("generations", [])
            if not generations or not generations[0].get("id"):
                st.error("Job completed but no generation ID was provided.")
                with st.expander("🔍 Debug: Final job response", expanded=True):
                    st.json(data)
                st.stop()
            
            generation_id = generations[0]["id"]
            st.write(f"✅ Video generation succeeded. Generation ID: {generation_id}")
            
            # Build the correct video content URL (from Azure OpenAI sample)
            base_endpoint = AZURE_OPENAI_ENDPOINT.split('/openai')[0] if '/openai' in AZURE_OPENAI_ENDPOINT else AZURE_OPENAI_ENDPOINT
            video_content_url = f"{base_endpoint}/openai/v1/video/generations/{generation_id}/content/video?api-version={video_api_version}"
            
            try:
                st.write(f"📥 Downloading video from: {video_content_url}")
                v = requests.get(video_content_url, headers=headers, timeout=120)
                v.raise_for_status()
                video_bytes = v.content
                st.write(f"✅ Downloaded {len(video_bytes)} bytes")
            except Exception as e:
                st.error(f"Failed to download video: {e}")
                st.write(f"❌ URL attempted: {video_content_url}")
                with st.expander("🔍 Debug: Final job response", expanded=True):
                    st.json(data)
                st.stop()

            st.success("Video generated!")
            st.video(video_bytes)
            st.download_button(
                label="Download MP4",
                data=video_bytes,
                file_name="generated_video.mp4",
                mime="video/mp4",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Unexpected error: {e}")
