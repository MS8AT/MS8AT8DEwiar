"""Offline self-check contract for a ChatGPT subscription brain.

The caller owns profile storage and UI text. This module never reads credentials,
opens a connection, lists models, or sends inference.
"""

KIND = "chatgpt_subscription"


def evaluate(profile, local_ready, safe_errors=()):
    """Return a public result for a subscription profile, or None for another kind.

    ``local_ready(profile)`` must only validate local fields and policy. Messages are
    copied only from explicitly allowlisted exception classes; every other exception
    is reduced to a stable code.
    """
    if not isinstance(profile, dict) or profile.get("kind") != KIND:
        return None
    if not callable(local_ready):
        raise TypeError("local_ready must be callable")
    if isinstance(safe_errors, type) and issubclass(safe_errors, Exception):
        safe_errors = (safe_errors,)
    elif not (isinstance(safe_errors, tuple) and all(isinstance(item, type) and issubclass(item, Exception)
                                                     for item in safe_errors)):
        safe_errors = ()
    try:
        local_ready(profile)
    except safe_errors as exc:
        return {"handled": True, "ok": False, "code": "subscription_not_ready", "message": str(exc),
                "network_calls": 0, "model_calls": 0}
    except Exception:
        return {"handled": True, "ok": False, "code": "subscription_check_unavailable",
                "network_calls": 0, "model_calls": 0}
    return {"handled": True, "ok": True, "code": "subscription_ready_local",
            "network_calls": 0, "model_calls": 0}
