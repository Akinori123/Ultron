#web_search.py
import json
import sys
import warnings
from pathlib import Path

def _get_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


BASE_DIR        = _get_base_dir()
API_CONFIG_PATH = BASE_DIR / "config" / "api_keys.json"


def _get_api_key() -> str:
    with open(API_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)["gemini_api_key"]


def _gemini_search(query: str) -> str:
    from google import genai
    # Google Search grounding is the real news engine: it reaches every major
    # Brazilian and world outlet. Ask explicitly for recent, sourced headlines
    # in Portuguese so we never answer "I couldn't find specific headlines".
    today = __import__("datetime").datetime.now().strftime("%d/%m/%Y")
    prompt = (
        f"Você é um pesquisador de notícias em tempo real. Hoje é {today}.\n"
        f"Pesquise na web AGORA e traga as notícias mais RECENTES e específicas sobre: {query}\n\n"
        "Regras:\n"
        "- Use a Busca do Google para encontrar matérias reais dos principais portais "
        "(G1, UOL, R7, CNN Brasil, Folha, Estadão, BBC Brasil, Reuters, AP, etc.), brasileiros e internacionais.\n"
        "- Traga manchetes CONCRETAS, com nomes, datas, números e o que aconteceu. Nunca diga apenas que 'há cobertura'.\n"
        "- Se o assunto for recente, priorize as últimas 24-72 horas.\n"
        "- Traga no mínimo 4 a 6 notícias distintas.\n"
        "- Responda TODO o conteúdo em português do Brasil, traduzindo qualquer fonte estrangeira.\n"
        "- Ao final, liste as fontes (nome do portal + link)."
    )

    client = genai.Client(api_key=_get_api_key())
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={"tools": [{"google_search": {}}]},
    )

    text = ""
    try:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text += part.text
    except Exception:
        pass
    if not text:
        text = (getattr(response, "text", "") or "")

    text = text.strip()
    if not text:
        raise ValueError("Gemini returned an empty response.")
    return text


def _ddg_search(query: str, max_results: int = 6) -> list[dict]:
    try:
        from ddgs import DDGS
    except ImportError:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=RuntimeWarning,
                message=r"This package .* has been renamed to .*",
            )
            from duckduckgo_search import DDGS

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title":   r.get("title",  ""),
                "snippet": r.get("body",   ""),
                "url":     r.get("href",   ""),
            })
    return results


def _format_ddg(query: str, results: list[dict]) -> str:
    if not results:
        return f"Nenhum resultado encontrado para: {query}"

    lines = [f"Resultados da busca para: {query}\n"]
    for i, r in enumerate(results, 1):
        if r.get("title"):   lines.append(f"{i}. {r['title']}")
        if r.get("snippet"): lines.append(f"   {r['snippet']}")
        if r.get("url"):     lines.append(f"   {r['url']}")
        lines.append("")
    return "\n".join(lines).strip()

def _compare(items: list[str], aspect: str) -> str:
    query = (
        f"Compare {', '.join(items)} in terms of {aspect}. "
        "Give specific facts and data."
    )
    try:
        return _gemini_search(query)
    except Exception as e:
        print(f"[WebSearch] ⚠️ Gemini compare failed: {e} — falling back to DDG")

    # DDG fallback: fetch results per item and merge
    all_results: dict[str, list] = {}
    for item in items:
        try:
            all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
        except Exception:
            all_results[item] = []

    lines = [f"Comparação — {aspect.upper()}", "─" * 40]
    for item in items:
        lines.append(f"\n▸ {item}")
        for r in all_results.get(item, [])[:2]:
            if r.get("snippet"):
                lines.append(f"  • {r['snippet']}")
    return "\n".join(lines)

def web_search(
    parameters:     dict,
    response=None,
    player=None,
    session_memory=None,
) -> str:
    params = parameters or {}
    query  = params.get("query", "").strip()
    mode   = params.get("mode",  "search").lower().strip()
    items  = params.get("items", [])
    aspect = params.get("aspect", "general").strip() or "general"

    if not query and not items:
        return "Por favor, forneça um termo de busca, senhor."

    if items and mode != "compare":
        mode = "compare"

    if player:
        player.write_log(f"[Search] {query or ', '.join(items)}")

    print(f"[WebSearch] Query: {query!r}  Mode: {mode}")
    if mode == "compare":
        try:
            result = _compare(items or ([query] if query else []), aspect)
            print("[WebSearch] Gemini compare OK.")
            return result
        except Exception as e:
            print(f"[WebSearch] Gemini compare failed ({e}) - trying DDG...")
            all_results: dict[str, list] = {}
            for item in items or ([query] if query else []):
                try:
                    all_results[item] = _ddg_search(f"{item} {aspect}", max_results=3)
                except Exception:
                    all_results[item] = []

            lines = [f"Comparação — {aspect.upper()}", "─" * 40]
            for item in items or ([query] if query else []):
                lines.append(f"\n▸ {item}")
                for r in all_results.get(item, [])[:2]:
                    if r.get("snippet"):
                        lines.append(f"  • {r['snippet']}")
            return "\n".join(lines).strip()

    # Primary: Gemini + Google Search grounding. It reaches every major Brazilian
    # and world outlet and returns concrete, dated headlines. DuckDuckGo is only a
    # fallback — it is far weaker and was the reason news searches came back empty.
    try:
        result = _gemini_search(query)
        if result and result.strip():
            if player and hasattr(player, "show_hud_deliverable"):
                try:
                    bullets = [ln.strip() for ln in result.splitlines() if len(ln.strip()) > 15][:5]
                    player.show_hud_deliverable(f"BUSCA: {query[:25].upper()}", bullets=bullets, kind="search")
                except Exception:
                    pass
            print("[WebSearch] Gemini search OK.")
            return result
        print("[WebSearch] Gemini returned empty, trying DDG...")
    except Exception as e:
        print(f"[WebSearch] Gemini search failed ({e}) - trying DDG...")

    try:
        results = _ddg_search(query)
        if results:
            if player and hasattr(player, "show_hud_operation"):
                try:
                    sources = [r.get("url") or r.get("title") for r in results[:4] if r.get("url") or r.get("title")]
                    player.show_hud_operation("WEB INTELLIGENCE", f"Retrieved {len(results)} sources for '{query[:30]}'", sources=sources, tool="SEARCH")
                except Exception:
                    pass
            result = _format_ddg(query, results)
            if player and hasattr(player, "show_hud_deliverable"):
                try:
                    bullets = [r.get("title") for r in results[:4] if r.get("title")]
                    player.show_hud_deliverable(f"BUSCA: {query[:25].upper()}", bullets=bullets, kind="search")
                except Exception:
                    pass
            print(f"[WebSearch] DDG OK: {len(results)} result(s).")
            return result
        return f"Nenhum resultado encontrado para: {query}"
    except Exception as e:
        return f"Falha na busca: {e}"
