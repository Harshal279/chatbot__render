import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bigin CRM Assistant",
    page_icon="🤖",
    layout="centered"
)

# ─── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Title ── */
.chat-title {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 0.15rem;
    letter-spacing: -0.5px;
}
.chat-subtitle {
    text-align: center;
    font-size: 0.85rem;
    color: #64748b;
    margin-bottom: 1.8rem;
}

/* ── Bubbles ── */
.msg-row-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.55rem 0;
    animation: pop .25s ease;
}
.msg-row-bot {
    display: flex;
    justify-content: flex-start;
    align-items: flex-end;
    gap: 0.55rem;
    margin: 0.55rem 0;
    animation: pop .25s ease;
}
@keyframes pop {
    from { opacity:0; transform:translateY(8px); }
    to   { opacity:1; transform:translateY(0); }
}
.bubble-user {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: #fff;
    padding: .7rem 1.1rem;
    border-radius: 1.2rem 1.2rem .25rem 1.2rem;
    max-width: 72%;
    font-size: .93rem;
    line-height: 1.55;
    box-shadow: 0 4px 18px rgba(99,102,241,.35);
    white-space: pre-wrap;
}
.bubble-bot {
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(255,255,255,.12);
    color: #e2e8f0;
    padding: .7rem 1.1rem;
    border-radius: 1.2rem 1.2rem 1.2rem .25rem;
    max-width: 72%;
    font-size: .93rem;
    line-height: 1.55;
    backdrop-filter: blur(12px);
    white-space: pre-wrap;
}
.avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: linear-gradient(135deg,#6366f1,#a855f7);
    display:flex; align-items:center; justify-content:center;
    font-size:.9rem; flex-shrink:0;
}

