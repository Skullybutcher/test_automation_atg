import yaml
import traceback
from modules.api_client import AviMockClient
from modules.mock_tools import mock_ssh_connect, mock_rdp_validate

def run_test_workflow(config_path, test_data_path, logger):
    # Pass the logger into the client here
    client = AviMockClient(config_path, logger=logger)
    
    try:
        with open(test_data_path, 'r') as file:
            test_case_data = yaml.safe_load(file)
        
        test_name = test_case_data['test_case_name']
        logger(f"[bold white]Session:[/bold white] {test_name}")
        
        # 0. Auth
        client.register()
        if not client.login():
            return

        # 1. Pre-Fetcher
        logger("[cyan][Stage 1: Pre-Fetcher][/cyan]")
        tenants = client.get_resource(client.config['endpoints']['tenants'])
        v_services = client.get_resource(client.config['endpoints']['virtual_service'])
        s_engines = client.get_resource(client.config['endpoints']['service_engines'])
        
        # Safe Extraction
        ts_list = tenants.get('results', []) if isinstance(tenants, dict) else tenants
        vs_list = v_services.get('results', []) if isinstance(v_services, dict) else v_services
        se_list = s_engines.get('results', []) if isinstance(s_engines, dict) else s_engines

        logger(f"Tenants: {len(ts_list)} | VS: {len(vs_list)} | SE: {len(se_list)}")

        # 2. Pre-Validation
        logger("[cyan][Stage 2: Pre-Validation][/cyan]")
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
        logger("[cyan][Stage 3: Task/Trigger][/cyan]")
        vs_uuid = target_vs['uuid']
        logger(f"Disabling UUID: {vs_uuid}...")
        client.update_vs_state(vs_uuid, enabled_status=False)
        
        logger(mock_ssh_connect("192.168.1.100"))
        logger(mock_rdp_validate("192.168.1.101"))

        # 4. Post-Validation
        logger("[cyan][Stage 4: Post-Validation][/cyan]")
        final_data = client.get_resource(f"{client.config['endpoints']['virtual_service']}/{vs_uuid}")
        
        # Check raw dictionary or list safety
        if isinstance(final_data, dict) and final_data.get('enabled') is False:
            logger(f"[bold green]SUCCESS:[/bold green] {target_name} is DISABLED.")
        else:
            logger(f"[bold red]FAILURE:[/bold red] State did not change.")
            
    except Exception as e:
        # This catches any crash and prints it to the panel
        logger(f"[bold red]CRITICAL ERROR:[/bold red] {str(e)}")
        logger(traceback.format_exc())