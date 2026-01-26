from agent.schemas import AnimationPlan, TimedAnimationPlan, TimedAction

DEFAULT_DURATIONS = {
    "jump": 1.5,
    "wave": 2.0,
    "idle": 1.0,
}


def build_timeline(plan: AnimationPlan) -> TimedAnimationPlan:
    timeline = []
    current_time = 0.0

    for action in plan.actions:
        base_duration = action.duration or DEFAULT_DURATIONS[action.type]
        duration_mult = action.params.get("duration_mult", 1.0)
        duration = base_duration * duration_mult

        timed = TimedAction(
            type=action.type,
            duration=duration,
            params=action.params,
            start_time=current_time,
            end_time=current_time + duration,
        )

        timeline.append(timed)
        current_time += duration

    return TimedAnimationPlan(
        timeline=timeline,
        total_duration=current_time,
    )
