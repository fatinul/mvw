import json
import re
import requests
from bs4 import BeautifulSoup

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.google.com",
}


def _debug_print(msg: str, debug: bool):
    if debug:
        print(f"  [RT DEBUG] {msg}")


def _parse_movie_page(content: str, debug: bool = False) -> dict:
    """Parse a RT movie page and return scores + review counts."""
    soup = BeautifulSoup(content, "html.parser")
    data = {
        "tomatometer": None,
        "audience_score": None,
        "critic_reviews": None,
        "audience_reviews": None,
    }

    # 1. Primary Method: Extract directly from the embedded media-scorecard JSON script
    scorecard_script = soup.find("script", id="media-scorecard-json")

    if scorecard_script and scorecard_script.string:
        try:
            json_data = json.loads(scorecard_script.string)

            # Tomatometer score
            critics_score = json_data.get("criticsScore", {}).get("score")
            if critics_score is not None:
                data["tomatometer"] = int(critics_score)
                _debug_print(f"Tomatometer: {data['tomatometer']}%", debug)

            # Critic review count
            critics_count = json_data.get("criticsScore", {}).get("reviewCount")
            if critics_count is not None:
                data["critic_reviews"] = int(critics_count)
                _debug_print(f"Critic reviews: {data['critic_reviews']}", debug)

            # Audience / Popcornmeter score
            audience_score = json_data.get("audienceScore", {}).get("score")
            if audience_score is not None:
                data["audience_score"] = int(audience_score)
                _debug_print(f"Audience score: {data['audience_score']}%", debug)

            # Audience review count
            audience_count = json_data.get("audienceScore", {}).get(
                "reviewCount"
            )
            if audience_count is not None:
                data["audience_reviews"] = int(audience_count)
                _debug_print(
                    f"Audience reviews: {data['audience_reviews']}", debug
                )

            return data

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            _debug_print(f"Failed to parse media-scorecard-json: {e}", debug)

    else:
        _debug_print("script[id=media-scorecard-json] not found", debug)

    # 2. Fallback Method: Inspect custom Web Component attributes if JSON fails
    score_board = soup.find("media-scorecard") or soup.find("score-board")
    if score_board:
        _debug_print("Attempting fallback using Web Component attributes", debug)

        def _safe_int(attr_name: str) -> int | None:
            val = score_board.get(attr_name)
            if val:
                nums = re.findall(r"\d+", str(val))
                if nums:
                    return int(nums[0])
            return None

        data["tomatometer"] = _safe_int("critics-score")
        data["critic_reviews"] = _safe_int("critics-count")
        data["audience_score"] = _safe_int("audience-score")
        data["audience_reviews"] = _safe_int("audience-count")

        _debug_print(f"Fallback extracted: {data}", debug)

    return data


def _derive_certification(
    tomatometer: int | None, critic_reviews: int | None
) -> str | None:
    """Derive certification status from tomatometer score and review count."""
    if tomatometer is None:
        return None
    if tomatometer >= 75 and (critic_reviews or 0) >= 80:
        return "Certified Fresh"
    if tomatometer >= 60:
        return "Fresh"
    return "Rotten"


def normalize_review_count(count: int | None) -> str:
    """Normalize review count for display: 1234 -> '1,234', 10234 -> '10K+'."""
    if count is None:
        return "N/A"
    if count >= 10_000:
        return f"{count // 1_000}K+"
    return f"{count:,}"


def fetch_rotten_tomatoes_data(
    title: str,
    year: str,
    tomato_url: str | None = None,
    debug: bool = False,
) -> dict | None:
    """Fetch RT data by scraping the Rotten Tomatoes movie page."""
    _debug_print("=== RT Fetch Start ===", debug)
    _debug_print(f"Title: {title}", debug)
    _debug_print(f"Year: {year}", debug)
    _debug_print(f"tomato_url: {tomato_url}", debug)

    if not tomato_url:
        _debug_print("No tomato_url provided, skipping", debug)
        _debug_print("=== RT Fetch End (skipped) ===", debug)
        return None

    try:
        _debug_print(f"Fetching RT page: {tomato_url}", debug)
        resp = requests.get(tomato_url, headers=REQUEST_HEADERS, timeout=15)
        _debug_print(f"RT page response status: {resp.status_code}", debug)
        _debug_print(f"RT page response length: {len(resp.text)} chars", debug)
        resp.raise_for_status()

        scores = _parse_movie_page(resp.text, debug=debug)
        certification = _derive_certification(
            scores["tomatometer"], scores["critic_reviews"]
        )
        _debug_print(f"Derived certification: {certification}", debug)

        if scores["tomatometer"] is None and scores["audience_score"] is None:
            _debug_print("No RT scores found, returning None", debug)
            _debug_print("=== RT Fetch End (no data) ===", debug)
            return None

        result = {
            "rt_tomatometer": scores["tomatometer"],
            "rt_audience_score": scores["audience_score"],
            "rt_certification": certification,
            "rt_critic_reviews": scores["critic_reviews"],
            "rt_audience_reviews": scores["audience_reviews"],
        }
        _debug_print(f"Final result: {result}", debug)
        _debug_print("=== RT Fetch End ===", debug)
        return result

    except Exception as e:
        _debug_print(f"EXCEPTION: {type(e).__name__}: {e}", debug)
        _debug_print("=== RT Fetch End (failed) ===", debug)
        return None