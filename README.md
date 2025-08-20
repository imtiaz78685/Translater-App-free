# AI Translator App (English ↔ Urdu)

Streamlit app that translates between English and Urdu using LangChain + Groq.

## 1) Setup
```bash
cd ai-translator-app
pip install -r requirements.txt
cp .env.example .env  # then put your real key in .env
```

Edit `.env` and set:
```
GROQ_API_KEY=gsk_your_real_key_here
```

Get your key from: https://console.groq.com/keys

## 2) Run
```bash
streamlit run app.py
```

## Notes
- Choose model in the sidebar (default: `llama-3.1-8b-instant`).
- Auto-detect tries to detect Urdu vs English. You can force direction too.
- History keeps your last translations during the session.