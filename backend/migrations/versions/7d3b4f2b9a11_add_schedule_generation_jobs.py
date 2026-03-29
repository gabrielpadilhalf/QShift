"""add schedule generation jobs

Revision ID: 7d3b4f2b9a11
Revises: c31bcd7719b4
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "7d3b4f2b9a11"
down_revision: Union[str, Sequence[str], None] = "c31bcd7719b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "schedule_generation_job",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("request_payload", sa.JSON(), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'done', 'failed')",
            name="schedule_generation_job_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["app_user.id"],
            name=op.f("fk_schedule_generation_job_user_id_app_user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_schedule_generation_job")),
    )
    op.create_index(
        "ix_schedule_generation_job_user_created_at",
        "schedule_generation_job",
        ["user_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_schedule_generation_job_user_status",
        "schedule_generation_job",
        ["user_id", "status"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_schedule_generation_job_user_status",
        table_name="schedule_generation_job",
    )
    op.drop_index(
        "ix_schedule_generation_job_user_created_at",
        table_name="schedule_generation_job",
    )
    op.drop_table("schedule_generation_job")
