import requests
from django.conf import settings

def generate_smart_whatsapp_message(record):
    """
    Generate WhatsApp message using Gemini REST API
    """
    api_key = settings.GEMINI_API_KEY
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"

    prompt = f"""
Write a short and polite WhatsApp message in simple Hindi + English mix for a tenant.

Details:
- Tenant Name: {record.tenant.name}
- Month: {record.month_year}
- Total Bill: ₹{record.total_due}
- Already Paid: ₹{record.amount_paid}
- Remaining Amount: ₹{record.remaining}

Rules:
- Keep it polite and professional
- Maximum 4-5 lines
- End with thank you
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        message = data['candidates'][0]['content']['parts'][0]['text']
        return message.strip()
    except Exception as e:
        # Fallback message
        return (
            f"नमस्ते {record.tenant.name} जी,\n\n"
            f"आपका {record.month_year} का किराया बिल:\n"
            f"कुल बिल: ₹{record.total_due}\n"
            f"भुगतान: ₹{record.amount_paid}\n"
            f"बाकी: ₹{record.remaining}\n\n"
            f"कृपया भुगतान करें। धन्यवाद!"
        )
