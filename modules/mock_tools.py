# modules/mock_tools.py

def mock_ssh_connect(host):
    return f"MOCK_SSH: Connected to {host} (Secure)"

def mock_rdp_validate(host):
    return f"MOCK_RDP: Validated connection to {host}"