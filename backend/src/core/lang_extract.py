from __future__ import annotations
from typing import Iterable, Dict, Any, List, Optional
import os
import langextract as lx
from rapidfuzz import process, fuzz

# ---- Canonical vocab you care about ----
CANON_EFFECTS = ["Bleeding", "Burning", "Poisoned", "Blinded", "Rooted", "Asleep"]
CANON_WEATHERS = ["Cleansing Rain", "Arcane Winds", "Scorched Earth", "Sunlight", "Darkness", "Blizzard", "Sandstorm"]
CANON_DAMAGE_TYPES = [
    "Humanoid","Beast","Flying","Mechanical","Undead",
    "Dragonkin","Elemental","Magic","Aquatic","Critter"
]

PROMPT = """
Extract pet battle mechanics from the text.

Rules:
- Use exact text spans from the input when possible.
- Do not paraphrase extraction_text.
- Do not overlap spans.
- If an effect is implied (e.g., “count as Burning”), include that effect.
- If weather is created or referenced, extract it.
- If a damage type is mentioned (e.g., “Elemental damage”), extract it.

Schema (extraction_class → attributes):
- effect: attributes = {"name": one of [Bleeding, Burning, Poisoned, Blinded, Rooted, Asleep]}
- weather: attributes = {"name": string in known weathers if present}
- damage: attributes = {"type": one of damage types, "value": optional integer if present}

Return multiple extractions per text when appropriate.
"""

def _examples() -> List[lx.data.ExampleData]:
    # A few, clear few-shot examples to steer the model
    return [
        lx.data.ExampleData(
            text=(
                "Arcane Storm: Prevents pets from being stunned or rooted. "
                "Turns the weather to Arcane Winds for 5 rounds."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="effect",
                    extraction_text="rooted",
                    attributes={"name": "Rooted"},
                ),
                lx.data.Extraction(
                    extraction_class="weather",
                    extraction_text="Arcane Winds",
                    attributes={"name": "Arcane Winds"},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "Scorched Earth: Causes all pets to be considered Burning and take Dragonkin damage."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="effect",
                    extraction_text="Burning",
                    attributes={"name": "Burning"},
                ),
                lx.data.Extraction(
                    extraction_class="damage",
                    extraction_text="Dragonkin damage",
                    attributes={"type": "Dragonkin"},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "Cleansing Rain: Reduces duration of damage over time effects and boosts Aquatic abilities."
            ),
            extractions=[
                # No specific canonical status, but weather modifier exists; keep it as weather name if relevant
                lx.data.Extraction(
                    extraction_class="weather",
                    extraction_text="Cleansing Rain",
                    attributes={"name": "Cleansing Rain"},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "Sunlight: Strikes enemies with Elemental damage and creates a Sunny Day weather effect."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="damage",
                    extraction_text="Elemental damage",
                    attributes={"type": "Elemental"},
                ),
                lx.data.Extraction(
                    extraction_class="weather",
                    extraction_text="Sunlight",
                    attributes={"name": "Sunlight"},
                ),
            ],
        ),
        lx.data.ExampleData(
            text=(
                "Builds a turret that assaults the enemy team's front pet, dealing 9 Mechanical damage each round."
            ),
            extractions=[
                lx.data.Extraction(
                    extraction_class="damage",
                    extraction_text="Mechanical damage",
                    attributes={"type": "Mechanical"},
                ),
            ],
        ),
    ]

def _normalize_label(label: str, canon: List[str], cutoff: int = 80) -> Optional[str]:
    """Map free text to a canonical label with fuzzy matching."""
    res = process.extractOne(label, canon, scorer=fuzz.WRatio, score_cutoff=cutoff)
    return res[0] if res else None

def extract_for_ability(
    text: str,
    model_id: str = "gemini-2.5-flash",
    api_key: Optional[str] = None,
    use_ollama: bool = False,
    model_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Run LangExtract on a single ability description/name blob and return structured fields.

    Returns:
        {
          "effects": ["Burning", ...],
          "weathers": ["Arcane Winds", ...],
          "damage_types": ["Mechanical", "Dragonkin", ...],
          "spans": [{"class":"effect","text":"Burning","start":..., "end":...}, ...]
        }
    """
    # Prefer env var for Gemini/OpenAI if not explicitly passed
    api_key = api_key or os.environ.get("LANGEXTRACT_API_KEY")

    kwargs = dict(
        text_or_documents=text,
        prompt_description=PROMPT,
        examples=_examples(),
        model_id=model_id,
    )

    # Provider-specific flags
    if use_ollama:
        kwargs.update(dict(model_url=model_url or "http://localhost:11434",
                           fence_output=False, use_schema_constraints=False))
    elif "gpt-" in model_id or model_id.startswith("o"):
        # OpenAI family
        kwargs.update(dict(api_key=os.environ.get("OPENAI_API_KEY"),
                           fence_output=True, use_schema_constraints=False))
    else:
        # Gemini family (recommended)
        if api_key:
            kwargs.update(dict(api_key=api_key))

    result = lx.extract(**kwargs)

    effects: List[str] = []
    weathers: List[str] = []
    damage_types: List[str] = []
    spans: List[Dict[str, Any]] = []

    # result.extractions is a list of lx.data.Extraction
    for ex in getattr(result, "extractions", []) or []:
        cls = ex.extraction_class or ""
        attrs = ex.attributes or {}
        spans.append({
            "class": cls,
            "text": ex.extraction_text,
            "start": getattr(ex, "start_char", None),
            "end": getattr(ex, "end_char", None),
        })

        if cls == "effect":
            name = attrs.get("name") or ex.extraction_text
            norm = _normalize_label(name, CANON_EFFECTS, cutoff=75)
            if norm:
                effects.append(norm)
        elif cls == "weather":
            name = attrs.get("name") or ex.extraction_text
            norm = _normalize_label(name, CANON_WEATHERS, cutoff=70)
            if norm:
                weathers.append(norm)
        elif cls == "damage":
            dtype = attrs.get("type") or ex.extraction_text
            norm = _normalize_label(dtype, CANON_DAMAGE_TYPES, cutoff=70)
            if norm:
                damage_types.append(norm)

    # Deduplicate while keeping order
    def _dedup(seq: List[str]) -> List[str]:
        seen = set(); out=[]
        for s in seq:
            if s not in seen:
                seen.add(s); out.append(s)
        return out

    return {
        "effects": _dedup(effects),
        "weathers": _dedup(weathers),
        "damage_types": _dedup(damage_types),
        "spans": spans,
    }
