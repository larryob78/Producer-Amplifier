"""VFX trigger keyword scanning with false-positive filtering."""

from __future__ import annotations

import re

from sba.parsing.models import VFXTrigger

# Each category has keyword patterns and false-positive exclusion patterns
VFX_TRIGGER_TAXONOMY: dict[str, dict] = {
    "water": {
        "keywords": [
            r"\bocean\b",
            r"\bsea\b",
            r"\briver\b",
            r"\blake\b",
            r"\bpool\b",
            r"\bflood(?:ing|ed|s)?\b",
            r"\bunderwater\b",
            r"\bswim(?:s|ming)?\b",
            r"\bdive[sd]?\b",
            r"\bwave[sd]?\b",
            r"\btsunami\b",
            r"\bsplash(?:es|ing)?\b",
            r"\bsubmerg(?:ed|es|ing)?\b",
            r"\bdrown(?:s|ing|ed)?\b",
        ],
        "exclusions": [
            r"water\s*(?:bottle|glass|cup|cooler|proof|tight|color|mark)",
        ],
        "severity": "high",
    },
    "fire_pyro": {
        "keywords": [
            r"\bflame[sd]?\b",
            r"\bburn(?:s|ing|ed)?\b",
            r"\bexplo(?:sion|de[sd]?|ding)\b",
            r"\bblast\b",
            r"\binferno\b",
            r"\bblaze[sd]?\b",
            r"\bignite[sd]?\b",
            r"\bsmoke\b",
            r"\bspark[sd]?\b",
            r"\bdetonate[sd]?\b",
            r"\bgunfire\b",
            r"\bmuzzle\s*flash\b",
            r"\bfireball\b",
        ],
        "exclusions": [
            r"fire[sd]\s+(?:from|him|her|them|the\s+employee|a\s+question|off\s+an?\s+email)",
            r"fire\s*(?:place|house|fighter|truck|man|men|woman|station|chief|escape|exit|drill|alarm|hydrant|department)",
            r"\bcamp\s*fire\b",
        ],
        "severity": "high",
    },
    "crowds_extras": {
        "keywords": [
            r"\bcrowd[sd]?\b",
            r"\bmob\b",
            r"\bhorde\b",
            r"\bhundreds\b",
            r"\bthousands\b",
            r"\barm(?:y|ies)\b",
            r"\bsoldier[sd]?\b",
            r"\btroop[sd]?\b",
            r"\briot(?:s|ing|ers?)?\b",
            r"\bstampede\b",
            r"\bparade\b",
            r"\bstadium\b",
        ],
        "exclusions": [],
        "severity": "medium",
    },
    "vehicles": {
        "keywords": [
            r"\bcar\s+(?:chase|crash|wreck|flip|roll)\b",
            r"\bhelicopter\b",
            r"\bchopper\b",
            r"\baircraft\b",
            r"\bjet\b",
            r"\bspacecraft\b",
            r"\bspaceship\b",
            r"\bsubmarine\b",
            r"\btrain\b.*\b(?:crash|wreck|derail)\b",
            r"\bcrash(?:es|ing|ed)?\b",
            r"\bcollision\b",
        ],
        "exclusions": [
            r"tank\s*(?:top|of\s+gas)",
        ],
        "severity": "medium",
    },
    "creatures_animals": {
        "keywords": [
            r"\bmonster[sd]?\b",
            r"\bcreature[sd]?\b",
            r"\balien[sd]?\b",
            r"\bdragon[sd]?\b",
            r"\bdinosaur[sd]?\b",
            r"\bzombie[sd]?\b",
            r"\bwolf\b",
            r"\bwolves\b",
            r"\bmutant[sd]?\b",
            r"\bdemon[sd]?\b",
            r"\bghost[sd]?\b",
            r"\bwerewolf\b",
            r"\bvampire[sd]?\b",
        ],
        "exclusions": [
            r"bear\s+(?:with|in\s+mind)",
            r"horse\s*(?:play|power|shoe|around)",
        ],
        "severity": "high",
    },
    "destruction": {
        "keywords": [
            r"\bcollaps(?:e[sd]?|ing)\b",
            r"\bdemolish\b",
            r"\bdestroy(?:s|ed|ing)?\b",
            r"\bdestruction\b",
            r"\bearthquake\b",
            r"\btornado\b",
            r"\bhurricane\b",
            r"\bavalanch\b",
            r"\bshatter(?:s|ed|ing)?\b",
            r"\bcrumbl(?:e[sd]?|ing)\b",
        ],
        "exclusions": [],
        "severity": "high",
    },
    "weapons_combat": {
        "keywords": [
            r"\bgun[sd]?\b",
            r"\bpistol\b",
            r"\brifle\b",
            r"\bshotgun\b",
            r"\bshoot(?:s|ing|out)?\b",
            r"\bsword[sd]?\b",
            r"\blightsaber[sd]?\b",
            r"\bbattle\b",
            r"\bblaster[sd]?\b",
        ],
        "exclusions": [
            r"gun\s*(?:metal|powder\s+grey)",
        ],
        "severity": "medium",
    },
    "aerial_height": {
        "keywords": [
            r"\bfly(?:s|ing)?\b",
            r"\bflight\b",
            r"\bsoar(?:s|ing)?\b",
            r"\bhover(?:s|ing)?\b",
            r"\bparachute\b",
            r"\bskydiv(?:e|ing)\b",
        ],
        "exclusions": [
            r"flight\s+(?:of\s+stairs|attendant|delay)",
        ],
        "severity": "high",
    },
    "weather_atmosphere": {
        "keywords": [
            r"\bstorm(?:s|ing|y)?\b",
            r"\blightning\b",
            r"\bthunder\b",
            r"\bsnow(?:s|ing|storm)?\b",
            r"\bblizzard\b",
            r"\bfog(?:gy)?\b",
            r"\bmist(?:y)?\b",
        ],
        "exclusions": [
            r"\bbrain\b",
        ],
        "severity": "medium",
    },
    "supernatural_magic": {
        "keywords": [
            r"\bmagic\b",
            r"\bspell[sd]?\b",
            r"\bteleport\b",
            r"\bvanish(?:es|ed|ing)?\b",
            r"\btransform(?:s|ing|ation)?\b",
            r"\blevitat(?:e[sd]?|ing|ion)\b",
            r"\bforce[\s-]?field\b",
            r"\bportal[sd]?\b",
            r"\bsupernatural\b",
            r"\b(?:the\s+)?force\b",
        ],
        "exclusions": [
            r"force[sd]?\s+(?:him|her|them|to|into|out)",
            r"(?:air|task|work|police|armed)\s+force",
        ],
        "severity": "high",
    },
}


def scan_for_vfx_triggers(text: str) -> list[VFXTrigger]:
    """Scan text for VFX trigger keywords with false-positive filtering."""
    triggers: list[VFXTrigger] = []

    for category, config in VFX_TRIGGER_TAXONOMY.items():
        for pattern_str in config["keywords"]:
            pattern = re.compile(pattern_str, re.IGNORECASE)
            for match in pattern.finditer(text):
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end].strip()

                # Check false-positive exclusions
                is_false_positive = False
                for excl in config.get("exclusions", []):
                    if re.search(excl, context, re.IGNORECASE):
                        is_false_positive = True
                        break

                if not is_false_positive:
                    triggers.append(
                        VFXTrigger(
                            category=category,
                            matched_keyword=match.group(0),
                            severity=config["severity"],
                            context=context,
                            position=match.start(),
                        )
                    )

    return triggers
