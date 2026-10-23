"""Решает, допустима ли обычная проверка tools; побочных действий нет."""

SUBSCRIPTION_KIND = "chatgpt_subscription"


def should_probe(profile):
    """Пустой, неверный или подписочный профиль не запускает общий probe-tools."""
    return isinstance(profile, dict) and bool(profile) and profile.get("kind") != SUBSCRIPTION_KIND
