import threading
from modules.workflow import run_test_workflow

def main():
    # Define the configuration paths
    # In a real scenario, you might have different YAMLs for different environments
    config_file = "config/api_config.yaml"
    test_data_file = "config/test_case_1.yaml"

    print("=== Initializing Parallel Test Execution ===")

    # Create multiple threads to satisfy the parallelism requirement
    # Each thread represents an isolated test execution
    thread1 = threading.Thread(target=run_test_workflow, args=(config_file, test_data_file))
    thread2 = threading.Thread(target=run_test_workflow, args=(config_file, test_data_file))

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for both threads to complete before finishing the script
    thread1.join()
    thread2.join()

    print("\n=== All Parallel Test Cases Completed ===")

if __name__ == "__main__":
    main()