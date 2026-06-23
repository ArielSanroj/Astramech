"""Outreach message generation using OpenAI."""
from typing import Optional
from openai import OpenAI

client = OpenAI()


def generate_outreach(post_text: str, author: Optional[str]) -> str:
    """Generate empathetic X reply using GPT."""
    name = f"@{author}" if author else "there"
    system = (
        "You write empathetic, insightful X replies under 280 characters. "
        "Tone: professional, warm, no hard sell. Subtly nod to Clio Circle AI "
        "(employee wellness, retention, leadership coaching, ethical AI, crisis response)."
    )
    user = (
        f"Post by {name}:\n{post_text}\n\n"
        "Write ONE concise reply. Acknowledge their pain point, add a useful insight, "
        "subtly note that tools like Clio Circle AI can help, and invite dialogue. "
        "No stats, no promises, no pushy CTA."
    )
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        max_tokens=100,
        temperature=0.6,
    )
    text = resp.choices[0].message.content.strip()
    return text[:280]
