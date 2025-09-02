from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "67915f146566"
down_revision = "0001"
branch_labels = None
depends_on = None

def _index_exists(conn, index_name: str) -> bool:
    # Check for an index by name in the current schema (PostgreSQL)
    return bool(
        conn.execute(
            sa.text(
                "SELECT EXISTS (SELECT 1 "
                "FROM pg_indexes "
                "WHERE schemaname = current_schema() AND indexname = :n)"
            ),
            {"n": index_name},
        ).scalar()
    )

def _column_exists(insp, table: str, column: str, schema: str | None = None) -> bool:
    return column in {c["name"] for c in insp.get_columns(table, schema=schema)}

def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    # 1) Create refresh_tokens table only if missing
    if not insp.has_table("refresh_tokens"):
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("token", sa.String(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("token"),
        )

    # 2) Create index on refresh_tokens.id if missing
    ix_name = op.f("ix_refresh_tokens_id")
    if not _index_exists(bind, ix_name):
        op.create_index(ix_name, "refresh_tokens", ["id"], unique=False)

    # 3) image_history: ensure meta_data exists without duplicating
    if insp.has_table("image_history"):
        has_meta_data = _column_exists(insp, "image_history", "meta_data")
        has_metadata = _column_exists(insp, "image_history", "metadata")
        if not has_meta_data and has_metadata:
            # Proper rename preserves data
            op.alter_column("image_history", "metadata", new_column_name="meta_data")
        elif not has_meta_data and not has_metadata:
            op.add_column("image_history", sa.Column("meta_data", sa.JSON(), nullable=True))
        elif has_meta_data and has_metadata:
            # If both exist, drop the legacy column defensively
            op.execute("ALTER TABLE image_history DROP COLUMN IF EXISTS metadata")

    # 4) search_history: add meta_data only if missing
    if insp.has_table("search_history"):
        if not _column_exists(insp, "search_history", "meta_data"):
            op.add_column("search_history", sa.Column("meta_data", sa.JSON(), nullable=True))

def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)

    # Reverse search_history addition
    if insp.has_table("search_history") and _column_exists(insp, "search_history", "meta_data"):
        op.execute("ALTER TABLE search_history DROP COLUMN IF EXISTS meta_data")

    # Reverse image_history change
    if insp.has_table("image_history"):
        has_meta_data = _column_exists(insp, "image_history", "meta_data")
        has_metadata = _column_exists(insp, "image_history", "metadata")
        if has_meta_data and not has_metadata:
            op.alter_column("image_history", "meta_data", new_column_name="metadata")
        elif has_meta_data:
            op.execute("ALTER TABLE image_history DROP COLUMN IF EXISTS meta_data")

    # Drop index and table if present
    ix_name = op.f("ix_refresh_tokens_id")
    if _index_exists(bind, ix_name):
        op.drop_index(ix_name, table_name="refresh_tokens")
    if insp.has_table("refresh_tokens"):
        op.drop_table("refresh_tokens")
