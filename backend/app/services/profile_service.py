from __future__ import annotations

from typing import Any

PROFILE_FIELDS = [
    'profession',
    'industry',
    'skills',
    'career_goal',
    'target_audience',
    'preferred_tone',
    'preferred_style',
    'linkedin_url',
    'github_url',
    'portfolio_url',
]


class ProfileService:
    @staticmethod
    def normalize_profile_data(data: dict[str, Any] | None) -> dict[str, Any]:
        profile: dict[str, Any] = {}
        if not isinstance(data, dict):
            return profile

        for field in PROFILE_FIELDS:
            value = data.get(field)
            if value is None:
                continue
            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned:
                    profile[field] = cleaned
            else:
                profile[field] = value
        return profile

    @staticmethod
    def profile_completion(user) -> int:
        if user is None:
            return 0

        completed = 0
        for field in PROFILE_FIELDS:
            value = getattr(user, field, None)
            if isinstance(value, str):
                if value.strip():
                    completed += 1
            elif value not in (None, '', False):
                completed += 1

        return int(round((completed / len(PROFILE_FIELDS)) * 100))

    @staticmethod
    def build_profile_summary(user) -> dict[str, Any]:
        if user is None:
            return {
                'profile_completion': 0,
                'profile': {},
            }

        profile = {key: getattr(user, key, None) for key in PROFILE_FIELDS}
        profile = {key: value.strip() if isinstance(value, str) else value for key, value in profile.items()}

        return {
            'profile_completion': ProfileService.profile_completion(user),
            'profile': profile,
            'personal_brand_mode': bool(getattr(user, 'personal_brand_mode', False)),
        }
