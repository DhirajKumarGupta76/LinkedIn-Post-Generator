from __future__ import annotations

import re


class RepurposeService:
    @staticmethod
    def repurpose(content: str, platform: str) -> str:
        text = (content or '').strip()
        if not text:
            raise ValueError('Content is required to repurpose.')

        normalized = platform.lower().strip()
        if normalized not in {'x', 'instagram', 'facebook', 'whatsapp', 'email'}:
            raise ValueError('Unsupported platform for repurposing.')

        first_sentence = text.split('. ')[0].strip() if '. ' in text else text
        summary = re.sub(r'\s+', ' ', text).strip()

        if normalized == 'x':
            short = summary[:240].rstrip()
            if len(short) < len(summary):
                short = short.rsplit(' ', 1)[0].strip() + '…'
            return short

        if normalized == 'instagram':
            caption = summary[:220].rstrip()
            if len(caption) < len(summary):
                caption = caption.rsplit(' ', 1)[0].strip() + '…'
            return f"Instagram caption:\n{caption}\n\n#CareerGrowth #Learning #ProfessionalDevelopment"

        if normalized == 'facebook':
            return f"{summary[:300].rstrip()}\n\nI’d love to hear how others are approaching this in their work."

        if normalized == 'whatsapp':
            return summary[:400].rstrip()

        subject = first_sentence[:80].rstrip() if first_sentence else 'Professional Update'
        return (
            f"Subject: {subject}\n\nHi there,\n\n"
            f"{summary}\n\n"
            f"Best,\n\n[Your Name]"
        )
