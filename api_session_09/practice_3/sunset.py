from datetime import datetime, timezone
from email.utils import format_datetime
from functools import wraps

from flask import request, jsonify

import logging

log = logging.getLogger("sunset")


# Chuyển datetime sang HTTP-date
def http_date(dt):
    return format_datetime(dt, usegmt=True)


# Decorator xử lý API hết hạn
def deprecate_at(
    sunset_date,
    replacement=None
):

    def wrap(fn):

        @wraps(fn)
        def inner(*args, **kwargs):

            now = datetime.now(timezone.utc)

            # Kiểm tra API đã hết hạn chưa
            if now >= sunset_date:

                return jsonify({
                    "error": "gone",
                    "sunset": http_date(sunset_date),
                    "use_instead": replacement
                }), 410

            # API vẫn còn hoạt động
            result = fn(*args, **kwargs)

            # Xử lý response
            body, status = (
                result
                if isinstance(result, tuple)
                else (result, 200)
            )

            response = jsonify(body)
            response.status_code = status

            # Thêm Sunset header
            response.headers["Sunset"] = (
                http_date(sunset_date)
            )

            # Thêm Deprecation header
            response.headers["Deprecation"] = "true"

            # Thêm Link header nếu có API thay thế
            if replacement:
                response.headers["Link"] = (
                    f'<{replacement}>; '
                    'rel="successor-version"'
                )

            # Ghi log
            log.warning(
                "deprecated_call %s %s",
                request.path,
                request.remote_addr
            )

            return response

        return inner

    return wrap