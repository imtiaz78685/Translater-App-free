
import os
import streamlit as st
from dotenv import load_dotenv
from langdetect import detect, DetectorFactory
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

DetectorFactory.seed = 0

load_dotenv()  

st.set_page_config(page_title="English ↔ Urdu Translator", page_icon="🌐", layout="centered")
st.markdown(
    """
    <style>
        .rtl { direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', 'Noto Naskh Arabic', 'Segoe UI', 'Arial', sans-serif; line-height: 1.9; font-size: 1.15rem; }
        .ltr { direction: ltr; text-align: left; line-height: 1.6; font-size: 1.05rem; }
        .muted { opacity: 0.7; }
        .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("English ↔ Urdu Translator")
st.caption("Powered by LangChain + Groq (Gemma/Llama). Type and translate instantly.")
st.markdown("**Model trained by Imtiaz **")

with st.sidebar:
    st.header("Settings")
    model_choice = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "gemma2-9b-it"],
        index=0,
        help="Choose a Groq chat model for translation."
    )
    mode = st.radio("Direction", ["Auto-detect", "English → Urdu", "Urdu → English"], index=0)
    show_prompt = st.checkbox("Show system prompt", value=False)
    keep_history = st.checkbox("Keep translation history", value=True)

    st.markdown("---")
    st.markdown("**API key**")
    if os.environ.get("GROQ_API_KEY"):
        st.success("GROQ_API_KEY found ✅")
    else:
        st.warning("Set GROQ_API_KEY in your environment or .env file.", icon="⚠️")

def get_llm():
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        st.error("GROQ_API_KEY is missing. Add it in your environment or .env file.")
        st.stop()
    return ChatGroq(model=model_choice, groq_api_key=api_key)

SYS_PROMPT_EN2UR = (
    "You are a professional translator. Translate the user's text from English to Urdu.\n"
    "Use natural, conversational Urdu. Preserve technical terms and code snippets.\n"
    "Do not add explanations—only return the translation."
)
SYS_PROMPT_UR2EN = (
    "You are a professional translator. Translate the user's text from Urdu to English.\n"
    "Use natural, fluent English. Preserve technical terms and code snippets.\n"
    "Do not add explanations—only return the translation."
)

def detect_lang(text: str) -> str:
    try:
        lang = detect(text)
        return lang
    except Exception:
        return "unknown"

def translate(text: str, direction: str):
    llm = get_llm()

    if direction == "Auto-detect":
        lang = detect_lang(text)
        if lang.startswith("ur") or lang in {"fa", "ar", "ps"}:
            system = SystemMessage(content=SYS_PROMPT_UR2EN)
            disp_dir = "ltr"
        else:
            system = SystemMessage(content=SYS_PROMPT_EN2UR)
            disp_dir = "rtl"
    elif direction == "English → Urdu":
        system = SystemMessage(content=SYS_PROMPT_EN2UR)
        disp_dir = "rtl"
    else:
        system = SystemMessage(content=SYS_PROMPT_UR2EN)
        disp_dir = "ltr"

    human = HumanMessage(content=text)
    result = llm.invoke([system, human])
    return (result.content or "").strip(), disp_dir, system.content

if "history" not in st.session_state:
    st.session_state.history = []

st.text_area("Input text", key="user_text", height=160, placeholder="Type English or Urdu here…")
cols = st.columns([1,1,1,3])
with cols[0]:
    translate_clicked = st.button("Translate", type="primary", use_container_width=True)
with cols[1]:
    clear_clicked = st.button("Clear", use_container_width=True)
with cols[2]:
    copy_clicked = st.button("Copy Output", use_container_width=True)

if clear_clicked:
    st.session_state.user_text = ""
    st.session_state.pop("last_output", None)
    if not keep_history:
        st.session_state.history = []

output_container = st.empty()

if translate_clicked and st.session_state.user_text.strip():
    with st.spinner("Translating…"):
        out, disp_dir, used_prompt = translate(st.session_state.user_text.strip(), mode)
        st.session_state.last_output = (out, disp_dir, used_prompt)
        if keep_history:
            st.session_state.history.append(
                {"direction": mode, "input": st.session_state.user_text.strip(), "output": out, "dir": disp_dir}
            )

if "last_output" in st.session_state:
    out, disp_dir, used_prompt = st.session_state.last_output
    css_class = "rtl" if disp_dir == "rtl" else "ltr"
    output_container.markdown(f"<div class='{css_class}'>{out}</div>", unsafe_allow_html=True)

    if copy_clicked:
        st.info("Select and copy the text above.", icon="📋")

    if show_prompt:
        st.markdown("**System prompt used:**")
        st.code(used_prompt, language="text")

if st.session_state.history:
    st.markdown("---")
    st.subheader("History")
    for i, item in enumerate(reversed(st.session_state.history[-10:]), start=1):
        css_class = "rtl" if item["dir"] == "rtl" else "ltr"
        st.markdown(f"**{i}. {item['direction']}**", help=item["input"][:120])
        st.markdown(f"<div class='{css_class}'>{item['output']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>—</div>", unsafe_allow_html=True)
