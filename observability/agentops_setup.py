import os

def init_agentops():
    api_key = os.getenv("AGENTOPS_API_KEY")
    if not api_key:
        print("AGENTOPS_API_KEY not found. Skipping AgentOps observability setup.")
        return False
    try:
        import agentops
        agentops.init(api_key=api_key)
        print("AgentOps successfully initialized.")
        return True
    except Exception as e:
        print(f"Failed to initialize AgentOps: {e}")
        return False
