from pydantic import BaseModel
from typing import List, Literal, Optional, Dict, Any


class AnimationAction(BaseModel):
    type: Literal["wave", "jump", "idle"]
    duration: Optional[float] = None
    params: Dict[str, Any] = {}


class AnimationPlan(BaseModel):
    actions: List[AnimationAction]


class TimedAction(AnimationAction):
    start_time: float
    end_time: float


class TimedAnimationPlan(BaseModel):
    timeline: List[TimedAction]
    total_duration: float
