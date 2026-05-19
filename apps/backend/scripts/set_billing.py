"""
CLI-скрипт для ручного управления биллинговыми лимитами пользователя.

Запуск:
    docker compose exec backend python scripts/set_billing.py \
        --email user@example.com --plan pro --limit 100 --days 30

Все аргументы кроме --email опциональны — обновляются только переданные поля.
--days 0  устанавливает subscription_ends_at = null (бессрочная подписка).
"""

import argparse
import os
import sys
from datetime import UTC, datetime, timedelta

import psycopg2
import psycopg2.extras

VALID_PLANS = ("free", "standart", "pro", "custom")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Управление биллинговыми лимитами пользователя в обход платёжного хаба."
    )
    parser.add_argument("--email", required=True, help="Email пользователя в БД")
    parser.add_argument(
        "--plan",
        choices=VALID_PLANS,
        default=None,
        help=f"Тариф: {', '.join(VALID_PLANS)}",
    )
    parser.add_argument("--limit", type=int, default=None, help="Максимум дел на мониторинге")
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Дней подписки от сейчас (0 = бессрочно / null)",
    )
    return parser


def _pg_url(url: str) -> str:
    """Убирает SQLAlchemy-диалект из URL для psycopg2."""
    for prefix in ("postgresql+asyncpg://", "postgresql+psycopg2://"):
        if url.startswith(prefix):
            return "postgresql://" + url[len(prefix):]
    return url


def run(email: str, plan: str | None, limit: int | None, days: int | None) -> int:
    database_url = os.environ.get("DATABASE_URL", "")
    if not database_url:
        print("Ошибка: переменная окружения DATABASE_URL не задана.")
        return 1

    conn = psycopg2.connect(_pg_url(database_url))
    conn.autocommit = False

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("SELECT id, email, plan, cases_limit, subscription_ends_at FROM users WHERE email = %s", (email,))
            row = cur.fetchone()

            if row is None:
                print(f"Пользователь с email '{email}' не найден.")
                return 1

            set_clauses: list[str] = []
            params: list = []

            if plan is not None:
                set_clauses.append("plan = %s::plan_enum")
                params.append(plan)

            if limit is not None:
                set_clauses.append("cases_limit = %s")
                params.append(limit)

            if days is not None:
                if days == 0:
                    set_clauses.append("subscription_ends_at = NULL")
                else:
                    set_clauses.append("subscription_ends_at = %s")
                    params.append(datetime.now(UTC) + timedelta(days=days))

            if not set_clauses:
                print("Ни один аргумент для обновления не передан. Изменений нет.")
                return 0

            set_clauses.append("billing_updated_at = %s")
            params.append(datetime.now(UTC))
            params.append(email)

            sql = f"UPDATE users SET {', '.join(set_clauses)} WHERE email = %s RETURNING email, plan, cases_limit, subscription_ends_at, billing_updated_at"
            cur.execute(sql, params)
            updated = cur.fetchone()
            conn.commit()

            ends_at = updated["subscription_ends_at"].isoformat() if updated["subscription_ends_at"] else "null (бессрочно)"
            updated_names = []
            if plan is not None:
                updated_names.append("plan")
            if limit is not None:
                updated_names.append("cases_limit")
            if days is not None:
                updated_names.append("subscription_ends_at")

            print(
                f"Обновлено: {', '.join(updated_names)}\n"
                f"  email:                {updated['email']}\n"
                f"  plan:                 {updated['plan']}\n"
                f"  cases_limit:          {updated['cases_limit']}\n"
                f"  subscription_ends_at: {ends_at}\n"
                f"  billing_updated_at:   {updated['billing_updated_at'].isoformat()}"
            )
            return 0

    except Exception as exc:
        conn.rollback()
        print(f"Ошибка: {exc}")
        return 1
    finally:
        conn.close()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args.email, args.plan, args.limit, args.days))


if __name__ == "__main__":
    main()
