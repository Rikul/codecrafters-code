from ..app_logging import log
from .tool import Tool
from ..scheduled_tasks import ScheduledTasks

class ListScheduledTasks(Tool):
    
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "list_scheduled_tasks",
                "description": "List all background scheduled tasks",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        }

    @staticmethod
    def call() -> str:
        log.info("list_scheduled_tasks called")
      
        tasks = ScheduledTasks().load_tasks()
        if not tasks:
            return "No scheduled tasks found."
        
        return tasks

    
class AddScheduledTask(Tool):
    
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "add_scheduled_task",
                "description": "Add a new background scheduled task that will be executed at intervals by the background agent with your prompt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "A name for the scheduled task"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "The prompt that will be executed at intervals by the background agent"
                        },
                        "interval_minutes": {
                            "type": "integer",
                            "description": "The interval in minutes at which the background agent will execute the prompt"
                        }
                    },
                    "required": ["name", "prompt", "interval_minutes"]
                }
            }
        }

    @staticmethod
    def call(name: str, prompt: str, interval_minutes: int) -> str:
        log.info("add_scheduled_task called")
      
        tasks = ScheduledTasks()
        tasks.add_task(name=name, prompt=prompt, interval_mins=interval_minutes)

        return f"Added scheduled task '{name}' with interval {interval_minutes} minutes"
    
class RemoveScheduledTask(Tool):
    
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "remove_scheduled_task",
                "description": "Remove a background scheduled task so that it will no longer be executed by the background agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the scheduled task to remove"
                        }
                    },
                    "required": ["name"]
                }
            }
        }

    @staticmethod
    def call(name: str) -> str:
        log.info("remove_scheduled_task called")
      
        ScheduledTasks().remove_task(name)

        return f"Removed scheduled task '{name}'"
    

class DisableScheduledTask(Tool):
    
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "disable_scheduled_task",
                "description": "Disable a background scheduled task so that it will temporarily stop being executed by the background agent without being removed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the scheduled task to deactivate"
                        }
                    },
                    "required": ["name"]
                }
            }
        }

    @staticmethod
    def call(name: str) -> str:
        log.info("disable_scheduled_task called")
      
        ScheduledTasks().disable_task(name)

        return f"Disabled scheduled task '{name}'"
    

class EnableScheduledTask(Tool):
    
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "enable_scheduled_task",
                "description": "Enable a background scheduled task that was previously disabled so that it will resume being executed by the background agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the scheduled task to enable"
                        }
                    },
                    "required": ["name"]
                }
            }
        }

    @staticmethod
    def call(name: str) -> str:
        log.info("enable_scheduled_task called")
      
        ScheduledTasks().enable_task(name)  

        return f"Enabled scheduled task '{name}'"
    
class GetScheduledTaskOutput(Tool):
    
    @staticmethod
    def spec():
        return {
            "type": "function",
            "function": {
                "name": "get_scheduled_task_output",
                "description": "Get the output from a scheduled task that is executed by the background agent."
                                "This can be used to check the results of the scheduled task prompts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the scheduled task to get output for"
                        },
                        "num_entries": {
                            "type": "integer",
                            "description": "The number of recent output entries to return for the specified scheduled task (default: 5)"
                        }
                    },
                    "required": ["name"]
                }
            }
        }

    @staticmethod
    def call(name: str, num_entries: int = 5) -> str:
        log.info("get_scheduled_task_output called")
      
        tasks = ScheduledTasks()
        output = tasks.get_output(name=name, num_entries=num_entries)
    
        return output if output else f"No output found for scheduled task '{name}'"
    