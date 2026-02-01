"""
Rate Limit Probe Utility

This script checks whether you are currently rate-limited by the GitHub Models API.

- Loads your GitHub Models token from a `.env` file (expected in the same folder you run this from)
- Sends a minimal request to avoid burning tokens
- Prints rate limit status and helpful timing info if limited

Usage:
    python rate_limit_probe.py
"""

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from openai import OpenAI

BASE_URL = "https://models.github.ai/inference"
MODEL = "openai/gpt-4o"


def to_utc_iso(epoch_seconds: str) -> str:
    """Convert epoch seconds to an ISO 8601 UTC string."""
    dt = datetime.fromtimestamp(int(epoch_seconds), tz=timezone.utc)
    return dt.isoformat()


def pretty_wait(seconds: int) -> str:
    """Format seconds as a human-friendly wait time."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}h {minutes}m {secs}s"


def main() -> None:
    """Probe the GitHub Models API for rate limit status."""
    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise SystemExit(
            "Missing GITHUB_TOKEN. Add it to a .env file in this folder:\n"
            "GITHUB_TOKEN=your_token_here"
        )

    client = OpenAI(api_key=token, base_url=BASE_URL)

    try:
        # Keep it tiny to avoid burning tokens/requests.
        client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5,
            temperature=0,
        )
        print("✅ Request succeeded (not rate-limited right now).")
        return

    except Exception as exc:
        resp = getattr(exc, "response", None)

        print("❌ Request failed.")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error: {exc}")

        if resp is None:
            print(
                "\n(No HTTP response object found on the exception, so headers "
                "like Retry-After may not be available in this SDK/version.)"
            )
            return

        headers = resp.headers

        print("\n--- Rate limit / retry headers (if present) ---")
        retry_after = headers.get("retry-after")
        remaining = headers.get("x-ratelimit-remaining")
        reset = headers.get("x-ratelimit-reset")
        limit = headers.get("x-ratelimit-limit")

        status = getattr(resp, "status_code", "unknown")
        print("status:", status)
        print("retry-after:", retry_after)
        print("x-ratelimit-remaining:", remaining)
        print("x-ratelimit-limit:", limit)
        print("x-ratelimit-reset:", reset)

        if retry_after:
            try:
                seconds = int(float(retry_after))
                ready_at_local = datetime.now() + timedelta(seconds=seconds)
                print("\n--- Retry-After interpretation ---")
                print("wait:", pretty_wait(seconds))
                print("ready_at (local):", ready_at_local.strftime("%Y-%m-%d %H:%M:%S"))
            except (ValueError, TypeError) as parse_err:
                print(f"\n(Could not parse Retry-After value: {parse_err})")

        if reset:
            try:
                print("reset (UTC):", to_utc_iso(reset))
            except (ValueError, TypeError) as parse_err:
                print(f"(Could not parse x-ratelimit-reset value: {parse_err})")


if __name__ == "__main__":
    main()
