from agent.schemas import AnimationPlan, TimedAnimationPlan, TimedAction


def build_timeline(plan: AnimationPlan) -> TimedAnimationPlan:
    current_time = 0.0
    timeline = []

    for action in plan.actions:
        start = current_time
        end = start + (action.duration or 0)

        timeline.append(
            TimedAction(
                type=action.type,
                duration=action.duration,
                start_time=start,
                end_time=end,
            )
        )

        current_time = end

    return TimedAnimationPlan(
        timeline=timeline,
        total_duration=current_time
    )