/* ── Input / Form ── */
.stTextInput>div>div>input {
    background: rgba(255,255,255,.06) !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: .8rem !important;
    color: #e2e8f0 !important;
    font-size: .93rem !important;
    padding: .7rem 1rem !important;
}
.stTextInput>div>div>input:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,.25) !important;
}
.stTextInput>div>div>input::placeholder { color:#475569 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: rgba(15,12,41,.95) !important;
    border-right: 1px solid rgba(255,255,255,.07);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stMarkdown h2 { font-size:1.1rem; margin-bottom:.3rem; }

/* ── Buttons ── */
.stButton>button, [data-testid="stFormSubmitButton"]>button {
    background: linear-gradient(135deg,#6366f1,#4f46e5) !important;
    color: #fff !important;
    border: none !important;
    border-radius: .65rem !important;
    font-weight: 500 !important;
    transition: all .2s !important;
}
.stButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(99,102,241,.45) !important;
}

/* ── Selectbox ── */
.stSelectbox>div>div {
    background: rgba(255,255,255,.06) !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: .65rem !important;
    color: #e2e8f0 !important;
}

/* ── Divider ── */
hr { border-color: rgba(255,255,255,.08) !important; }

/* ── Info box for download ── */
.download-box {
    background: rgba(99,102,241,.12);
    border: 1px solid rgba(99,102,241,.35);
    border-radius: 1rem;
    padding: 1.1rem 1.4rem;
    margin: 1rem 0;
    color: #c7d2fe;
    font-size: .9rem;
}
</style>
""", unsafe_allow_html=True)

# ─── System Prompt ────────────────────────────────────────────────────────────
CRM_SYSTEM_PROMPT = """You are Aria, a warm and intelligent CRM consultant at a Zoho & Bigin CRM implementation company.

## Your personality
- Friendly, warm, professional — like a knowledgeable friend, never a cold form.
- Never say "Phase 1", "Step 3 of 21", or anything that sounds robotic.
- Use natural language, react warmly to answers ("Great!", "Got it!", "That's helpful!").
- If the user asks an off-topic question, answer it helpfully, then return to where you left off.
- If the user volunteers extra information, acknowledge it and use it later.

---

## STEP 0 — Always do this first on every new conversation

Greet the user warmly, introduce yourself as Aria, and ask them to pick one of the following:

**1. Generate a CRM Quotation** — I'll guide you through a quick discovery chat to build your Bigin CRM proposal.
**2. Learn about Zoho & its Products** — I'll explain Zoho's product ecosystem and help you figure out the right tools for your business.

Wait for their answer before doing anything else.

---

## MODE A — CRM Quotation Discovery (STRICT ONE-QUESTION-PER-TURN)

⚠️ CRITICAL RULE: Ask **exactly ONE question per message**. Never combine two questions in the same message. Wait for the user's answer, then ask the next question. Follow this exact order:

**Q1.** "What's the name of the company we're preparing this proposal for?"

**Q2.** (After getting company name) "Great! Who's the main point of contact there? I'd love their name and designation — for example, 'Mr. Rajesh Sharma, Sales Head'."

**Q3.** "What does [Company] primarily do? I'm talking about the core business — for example, a chai franchise chain, a financial advisory firm, real estate, etc."

**Q4.** "And who are [Company]'s main target customers? For example, individual consumers, businesses, franchise owners, high-net-worth clients?"

**Q5.** "What does your current sales process look like? Walk me through it — from when a lead comes in to when a deal is closed."

**Q6.** "What tools or systems are you using right now to manage leads and customer data? Things like Excel, Google Sheets, WhatsApp groups, or maybe an old CRM?"

**Q7.** "How many people in total will be using Bigin? Just a rough breakdown works — something like: Sales/BD team, Managers, Support staff, and any others."

**Q8.** "What's the biggest challenge your team faces today when it comes to managing leads and sales? Things like lead leakage, no follow-up tracking, manual reporting — anything that's a real pain point."

*(After Q8, give a short warm summary: "Got it! So [Company] is in [industry], targeting [customers], with [X] users. The main pain points are [list]. Does that sound right?")*

**Q9.** "Now let's talk about your CRM setup. Which modules do you think will need the most customization? For example: Contacts, Companies, Deals, Products, Tasks — or maybe something else?"

**Q10.** "Are there any special custom fields you'll need? For example, things like a Franchise Code, Loan Type, EMI Details, or Source of Lead — anything specific to your business?"

**Q11.** "How many separate sales pipelines do you need? For example, one for Retail, one for Franchise, one for Corporate — or maybe just one?"

**Q12.** (For each pipeline, one at a time) "What are the stages in [Pipeline name], in order? For example: New → Qualified → Proposal Sent → Negotiation → Closed Won."
*(Repeat Q12 for each pipeline the user mentioned. Suggest stage examples based on their industry from Q3.)*

*(After all pipelines: "Here's what I have for your pipelines: [list]. Does that look right?")*

**Q13.** "Where do your leads come from today? List as many as you like — Facebook Ads, Instagram, LinkedIn, Google Ads, IndiaMART, TradeIndia, your website, WhatsApp, walk-ins, referrals, anything else?"

**Q14.** "Would you want WhatsApp Business API integrated with Bigin, so your team can chat with leads directly from inside the CRM?"

**Q15.** "Any other integrations you have in mind? For instance, Zoho Books for accounting, Google Sheets, Zoho Inventory, or anything else?"

**Q16.** "Should leads be automatically assigned to specific team members based on criteria like city, product, or lead source?"

**Q17.** "What kinds of automations would be useful for your team? For example: automatically creating a task when a deal moves to a new stage, sending SMS or email reminders, getting notified when a high-value deal comes in, or automated follow-up sequences?"

**Q18.** "Are there any specific alert rules you need? For example, 'If a deal value goes above ₹5 lakhs, notify the owner immediately' — that kind of thing?"

**Q19.** "Which reports matter most to you? For example: daily activity report, lead source analysis, user-wise performance, pipeline health, conversion ratios, end-of-day summary — or something custom?"

*(Based on pain points from Q8, suggest the most relevant reports.)*

**Q20.** "For training, roughly how many hours would your sales team need? And separately, your admin team? Would the owners or senior management want a session too?"

**Q21.** "After the CRM goes live, how many months of hands-on support would you want from our team — 1 month, 3 months, 6 months, or 12 months?"

**Q22.** "Should we set up a WhatsApp group for daily coordination between your team and ours?"

**Q23.** "Do you have existing customer data you'd want to import into Bigin? Just basic contacts like name/phone/email, or full historical data including past deals and notes?"

**Q24.** "Last one! Who will be the main person on your side coordinating with us during setup? Ideally someone who's tech-savvy — I'll need their name and mobile number."

---

**After Q24:** Output a complete, clean, well-formatted summary of everything collected. Start it exactly with:
`📋 **Here's everything I've gathered so far:**`
Then organize it clearly by area (Company Info, CRM Setup, Pipelines, etc.).
End with: "Does everything look correct? Anything you'd like to add or change?"

---

## MODE B — Zoho Product Information

Become a knowledgeable Zoho product advisor. Help users understand the Zoho ecosystem:

- **Bigin by Zoho CRM** — pipeline-centric CRM for small businesses
- **Zoho CRM** — full-featured CRM for mid/large teams
- **Zoho One** — all-in-one business OS (45+ apps)
- **Zoho Books** — accounting & invoicing
- **Zoho Inventory** — inventory & order management
- **Zoho Campaigns** — email marketing
- **Zoho Desk** — customer support helpdesk
- **Zoho Analytics** — BI & reporting
- **Zoho People** — HR management
- **Zoho Projects** — project management
- **Zoho Sign** — digital signatures
- **Zoho Flow** — workflow automation between apps
- **Zoho SalesIQ** — live chat & visitor tracking

Ask about their industry, team size, and pain points to recommend the right Zoho stack. Answer any specific product questions naturally. If they want a quotation, smoothly switch to Mode A.
"""

# ─── Session State ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GROQ_API_KEY", "")
if "model" not in st.session_state:
    st.session_state.model = "llama-3.3-70b-versatile"
if "greeted" not in st.session_state:
    st.session_state.greeted = False

# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    st.markdown("### 🔑 Groq API Key")
    api_key_input = st.text_input(
        "API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
        help="Free at console.groq.com"
    )
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        st.session_state.greeted = False  # reset so greeting streams again

    if not st.session_state.api_key:
        st.warning("⚠️ Add your Groq API key to start")
        st.markdown("[Get free key →](https://console.groq.com)", unsafe_allow_html=False)

    st.markdown("---")
    st.markdown("### 🧠 Model")
    model_options = {
        "Llama 3.3 70B (Best)": "llama-3.3-70b-versatile",
        "Llama 3.1 8B (Fastest)": "llama-3.1-8b-instant",
        "Mixtral 8x7B": "mixtral-8x7b-32768",
        "Gemma 2 9B": "gemma2-9b-it",
    }
    chosen = st.selectbox("Model", list(model_options.keys()), index=0, label_visibility="collapsed")
    st.session_state.model = model_options[chosen]

    st.markdown("---")
    st.markdown(f"**💬 Messages:** {len(st.session_state.messages)}")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.greeted = False
        st.rerun()

    st.markdown("---")
    st.markdown("<small style='color:#475569'>Aria · Bigin CRM Consultant · Powered by Groq</small>",
                unsafe_allow_html=True)

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("<div class='chat-title'>🤖 Aria — CRM Consultant</div>", unsafe_allow_html=True)
st.markdown("<div class='chat-subtitle'>Your AI assistant for Bigin CRM proposal discovery</div>",
            unsafe_allow_html=True)


# ─── AI Helper ───────────────────────────────────────────────────────────────
def call_ai(conversation: list) -> str:
    """Call Groq with the full conversation and return assistant reply."""
    if not st.session_state.api_key:
        return "⚠️ Please add your Groq API key in the sidebar to continue."
    try:
        client = OpenAI(
            api_key=st.session_state.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        payload = [{"role": "system", "content": CRM_SYSTEM_PROMPT}] + conversation
        resp = client.chat.completions.create(
            model=st.session_state.model,
            messages=payload,
            max_tokens=1024,
            temperature=0.65,
        )
        return resp.choices[0].message.content
    except Exception as e:
        err = str(e)
        if "401" in err or "invalid_api_key" in err.lower():
            return "❌ Invalid API key. Please check the key in the sidebar."
        elif "rate_limit" in err.lower():
            return "⏳ Rate limit reached. Please wait a moment and try again."
        elif "connection" in err.lower():
            return "🌐 Connection error. Check your internet and try again."
        else:
            return f"❌ Something went wrong: {err}"


# ─── Auto-Greeting ────────────────────────────────────────────────────────────
# If no messages yet AND we have an API key, let Aria send the first message.
if not st.session_state.messages and not st.session_state.greeted and st.session_state.api_key:
    with st.spinner("Aria is typing…"):
        greeting = call_ai([])  # Empty history — AI will self-introduce per system prompt
    st.session_state.messages.append({"role": "assistant", "content": greeting})
    st.session_state.greeted = True
    st.rerun()

# If no API key yet — show a prompt
if not st.session_state.api_key and not st.session_state.messages:
    st.markdown("""
    <div style='text-align:center; padding: 3rem 1rem;'>
        <div style='font-size:3rem; margin-bottom:1rem;'>👋</div>
        <div style='color:#94a3b8; font-size:1rem; margin-bottom:.5rem;'>Hi! I'm Aria, your Bigin CRM consultant.</div>
        <div style='color:#475569; font-size:.88rem;'>Add your Groq API key in the sidebar to start our conversation.</div>
    </div>
    """, unsafe_allow_html=True)

# ─── Render Chat History ──────────────────────────────────────────────────────
summary_present = False

for msg in st.session_state.messages:
    content = msg["content"]
    if msg["role"] == "user":
        st.markdown(f"""
        <div class='msg-row-user'>
            <div class='bubble-user'>{content}</div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='msg-row-bot'>
            <div class='avatar'>🤖</div>
            <div class='bubble-bot'>{content}</div>
        </div>""", unsafe_allow_html=True)
        # Detect if the final summary has been produced
        if "📋 **Here's everything I've gathered so far:**" in content:
            summary_present = True

# ─── Download Button (appears after final summary) ───────────────────────────
if summary_present:
    # Extract last summary from messages
    summary_text = ""
    for msg in reversed(st.session_state.messages):
        if "📋 **Here's everything I've gathered so far:**" in msg["content"]:
            summary_text = msg["content"]
            break
    st.markdown("<div class='download-box'>✅ All details collected! You can download the summary below.</div>",
                unsafe_allow_html=True)
    st.download_button(
        label="📥 Download Summary",
        data=summary_text.encode("utf-8"),
        file_name="bigin_crm_requirements.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ─── Chat Input ───────────────────────────────────────────────────────────────
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Type your reply here…",
            label_visibility="collapsed",
        )
    with col2:
        submitted = st.form_submit_button("Send ➤", use_container_width=True)

if submitted and user_input.strip():
    user_msg = user_input.strip()

    # Append user turn
    st.session_state.messages.append({"role": "user", "content": user_msg})

    # Get AI reply
    with st.spinner("Aria is typing…"):
        reply = call_ai(st.session_state.messages)

    # Append assistant turn
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.rerun()
