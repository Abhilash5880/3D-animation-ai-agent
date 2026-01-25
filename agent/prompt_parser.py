from agent.schemas import AnimationPlan, AnimationAction


HEIGHT_MAP = {
    "small": 1.5,
    "low": 1.5,
    "normal": 2.0,
    "high": 3.5,
    "big": 3.5
}

WAVE_SPEED_MAP = {
    "slow": 0.5,
    "normal": 1.0,
    "fast": 1.5
}


def parse_prompt(prompt: str) -> AnimationPlan:
    prompt = prompt.lower()
    actions = []

    # ---- WAVE ----
    if "wave" in prompt:
        params = {
            "speed": "normal",
            "intensity": 1.0
        }

        if "slow" in prompt:
            params["speed"] = "slow"
        elif "fast" in prompt:
            params["speed"] = "fast"

        if "gentle" in prompt:
            params["intensity"] = 0.5
        elif "energetic" in prompt:
            params["intensity"] = 1.5

        actions.append(
            AnimationAction(
                type="wave",
                duration=2.0,
                params=params
            )
        )

    # ---- JUMP ----
    if "jump" in prompt:
        height = 2.0
        for keyword, value in HEIGHT_MAP.items():
            if keyword in prompt:
                height = value
                break

        actions.append(
            AnimationAction(
                type="jump",
                duration=1.5,
                params={
                    "height": height
                }
            )
        )

    # ---- FALLBACK ----
    if not actions:
        actions.append(
            AnimationAction(
                type="idle",
                duration=2.0,
                params={}
            )
        )

    return AnimationPlan(actions=actions)
