"""Executes a job's predefined task and packages the result for the /jobs/{id}/result API."""
import importlib
import time

TASK_MODULES = {
    "CPU_TEST": "tasks.cpu_task",
    "MEMORY_TEST": "tasks.memory_task",
    "SLEEP_TEST": "tasks.sleep_task",
    "FILE_PROCESSING": "tasks.file_task",
    "NETWORK_CHECK": "tasks.network_task",
    "RANDOM_FAILURE": "tasks.failure_task",
}


def execute(task_type: str) -> dict:
    module_name = TASK_MODULES.get(task_type)
    start = time.time()

    if not module_name:
        return {
            "status": "FAILED",
            "exit_code": 1,
            "output": None,
            "error": f"Unknown task type: {task_type}",
            "execution_time": round(time.time() - start, 2),
        }

    try:
        module = importlib.import_module(module_name)
        output = module.run()
        return {
            "status": "COMPLETED",
            "exit_code": 0,
            "output": str(output),
            "error": None,
            "execution_time": round(time.time() - start, 2),
        }
    except Exception as exc:
        return {
            "status": "FAILED",
            "exit_code": 1,
            "output": None,
            "error": str(exc),
            "execution_time": round(time.time() - start, 2),
        }
