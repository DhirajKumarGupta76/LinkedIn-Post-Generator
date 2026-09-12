from datetime import datetime, timezone

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    profession: Mapped[str | None] = mapped_column(String(200), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    career_goal: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(String(150), nullable=True)
    preferred_tone: Mapped[str | None] = mapped_column(String(120), nullable=True)
    preferred_style: Mapped[str | None] = mapped_column(String(120), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    personal_brand_mode: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_login: Mapped[datetime | None] = mapped_column(nullable=True)

    generated_posts = relationship('GeneratedPost', back_populates='user', cascade='all, delete-orphan')
    saved_posts = relationship('SavedPost', back_populates='user', cascade='all, delete-orphan')

    def to_public_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'profile_image': self.profile_image,
            'bio': self.bio,
            'profession': self.profession,
            'industry': self.industry,
            'skills': self.skills,
            'career_goal': self.career_goal,
            'target_audience': self.target_audience,
            'preferred_tone': self.preferred_tone,
            'preferred_style': self.preferred_style,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'personal_brand_mode': self.personal_brand_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }
