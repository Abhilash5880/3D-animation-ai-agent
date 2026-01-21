from agent.schemas import AnimationPlan, AnimationAction


def parse_prompt(prompt: str) -> AnimationPlan:
    prompt = prompt.lower()
    actions = []

    if "wave" in prompt:
        actions.append(AnimationAction(type="wave", duration=2.0))

    if "jump" in prompt:
        actions.append(AnimationAction(type="jump", duration=1.5))

    if not actions:
        actions.append(AnimationAction(type="idle", duration=2.0))

    return AnimationPlan(actions=actions)
