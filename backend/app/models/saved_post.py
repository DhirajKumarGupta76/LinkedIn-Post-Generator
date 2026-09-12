from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class SavedPost(db.Model):
    __tablename__ = 'saved_posts'

    __table_args__ = (
        Index('ix_saved_posts_user_post', 'user_id', 'post_id', unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('generated_posts.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=False, default='[]')
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship('User', back_populates='saved_posts')
    generated_post = relationship('GeneratedPost', back_populates='saved_posts')

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'post_id': self.post_id,
            'title': self.title,
            'content': self.content,
            'tags': json.loads(self.tags or '[]'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
