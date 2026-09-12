import json
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class GeneratedPost(db.Model):
    __tablename__ = 'generated_posts'

    __table_args__ = (
        Index('ix_generated_posts_user_created', 'user_id', 'created_at'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    achievement: Mapped[str] = mapped_column(String(120), nullable=False)
    mood: Mapped[str] = mapped_column(String(80), nullable=False)
    feeling: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[str] = mapped_column(String(80), nullable=False)
    audience: Mapped[str] = mapped_column(String(120), nullable=False)
    style: Mapped[str] = mapped_column(String(120), nullable=False)
    word_length: Mapped[str] = mapped_column(String(60), nullable=False)
    generated_content: Mapped[str] = mapped_column(Text, nullable=False)
    edited_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship('User', back_populates='generated_posts')
    saved_posts = relationship('SavedPost', back_populates='generated_post', cascade='all, delete-orphan')

    def set_hashtags(self, tags):
        self.hashtags = json.dumps(tags or [])

    def get_hashtags(self):
        try:
            parsed = json.loads(self.hashtags or '[]')
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
        return []

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'topic': self.topic,
            'achievement': self.achievement,
            'mood': self.mood,
            'feeling': self.feeling,
            'tone': self.tone,
            'audience': self.audience,
            'style': self.style,
            'word_length': self.word_length,
            'generated_content': self.generated_content,
            'edited_content': self.edited_content or self.generated_content,
            'content': self.edited_content or self.generated_content,
            'hashtags': self.get_hashtags(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
