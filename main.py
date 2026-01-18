import threading
import time
import re
from modules.workflow import run_test_workflow

# ANSI Color Codes
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

print_lock = threading.Lock()

class IndentedLogger:
    def __init__(self, thread_name, color, indent_level=0):
        self.thread_name = thread_name
        self.color = color
        # 50 spaces of padding for Thread 2
        self.padding = " " * 50 if indent_level > 0 else ""

    def log(self, message):
        """
        Prints messages with thread-specific color and indentation.
        """
        # 1. Strip Rich tags like [bold] or [cyan]
        clean_msg = re.sub(r'\[/?[a-z]+\s?[a-z]*\]', '', str(message))
        clean_msg = clean_msg.replace("[/]", "")

        with print_lock:
            # Structure: [PADDING] [COLOR] [THREAD-NAME] MESSAGE [RESET]
            print(f"{self.padding}{self.color}[{self.thread_name}] {clean_msg}{RESET}")

def main():
    config_file = "config/api_config.yaml"
    test_data_file = "config/test_case_1.yaml"

    print(f"{BOLD}=== Initializing Indented Parallel Execution ==={RESET}")
    print(f"{CYAN}THREAD-1 (Left){RESET}" + (" " * 35) + f"{YELLOW}THREAD-2 (Indented){RESET}\n")

    # Thread 1: No Indent, Cyan
    logger1 = IndentedLogger("THREAD-1", CYAN, indent_level=0)
    
    # Thread 2: 50-space Indent, Yellow
    logger2 = IndentedLogger("THREAD-2", YELLOW, indent_level=1)

    # Initialize Threads
    thread1 = threading.Thread(target=run_test_workflow, args=(config_file, test_data_file, logger1.log))
    thread2 = threading.Thread(target=run_test_workflow, args=(config_file, test_data_file, logger2.log))

    # Start
    thread1.start()
    thread2.start()

    # Wait
    thread1.join()
    thread2.join()

    print(f"\n{BOLD}=== All Parallel Test Cases Completed ==={RESET}")

if __name__ == "__main__":
    main()