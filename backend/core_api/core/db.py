from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from fastapi import HTTPException, status

from core_api.core.config import settings
from core_api.core.logging import logger

engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    db = SessionLocal()
    try:
        logger.debug("DB session opened")
        yield db
        db.commit()
        logger.debug("DB commit ok")
    except (IntegrityError, DataError) as e:
        db.rollback()
        logger.debug("DB rollback on 4xx")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or conflicting data",
        ) from e
    except SQLAlchemyError as e:
        db.rollback()
        logger.debug("DB rollback on 5xx")
        raise HTTPException(status_code=500, detail="Database error") from e
    except Exception as e:
        db.rollback()
        logger.debug(f"DB rollback on Exception: {e}")
        raise
    finally:
        db.close()
        logger.debug("DB session closed")
