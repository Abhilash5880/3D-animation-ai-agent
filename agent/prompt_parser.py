import re
from typing import List
from agent.schemas import AnimationAction


MODIFIER_MAP = {
    "quick": {"duration_mult": 0.6},
    "quickly": {"duration_mult": 0.6},
    "slow": {"duration_mult": 1.4},
    "slowly": {"duration_mult": 1.4},
    "high": {"height": 3.5},
    "higher": {"height": 3.5},
}


def parse_prompt(prompt: str) -> List[AnimationAction]:
    prompt = prompt.lower()

    tokens = re.split(r"\bthen\b|\band\b|,", prompt)
    actions: List[AnimationAction] = []

    for token in tokens:
        token = token.strip()
        params = {}

        for word, mod in MODIFIER_MAP.items():
            if word in token:
                params.update(mod)

        if "jump" in token:
            actions.append(
                AnimationAction(type="jump", params=params)
            )

        elif "wave" in token:
            actions.append(
                AnimationAction(type="wave", params=params)
            )

    return actions
