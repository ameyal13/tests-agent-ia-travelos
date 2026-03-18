# El orquestador no llama al LLM directamente.
# Su lógica está en orchestrator.py usando LangGraph.
# Este archivo existe por consistencia con la estructura
# y puede usarse en el futuro para prompts de validación.

ORCHESTRATOR_ERROR_MSG = """
Ocurrió un error durante el procesamiento del viaje.
Por favor intenta de nuevo o contacta soporte.
"""