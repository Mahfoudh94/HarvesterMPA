import uuid
from typing import List
from sqlalchemy import select

from logger import base_logger
from models import Announcement, AnnouncementImage, AnnouncementType, BusinessLine
from usecases import announcement_image, usecase_logger, session


def load_all():
    stmt = select(Announcement)
    return session.scalars(stmt).all()


def load_id_set():
    stmt = select(Announcement.id)
    result = session.scalars(stmt)
    return set(result)


def upsert(announcement_data: dict, images: List[str]):
    announcement_types_ids = announcement_data.pop('announcement_types')
    business_lines_ids = announcement_data.pop('business_lines')
    announcement_id_str = announcement_data.pop('id')
    announcement_id = uuid.UUID(announcement_id_str)
    announcement = Announcement(**announcement_data, id=announcement_id)

    try:
        announcement_types = session.scalars(
            select(AnnouncementType).where(
                AnnouncementType.id.in_(announcement_types_ids)
            )
        ).all()
        announcement.announcement_types.extend(announcement_types)

        business_lines = session.scalars(
            select(BusinessLine).where(
                BusinessLine.id.in_(business_lines_ids)
            )
        )
        announcement.business_lines.extend(business_lines)

        uploaded_images_paths = announcement_image.upload(images, announcement_id)
        uploaded_images = []

        for index, image_remote_path in enumerate(uploaded_images_paths):
            uploaded_images.append(
                AnnouncementImage(image_path=image_remote_path)
            )

        if len(uploaded_images) == 0:
            base_logger.warn(f"Empty uploaded images: {announcement_id_str}")

        announcement.images = uploaded_images
        session.add(announcement)

    except Exception as e:
        base_logger.error(f"announcement {announcement_id_str}: {e.__class__.__name__}: {e}")
        session.rollback()

def commit_all():
    try:
        session.commit()
    except Exception as e:
        usecase_logger.error(f"commit error: {e.__class__.__name__}: {e}")
        session.rollback()
