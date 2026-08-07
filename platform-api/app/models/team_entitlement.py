from uuid import UUID

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import PlanType
from app.database.base import Base, TimestampMixin, UUIDMixin


class TeamEntitlement(
    UUIDMixin,
    TimestampMixin,
    Base,
):
    """
    Plan and resource guardrails assigned to a tenant workspace.

    Entitlements are enforced by the Platform API so clients cannot
    bypass plan limits by calling backend endpoints directly.
    """

    __tablename__ = "team_entitlements"

    team_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey(
            "teams.id",
            ondelete="CASCADE",
        ),
        unique=True,
        index=True,
        nullable=False,
    )

    plan: Mapped[PlanType] = mapped_column(
        Enum(
            PlanType,
            name="plan_type",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=PlanType.FREE,
        nullable=False,
    )

    max_projects: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False,
    )

    max_agents: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    max_members: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    allow_runtime_execution: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    allow_paid_provider_usage: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    allow_staging_deployments: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    allow_production_deployments: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<TeamEntitlement "
            f"team_id={self.team_id} "
            f"plan={self.plan.value!r}>"
        )
