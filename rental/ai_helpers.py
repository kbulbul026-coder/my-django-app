import requests
from django.conf import settings


def generate_smart_whatsapp_message(record):
    """
    Generate a polite WhatsApp message using Gemini REST API
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)

    if not api_key:
        return get_fallback_message(record)

    # You can change the model name if needed (e.g. gemini-2.0-flash or gemini-3.6-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    remaining = record.remaining

    if remaining <= 0:
        status_text = "This bill is fully paid."
    else:
        status_text = f"Remaining amount is ₹{remaining}."

    prompt = f"""
Write a short and polite WhatsApp message in simple Hindi + English mix for a tenant.

Details:
- Tenant Name: {record.tenant.name}
- Month: {record.month_year}
- Total Bill: ₹{record.total_due}
- Already Paid: ₹{record.amount_paid}
- Remaining: ₹{remaining}
- Status: {status_text}

Rules:
- Keep it polite and professional
- Maximum 5 lines
- If the bill is fully paid, thank the tenant
- If money is still pending, politely ask for the remaining amount
- End with thank you
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()

        message = data['candidates'][0]['content']['parts'][0]['text']
        return message.strip()

    except Exception as e:
        print("Gemini Error:", e)
        return get_fallback_message(record)


def get_fallback_message(record):
    """Fallback message if AI fails"""
    remaining = record.remaining

    if remaining <= 0:
        # Fully Paid
        return (
            f"नमस्ते {record.tenant.name} जी,\n\n"
            f"आपका {record.month_year} का किराया बिल:\n"
            f"• कुल बिल: ₹{record.total_due}\n"
            f"• भुगतान: ₹{record.amount_paid}\n\n"
            f"पूरा भुगतान प्राप्त हो गया है।\n"
            f"धन्यवाद! 🙏"
        )
    else:
        # Pending or Partial
        return (
            f"नमस्ते {record.tenant.name} जी,\n\n"
            f"आपका {record.month_year} का किराया बिल:\n"
            f"• कुल बिल: ₹{record.total_due}\n"
            f"• भुगतान: ₹{record.amount_paid}\n"
            f"• बाकी: ₹{remaining}\n\n"
            f"कृपया शेष राशि का भुगतान करें।\n"
            f"धन्यवाद!"
        )
