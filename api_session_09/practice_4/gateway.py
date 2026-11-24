import hashlib
import logging

from datetime import datetime, timezone
from flask import request

from handler import v1_create_order, v2_create_order

# Tỷ lệ traffic thông thường được chuyển sang v2
V2_PERCENT = 5

# Các cohort được ưu tiên chuyển sang v2
V2_COHORTS = {"beta", "internal"}

# Các account luôn được chuyển sang v2
V2_FORCE_ACCOUNTS = {"acct_42", "acct_99"}

# Thời điểm sunset v1.
# Ban đầu để None.
# Chỉ thiết lập ngày sau khi rollout lên 100%.
V1_SUNSET_AT = datetime(2026, 10, 1, 23, 59, 59, tzinfo=timezone.utc)

log = logging.getLogger("gateway")

def route_to_v2(body):
    # 1. Explicit cohort has highest priority
    cohort = request.headers.get("X-Cohort", "").lower()

    if cohort in V2_COHORTS:
        log.info("Routing to v2: cohort=%s", cohort)
        return True

    # 2. Account allow-list
    acct = body.get("account_id", "")

    if acct in V2_FORCE_ACCOUNTS:
        log.info("Routing to v2: allow-listed account=%s", acct)
        return True

    # 3. Deterministic percentage bucket
    if V2_PERCENT <= 0:
        return False

    if V2_PERCENT >= 100:
        return True

    h = int(hashlib.md5(acct.encode()).hexdigest(), 16)

    bucket = h % 100

    log.info(
        "Account=%s, bucket=%s, V2_PERCENT=%s",
        acct,
        bucket,
        V2_PERCENT
    )

    return bucket < V2_PERCENT


def dispatch(body):
    # Sau Sunset: chuyển toàn bộ traffic sang v2
    if V1_SUNSET_AT is not None:
        now = datetime.now(timezone.utc)

        if now >= V1_SUNSET_AT:
            log.info("v1 has been sunset. Force routing to v2.")
            return "v2", v2_create_order(body)

    # Trước Sunset: thực hiện routing bình thường
    if route_to_v2(body):
        return "v2", v2_create_order(body)

    return "v1", v1_create_order(body)
