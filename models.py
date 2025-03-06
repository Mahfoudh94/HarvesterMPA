import datetime
import uuid
from typing import List

from sqlalchemy import Table, Column, ForeignKey, UUID as sa_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import ModelBase

announcements_business_lines_association = Table(
    "announcements_business_lines_association",
    ModelBase.metadata,
    Column("announcement_id", ForeignKey("announcements.id"), primary_key=True),
    Column("business_line_id", ForeignKey("business_lines.id"), primary_key=True),
)

announcements_types_association = Table(
    "announcements_types_association",
    ModelBase.metadata,
    Column("announcement_id", ForeignKey("announcements.id"), primary_key=True),
    Column("type_id", ForeignKey("announcement_types.id"), primary_key=True),
)


class Announcement(ModelBase):
    __tablename__ = 'announcements'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(default="")
    description: Mapped[str] = mapped_column(default="")
    number: Mapped[str] = mapped_column(default=True)
    owner: Mapped[str] = mapped_column(nullable=True)
    terms: Mapped[str] = mapped_column(nullable=True)
    contact: Mapped[str] = mapped_column(nullable=True)
    due_amount: Mapped[int] = mapped_column(default=-1)
    wilaya: Mapped[int] = mapped_column(nullable=True)
    publish_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now())
    due_date: Mapped[datetime.datetime] = mapped_column(nullable=True)
    status: Mapped[bool] = mapped_column()

    business_lines: Mapped[List["BusinessLine"]] = relationship(
        secondary=announcements_business_lines_association, back_populates="announcements",
    )
    announcement_types: Mapped[List["AnnouncementType"]] = relationship(
        secondary=announcements_types_association, back_populates="announcements",
    )
    images: Mapped[List["AnnouncementImage"]] = relationship(
        back_populates="announcement", cascade="all, delete-orphan"
    )


class AnnouncementImage(ModelBase):
    __tablename__ = 'announcement_images'

    id: Mapped[int] = mapped_column(primary_key=True)
    announcement_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('announcements.id'))
    image_path: Mapped[str] = mapped_column(nullable=False)

    announcement: Mapped["Announcement"] = relationship(back_populates="images")


class AnnouncementType(ModelBase):
    __tablename__ = 'announcement_types'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    announcements: Mapped[List["Announcement"]] = relationship(
        secondary=announcements_types_association,
        back_populates="announcement_types"
    )


class BusinessLine(ModelBase):
    __tablename__ = 'business_lines'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    announcements: Mapped[List["Announcement"]] = relationship(
        secondary=announcements_business_lines_association,
        back_populates="business_lines"
    )
