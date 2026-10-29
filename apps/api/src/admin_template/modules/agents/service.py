def list_agents():
    return []

def register_agent(url, token=None):
    return {"url": url, "token": token}

def health_check(agent):
    return True

def register_agent_record(url, token=None):
    return {"url": url, "token": token}

def health_check_agent(agent):
    return True
