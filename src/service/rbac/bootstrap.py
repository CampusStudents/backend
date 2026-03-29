import logging
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.security.utils import get_password_hash
from src.db.models import Permission, Role, User

logger = logging.getLogger()


async def bootstrap_rbac(session: AsyncSession) -> None:
    subjects = settings.rbac.initial_subjects
    actions = settings.rbac.initial_actions
    schema = settings.rbac.initial_permission_schema

    permissions = await _ensure_permissions(session, subjects, actions)
    roles = await _ensure_roles(session, schema)
    await _assign_permissions(session, permissions, roles, schema)
    await _ensure_admin_user(session, roles)

    await session.commit()


async def _ensure_permissions(
        session: AsyncSession,
        subjects: list[str],
        actions: list[str],
) -> dict[tuple[str, str], Permission]:
    existing = await session.execute(select(Permission))
    permissions = {(p.subject, p.action): p for p in existing.scalars().all()}

    for subject in subjects:
        for action in actions:
            key = (subject, action)
            if key not in permissions:
                permission = Permission(subject=subject, action=action)
                session.add(permission)
                permissions[key] = permission

    wildcard_key = ("*", "*")
    if wildcard_key not in permissions:
        permission = Permission(subject="*", action="*")
        session.add(permission)
        permissions[wildcard_key] = permission

    await session.flush()
    return permissions


async def _ensure_roles(
        session: AsyncSession, schema: dict[str, list[str]]
) -> dict[str, Role]:
    role_names = set(schema.keys()) | {
        settings.rbac.public_role_name,
        settings.rbac.admin_role_name,
    }
    result = await session.execute(select(Role).where(Role.name.in_(role_names)))
    existing = {role.name for role in result.scalars().all()}
    missing = role_names - existing
    if missing:
        session.add_all([Role(name=name) for name in missing])
        await session.flush()

    result = await session.execute(
        select(Role)
        .where(Role.name.in_(role_names))
        .options(selectinload(Role.permissions))
    )
    return {role.name: role for role in result.scalars().all()}


async def _assign_permissions(
        session: AsyncSession,
        permissions: dict[tuple[str, str], Permission],
        roles: dict[str, Role],
        schema: dict[str, list[str]],
) -> None:
    for role_name, scopes in schema.items():
        role = roles[role_name]
        role.permissions = await _resolve_permissions(
            session, permissions, scopes, role.permissions
        )

    admin_role = roles[settings.rbac.admin_role_name]
    for permission in permissions.values():
        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)


async def _resolve_permissions(
        session: AsyncSession,
        permissions: dict[tuple[str, str], Permission],
        scopes: Iterable[str],
        existing: list[Permission],
) -> list[Permission]:
    assigned_keys = {(permission.subject, permission.action) for permission in existing}

    def add_permission(permission: Permission) -> None:
        key = (permission.subject, permission.action)
        if key not in assigned_keys:
            existing.append(permission)
            assigned_keys.add(key)

    for scope in scopes:
        if scope == "*":
            for permission in permissions.values():
                add_permission(permission)
            continue

        if ":" not in scope:
            raise ValueError(f"Invalid scope format: {scope}")

        subject, action = scope.split(":", 1)
        key = (subject, action)
        permission = permissions.get(key)
        if not permission:
            permission = Permission(subject=subject, action=action)
            session.add(permission)
            permissions[key] = permission
        add_permission(permission)

    if permissions:
        await session.flush()
    return existing


async def _get_user_with_roles(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(
        select(User).where(User.email == email).options(selectinload(User.roles))
    )
    return result.scalar_one_or_none()


async def _ensure_admin_user(session: AsyncSession, roles: dict[str, Role]) -> None:
    admin_email = settings.rbac.admin_email
    admin_password = settings.rbac.admin_password
    if not admin_email or not admin_password:
        raise ValueError("Admin credentials are not configured")

    user = await _get_user_with_roles(session, admin_email)
    if not user:
        session.add(
            User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                is_active=True,
                is_verified=True,
            )
        )
        await session.flush()
        user = await _get_user_with_roles(session, admin_email)

    admin_role = roles[settings.rbac.admin_role_name]
    if admin_role not in user.roles:
        user.roles.append(admin_role)
