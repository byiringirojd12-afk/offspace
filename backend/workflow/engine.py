from .task_state import TaskState


class WorkflowEngine:
    """Coordinates multi-step autonomous task execution."""

    def __init__(self):
        self.tasks = {}

    def create_task(self, task_id, goal, steps):
        task = TaskState(task_id=task_id, goal=goal, steps=steps)
        self.tasks[task_id] = task
        return task

    def run_step(self, task_id, step_result):
        task = self.tasks.get(task_id)
        if not task:
            return None

        task.results.append(step_result)
        task.update_status("running")
        return task

    def complete(self, task_id):
        task = self.tasks.get(task_id)
        if task:
            task.update_status("completed")
        return task
