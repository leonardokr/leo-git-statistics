"""Dispatch webhook notifications when trigger conditions are met."""

import logging
from typing import Any, Dict, List

import aiohttp

from src.db.snapshots import snapshot_store
from src.db.webhooks import webhook_store

logger = logging.getLogger(__name__)


def _check_threshold(field: str, threshold: int, current: Dict[str, Any], previous: Dict[str, Any]) -> bool:
    """Check if a field crossed a threshold between two snapshots.

    :param field: Stats field name to check.
    :param threshold: Value that must be crossed.
    :param current: Current snapshot data.
    :param previous: Previous snapshot data.
    :returns: True if the threshold was crossed upward.
    :rtype: bool
    """
    cur_val = current.get(field, 0)
    prev_val = previous.get(field, 0)
    return prev_val < threshold <= cur_val


def evaluate_conditions(
    conditions: Dict[str, Any],
    current: Dict[str, Any],
    previous: Dict[str, Any],
) -> List[str]:
    """Evaluate webhook conditions and return triggered event descriptions.

    Supported condition keys:

    - ``stars_threshold``: int -- triggers when total_stars crosses this value.
    - ``streak_broken``: bool -- triggers when current_streak drops to 0.
    - ``contributions_record``: bool -- triggers when total_contributions exceeds previous.

    :param conditions: Condition dictionary from the webhook registration.
    :param current: Current stats snapshot.
    :param previous: Previous stats snapshot.
    :returns: List of triggered event description strings (empty if none).
    :rtype: list[str]
    """
    triggered = []

    stars_threshold = conditions.get("stars_threshold")
    if stars_threshold is not None:
        if _check_threshold("total_stars", int(stars_threshold), current, previous):
            triggered.append(f"Stars crossed {stars_threshold}")

    if conditions.get("streak_broken"):
        prev_streak = previous.get("current_streak", 0)
        cur_streak = current.get("current_streak", 0)
        if prev_streak > 0 and cur_streak == 0:
            triggered.append("Streak broken")

    if conditions.get("contributions_record"):
        prev_contribs = previous.get("total_contributions", 0)
        cur_contribs = current.get("total_contributions", 0)
        if cur_contribs > prev_contribs > 0:
            triggered.append(f"New contributions record: {cur_contribs}")

    return triggered


async def dispatch_webhooks(username: str, current_snapshot: Dict[str, Any]) -> int:
    """Check all webhooks for a user and fire matching notifications.

    :param username: GitHub username whose snapshot was just taken.
    :param current_snapshot: The current statistics data.
    :returns: Number of webhooks that were triggered.
    :rtype: int
    """
    previous = snapshot_store.get_latest_snapshot(username)
    if previous is None:
        return 0

    hooks = webhook_store.list_by_user(username)
    fired = 0

    async with aiohttp.ClientSession() as session:
        for hook in hooks:
            events = evaluate_conditions(hook["conditions"], current_snapshot, previous)
            if not events:
                continue

            payload = {
                "username": username,
                "webhook_id": hook["id"],
                "events": events,
                "snapshot": current_snapshot,
            }

            try:
                async with session.post(hook["url"], json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status < 400:
                        fired += 1
                    else:
                        logger.warning("Webhook %s returned %d", hook["id"], resp.status)
            except Exception as exc:
                logger.warning("Webhook %s delivery failed: %s", hook["id"], exc)

    return fired
