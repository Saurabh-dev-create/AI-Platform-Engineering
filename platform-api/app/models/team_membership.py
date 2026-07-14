from uuid import UUID

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import TeamRole
from app.database.base import Base, TimestampMixin, UUIDMixin


class TeamMembership(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Associate a platform user with a team and team-scoped role.

    Team membership is the foundation for tenant isolation and
    team-level authorization.
    """

    __tablename__ = "team_memberships"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "team_id",
            name="uq_team_memberships_user_id_team_id",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    team_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "teams.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[TeamRole] = mapped_column(
    Enum(
        TeamRole,
        name="team_role",
        native_enum=False,
        values_callable=lambda enum_class: [
            member.value
            for member in enum_class
        ],
    ),
    nullable=False,
    default=TeamRole.DEVELOPER,
   )

    def __repr__(self) -> str:
        return (
            f"<TeamMembership "
            f"user_id={self.user_id} "
            f"team_id={self.team_id} "
            f"role={self.role}>"
        )
