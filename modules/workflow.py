import yaml
from modules.api_client import AviMockClient
from modules.mock_tools import mock_ssh_connect, mock_rdp_validate

def run_test_workflow(config_path, test_data_path):
    # Initialize the client with the main API config
    client = AviMockClient(config_path)
    
    # Load the specific test case data dynamically 
    with open(test_data_path, 'r') as file:
        test_case_data = yaml.safe_load(file)
    
    # 0. Preparation: Register and Login
    print(f"--- Starting Session for {config_path} ---")
    client.register()
    if not client.login():
        print("Login failed. Exiting workflow.")
        return

    # 1. Pre-Fetcher Stage
    # Fetch all tenants, virtual services, and service engines from mock API 
    print("\n[Stage 1: Pre-Fetcher]")
    tenants = client.get_resource(client.config['endpoints']['tenants'])
    v_services = client.get_resource(client.config['endpoints']['virtual_service'])
    s_engines = client.get_resource(client.config['endpoints']['service_engines'])
    
    # Log the counts as part of the pre-fetch stage [cite: 35, 119]
    print(f"Tenants found: {len(tenants)}")
    print(f"Virtual Services found: {len(v_services)}")
    print(f"Service Engines found: {len(s_engines)}")

    # 2. Pre-Validation Stage
    print("\n[Stage 2: Pre-Validation]")
    target_vs_name = test_case_data['target_vs_name'] 
    
    # Identify specific Virtual Service 
    target_vs = next((vs for vs in v_services if vs['name'] == target_vs_name), None)
    
    if not target_vs:
        print(f"Error: Target VS {target_vs_name} not found.")
        return

    # Validate that "enabled": true before proceeding [cite: 40, 121]
    if target_vs.get('enabled') is True:
        print(f"Validation Passed: {target_vs_name} is ENABLED.")
    else:
        print(f"Validation Failed: {target_vs_name} is already disabled. Stopping.")
        return

    # 3. Task/Trigger Stage
    print("\n[Stage 3: Task/Trigger]")
    # Convert VS endpoint to a PUT request using the UUID [cite: 43, 123]
    vs_uuid = target_vs['uuid']
    print(f"Disabling Virtual Service (UUID: {vs_uuid})...")
    
    # Send payload {"enabled": false} to disable the VS [cite: 44, 124]
    update_result = client.update_vs_state(vs_uuid, enabled_status=False)
    
    # Trigger mock components [cite: 27, 113]   
    mock_ssh_connect("192.168.1.100")
    mock_rdp_validate("192.168.1.101")

    # 4. Post-Validation Stage
    print("\n[Stage 4: Post-Validation]")
    # Verify that the Virtual Service is now disabled [cite: 47, 127]
    final_vs_data = client.get_resource(f"{client.config['endpoints']['virtual_service']}/{vs_uuid}")
    
    if final_vs_data.get('enabled') is False:
        print(f"SUCCESS: {target_vs_name} is now DISABLED.")
    else:
        print(f"FAILURE: {target_vs_name} state did not change.")