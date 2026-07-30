from groq import AsyncGroq
from logger import logger
from core.config import GROQ_API_KEY, GROQ_MODEL


# used if the API key is missing or the call fails, so the chat never breaks
FALLBACK_MESSAGE = "The doctor hasn't replied yet. Please hold on, they will respond as soon as possible."

SYSTEM_PROMPT = (
    "You are standing in for a doctor who has not replied yet in a patient-doctor chat. "
    "Reassure the patient briefly and let them know the doctor will respond soon. "
    "Keep it to one or two sentences and do not give any medical advice."
)

client = AsyncGroq(api_key=GROQ_API_KEY)

async def generate_ai_reply(chat_history: list[dict]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in chat_history[-10:]:
        if m.get("role") == "doctor":
            role = "assistant"
        else:
            role = "user"
        messages.append({"role": role, "content": m.get("content", "")})

    try:
        response = await client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        logger.error(f"groq api call failed: {e}")
        return FALLBACK_MESSAGE


