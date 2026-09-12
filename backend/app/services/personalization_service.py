from __future__ import annotations

import re
from typing import Any


class PersonalizationService:
    @staticmethod
    def get_user_context(user) -> dict[str, str]:
        if user is None:
            return {}

        context = {}
        for key in [
            'profession',
            'industry',
            'skills',
            'career_goal',
            'target_audience',
            'preferred_tone',
            'preferred_style',
        ]:
            value = getattr(user, key, None)
            if isinstance(value, str) and value.strip():
                context[key] = value.strip()
        return context

    @staticmethod
    def is_personalized_generation(user, payload: dict | None = None) -> bool:
        if payload and isinstance(payload, dict):
            if payload.get('personalized_generation') is not None:
                return bool(payload.get('personalized_generation'))
        return bool(getattr(user, 'personal_brand_mode', False))

    @staticmethod
    def build_context_block(user) -> str:
        context = PersonalizationService.get_user_context(user)
        if not context:
            return ''

        parts = []
        for key, value in context.items():
            label = key.replace('_', ' ').title()
            parts.append(f'{label}: {value}')
        return ' | '.join(parts)

    @staticmethod
    def enrich_payload(payload: dict, user) -> dict:
        if not PersonalizationService.is_personalized_generation(user, payload):
            return payload

        context_block = PersonalizationService.build_context_block(user)
        if not context_block:
            return payload

        enriched = dict(payload)
        enriched['profile_context'] = context_block
        enriched['personalization_guidance'] = (
            'Use the user profile only when it is directly relevant to the topic. '
            'Never invent details or attributes that are not explicitly provided. '
            'Keep the writing authentic, professional, and aligned with their career goals.'
        )
        return enriched

    @staticmethod
    def generate_hooks(topic: str, profile_context: str = '') -> list[str]:
        topic_clean = (topic or 'my work').strip()
        profile_note = f" for {profile_context}" if profile_context else ''
        hooks = [
            f"I was curious about {topic_clean} and what it taught me next{profile_note}.",
            f"This is the story behind {topic_clean} — and why it changed how I work{profile_note}.",
            f"What if the biggest lesson in {topic_clean} was not the result, but the process{profile_note}?",
            f"Most people think {topic_clean} is about output. It is really about what you learn along the way{profile_note}.",
            f"I used to believe {topic_clean} was simple. The result taught me otherwise{profile_note}.",
        ]
        return hooks[:5]

    @staticmethod
    def generate_hashtags(topic: str, profile_context: str = '') -> list[str]:
        topic_tokens = re.findall(r'[A-Za-z]+', (topic or '').strip())
        primary = []
        for token in topic_tokens[:3]:
            if token.lower() not in {'the', 'and', 'for', 'with', 'about'}:
                primary.append(token.title())
        default_tags = ['#CareerGrowth', '#ProfessionalDevelopment', '#Leadership', '#Learning', '#LinkedIn']
        if not primary:
            return default_tags[:5]
        custom = [f'#{tag}' for tag in primary[:3]]
        return (custom + default_tags)[:5]

    @staticmethod
    def generate_ctas(profile_context: str = '') -> list[str]:
        base = [
            'What is something you are learning right now in your own work?',
            'I would love to hear how others are approaching this in their careers.',
            'If this resonates, I am happy to share a few lessons from the process.',
            'What has been the biggest challenge in your learning journey this year?',
        ]
        if profile_context:
            return base[:4]
        return base[:4]

    @staticmethod
    def quality_checks(content: str) -> dict[str, Any]:
        text = (content or '').strip()
        words = re.findall(r"\b[\w'-]+\b", text)
        word_count = len(words)
        hashtags = re.findall(r'#\w+', text)
        emojis = re.findall(r'[\U0001F300-\U0001FAFF\u2600-\u27BF]', text)
        repeated_words = []
        counts = {}
        for word in [w.lower() for w in words]:
            if len(word) > 3:
                counts[word] = counts.get(word, 0) + 1
        for word, count in counts.items():
            if count > 3:
                repeated_words.append(word)

        issues = []
        if word_count < 40:
            issues.append('Word count is below the recommended range for a LinkedIn post.')
        if len(hashtags) > 5:
            issues.append('Too many hashtags for a concise professional post.')
        if len(emojis) > 2:
            issues.append('Excessive emojis may reduce credibility.')
        if repeated_words:
            issues.append('Repeated phrases or words are noticeable in the draft.')
        if re.search(r'\b(?:guaranteed|100%|always|never|everyone|nobody)\b', text, re.IGNORECASE):
            issues.append('Claims sound unsupported or exaggerated.')
        if re.search(r'\b(?:\d+%|\d+ of \d+|\d+ million|\d+ thousand)\b', text) and not re.search(r'\b(?:about|approximately|roughly|around)\b', text, re.IGNORECASE):
            issues.append('Numeric claims should be supported by clear context.')
        if not re.search(r'\b(?:I|we|our|this|that|because|learned|built|worked)\b', text, re.IGNORECASE):
            issues.append('Missing clear context or first-person framing.')

        return {
            'passes': len(issues) == 0,
            'word_count': word_count,
            'repeated_phrases': repeated_words,
            'hashtags': hashtags,
            'emoji_count': len(emojis),
            'issues': issues,
        }
