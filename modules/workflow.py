# modules/workflow.py
import yaml
from modules.api_client import AviMockClient
from modules.mock_tools import mock_ssh_connect, mock_rdp_validate

def run_test_workflow(config_path, test_data_path, logger):
    """
    Executes the workflow.
    :param logger: A function that accepts a string message.
    """
    client = AviMockClient(config_path)
    
    with open(test_data_path, 'r') as file:
        test_case_data = yaml.safe_load(file)
    
    test_name = test_case_data['test_case_name']
    
    logger(f"[bold]Session:[/bold] {test_name}")
    
    # 0. Auth
    client.register()
    if not client.login():
        logger("[red]Login failed. Exiting.[/red]")
        return

    # 1. Pre-Fetcher
    logger("\n[blue][Stage 1: Pre-Fetcher][/blue]")
    tenants = client.get_resource(client.config['endpoints']['tenants'])
    v_services = client.get_resource(client.config['endpoints']['virtual_service'])
    s_engines = client.get_resource(client.config['endpoints']['service_engines'])
    
    # Extract lists safely
    ts_list = tenants.get('results', []) if isinstance(tenants, dict) else tenants
    vs_list = v_services.get('results', []) if isinstance(v_services, dict) else v_services
    se_list = s_engines.get('results', []) if isinstance(s_engines, dict) else s_engines

    logger(f"Tenants: {len(ts_list)}")
    logger(f"Virtual Svcs: {len(vs_list)}")
    logger(f"Svc Engines: {len(se_list)}")

    # 2. Pre-Validation
    logger("[blue][Stage 2: Pre-Validation][/blue]")
    target_name = test_case_data['target_vs_name']
    target_vs = next((vs for vs in vs_list if vs.get('name') == target_name), None)
    
    if not target_vs:
        logger(f"[red]Error:[/red] {target_name} not found.")
        return

    if target_vs.get('enabled') is True:
        logger(f"[green]PASS:[/green] {target_name} is ENABLED.")
    else:
        logger(f"[red]FAIL:[/red] Target is already disabled.")
        return

    # 3. Trigger
    logger("[blue][Stage 3: Task/Trigger][/blue]")
    vs_uuid = target_vs['uuid']
    client.update_vs_state(vs_uuid, enabled_status=False)
    
    # Log the mock tool output
    logger(mock_ssh_connect("192.168.1.100"))
    logger(mock_rdp_validate("192.168.1.101"))

    # 4. Post-Validation
    logger("[blue][Stage 4: Post-Validation][/blue]")
    final_data = client.get_resource(f"{client.config['endpoints']['virtual_service']}/{vs_uuid}")
    
    if final_data.get('enabled') is False:
        logger(f"[green]SUCCESS:[/green] {target_name} is DISABLED.")
    else:
        logger(f"[red]FAILURE:[/red] State did not change.")