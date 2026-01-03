import uuid
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class SharedState(BaseModel):
    task_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    user_request: str
    plan: List[str] = Field(default_factory=list)
    current_step_index: int = 0
    context: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING

    def update_context(self, key: str, value: Any) -> None:
        """Updates the context dictionary with a new key-value pair."""
        self.context[key] = value

    def get_current_step(self) -> Optional[str]:
        """Returns the current step from the plan based on the index."""
        if 0 <= self.current_step_index < len(self.plan):
            return self.plan[self.current_step_index]
        return None

    def mark_complete(self) -> None:
        """Marks the task as completed."""
        self.status = TaskStatus.COMPLETED
