"""add rooms and reservation room association

Revision ID: eafb9e49b335
Revises: 4e315e2597dc
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "eafb9e49b335"
down_revision: Union[str, Sequence[str], None] = "4e315e2597dc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the rooms table.
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.UniqueConstraint("name"),
    )

    op.create_index(
        op.f("ix_rooms_id"),
        "rooms",
        ["id"],
        unique=False,
    )

    # 2. Add the room association as nullable initially.
    op.add_column(
        "reservations",
        sa.Column("room_id", sa.Integer(), nullable=True),
    )

    # 3. Add a named foreign key.
    op.create_foreign_key(
        "fk_reservations_room_id_rooms",
        "reservations",
        "rooms",
        ["room_id"],
        ["id"],
    )

    # 4. Create a default room for existing reservations.
    op.execute(
        sa.text(
            """
            INSERT INTO rooms (name)
            VALUES ('Room 101')
            """
        )
    )

    # 5. Assign existing reservations to the default room.
    op.execute(
        sa.text(
            """
            UPDATE reservations
            SET room_id = (
                SELECT id FROM rooms WHERE name = 'Room 101'
            )
            WHERE room_id IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_reservations_room_id_rooms",
        "reservations",
        type_="foreignkey",
    )
    op.drop_column("reservations", "room_id")

    op.drop_index(op.f("ix_rooms_id"), table_name="rooms")
    op.drop_table("rooms")
