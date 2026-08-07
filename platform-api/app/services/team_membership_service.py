from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.constants import TeamRole
from app.core.exceptions import (
    PlatformException,
    ResourceConflictException,
    ResourceNotFoundException,
)
from app.models.team_membership import TeamMembership
from app.models.user import User
from app.repositories.team_membership_repository import (
    TeamMembershipRepository,
)
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository
from app.schemas.team_membership import (
    TeamMemberAdd,
    TeamMemberRoleUpdate,
)
from app.services.entitlement_service import EntitlementService


class TeamMembershipService:
    """
    Business logic for team membership lifecycle and team-scoped RBAC.
    """

    def __init__(
        self,
        team_repository: TeamRepository,
        membership_repository: TeamMembershipRepository,
        user_repository: UserRepository,
        entitlement_service: EntitlementService,
    ) -> None:
        self.team_repository = team_repository
        self.membership_repository = membership_repository
        self.user_repository = user_repository
        self.entitlement_service = entitlement_service

    def _require_team_admin(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
    ) -> TeamMembership:
        team = self.team_repository.get_for_user_by_id(
            db,
            team_id=team_id,
            user_id=current_user.id,
        )

        if team is None:
            raise ResourceNotFoundException(
                resource="Team",
                resource_id=str(team_id),
            )

        membership = self.membership_repository.get_by_user_and_team(
            db,
            user_id=current_user.id,
            team_id=team_id,
        )

        if (
            membership is None
            or membership.role != TeamRole.TEAM_ADMIN
        ):
            raise PlatformException(
                message="Team administrator role required",
                error_code="TEAM_ADMIN_REQUIRED",
                status_code=403,
            )

        return membership

    def add_member(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
        member_data: TeamMemberAdd,
    ) -> TeamMembership:
        self._require_team_admin(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        entitlement = self.entitlement_service.require_for_team(
            db,
            team_id=team_id,
        )

        current_members = (
            self.membership_repository.count_for_team(
                db,
                team_id=team_id,
            )
        )

        self.entitlement_service.require_member_capacity(
            entitlement,
            current_members=current_members,
        )

        normalized_email = member_data.email.lower()

        target_user = self.user_repository.get_by_email(
            db,
            normalized_email,
        )

        if target_user is None:
            raise ResourceNotFoundException(
                resource="User",
                resource_id=normalized_email,
            )

        existing_membership = (
            self.membership_repository.get_by_user_and_team(
                db,
                user_id=target_user.id,
                team_id=team_id,
            )
        )

        if existing_membership is not None:
            raise ResourceConflictException(
                resource="TeamMembership",
                field="user_id",
                value=str(target_user.id),
            )

        try:
            membership = self.membership_repository.create(
                db,
                user_id=target_user.id,
                team_id=team_id,
                role=member_data.role,
            )

            db.commit()
            db.refresh(membership)

            return membership

        except IntegrityError as exc:
            db.rollback()

            raise ResourceConflictException(
                resource="TeamMembership",
                field="user_id",
                value=str(target_user.id),
            ) from exc

    def list_members(
        self,
        db: Session,
        *,
        team_id: UUID,
        current_user: User,
    ) -> list[TeamMembership]:
        self._require_team_admin(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        return self.membership_repository.list_for_team(
            db,
            team_id=team_id,
        )

    def update_member_role(
        self,
        db: Session,
        *,
        team_id: UUID,
        target_user_id: UUID,
        current_user: User,
        role_data: TeamMemberRoleUpdate,
    ) -> TeamMembership:
        self._require_team_admin(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        membership = (
            self.membership_repository.get_by_user_and_team(
                db,
                user_id=target_user_id,
                team_id=team_id,
            )
        )

        if membership is None:
            raise ResourceNotFoundException(
                resource="TeamMembership",
                resource_id=str(target_user_id),
            )

        if (
            membership.role == TeamRole.TEAM_ADMIN
            and role_data.role != TeamRole.TEAM_ADMIN
        ):
            admin_count = (
                self.membership_repository.count_for_team_by_role(
                    db,
                    team_id=team_id,
                    role=TeamRole.TEAM_ADMIN,
                )
            )

            if admin_count <= 1:
                raise PlatformException(
                    message="The final team administrator cannot be demoted",
                    error_code="FINAL_TEAM_ADMIN_REQUIRED",
                    status_code=409,
                )

        membership = self.membership_repository.update_role(
            db,
            membership=membership,
            role=role_data.role,
        )

        db.commit()
        db.refresh(membership)

        return membership

    def remove_member(
        self,
        db: Session,
        *,
        team_id: UUID,
        target_user_id: UUID,
        current_user: User,
    ) -> None:
        self._require_team_admin(
            db,
            team_id=team_id,
            current_user=current_user,
        )

        membership = (
            self.membership_repository.get_by_user_and_team(
                db,
                user_id=target_user_id,
                team_id=team_id,
            )
        )

        if membership is None:
            raise ResourceNotFoundException(
                resource="TeamMembership",
                resource_id=str(target_user_id),
            )

        if membership.role == TeamRole.TEAM_ADMIN:
            admin_count = (
                self.membership_repository.count_for_team_by_role(
                    db,
                    team_id=team_id,
                    role=TeamRole.TEAM_ADMIN,
                )
            )

            if admin_count <= 1:
                raise PlatformException(
                    message="The final team administrator cannot be removed",
                    error_code="FINAL_TEAM_ADMIN_REQUIRED",
                    status_code=409,
                )

        self.membership_repository.delete(
            db,
            membership=membership,
        )

        db.commit()
