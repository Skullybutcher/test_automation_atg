import threading
import queue
import re
import time
from modules.workflow import run_test_workflow

# --- Configuration ---
# ANSI Color Codes for terminal output
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

# 1. The Shared Event Queue
# This queue acts as the buffer between fast workers and the slow screen.
log_queue = queue.Queue()

# --- The Dedicated Printer Thread ---
def printer_daemon():
    """
    Runs in the background. Constantly checks the queue for new messages
    and prints them immediately.
    """
    while True:
        # Get the next message (blocks until one is available)
        message = log_queue.get()
        
        # Check for the "Sentinel" (a signal to stop)
        if message is None:
            break
            
        # Print the message
        print(message)
        
        # Mark task as done
        log_queue.task_done()

# --- The Logger Class (Producer) ---
class AsyncLogger:
    def __init__(self, thread_name, color, indent_level=0):
        self.thread_name = thread_name
        self.color = color
        # Calculate padding: 50 spaces for the second thread
        self.padding = " " * 50 if indent_level > 0 else ""

    def log(self, message):
        """
        Formats the message and pushes it to the queue.
        Does NOT print directly. Returns immediately.
        """
        # 1. Clean up Rich tags like [bold] or [cyan]
        clean_msg = re.sub(r'\[/?[a-z]+\s?[a-z]*\]', '', str(message))
        clean_msg = clean_msg.replace("[/]", "")

        # 2. Format the final string
        # Structure: [PADDING] [COLOR] [THREAD-NAME] MESSAGE [RESET]
        formatted_message = f"{self.padding}{self.color}[{self.thread_name}] {clean_msg}{RESET}"
        
        # 3. Push to the shared queue (Non-blocking)
        log_queue.put(formatted_message)

# --- Main Execution ---
def main():
    config_file = "config/api_config.yaml"
    test_data_file = "config/test_case_1.yaml"

    print(f"{BOLD}=== Initializing Dedicated Printer Thread Engine ==={RESET}")
    print(f"{CYAN}THREAD-1 (Left){RESET}" + (" " * 35) + f"{YELLOW}THREAD-2 (Indented){RESET}\n")

    # 1. Start the Printer Thread (Daemon Mode)
    # Daemon means it will automatically die when the main script finishes
    printer_thread = threading.Thread(target=printer_daemon, daemon=True)
    printer_thread.start()

    # 2. Setup Loggers
    # Thread 1: No Indent, Cyan
    logger1 = AsyncLogger("THREAD-1", CYAN, indent_level=0)
    # Thread 2: 50-space Indent, Yellow
    logger2 = AsyncLogger("THREAD-2", YELLOW, indent_level=1)

    # 3. Start Worker Threads
    # We pass the .log method just like before, but now it's async!
    worker1 = threading.Thread(target=run_test_workflow, args=(config_file, test_data_file, logger1.log))
    worker2 = threading.Thread(target=run_test_workflow, args=(config_file, test_data_file, logger2.log))

    worker1.start()
    worker2.start()

    # 4. Wait for Workers to Finish
    worker1.join()
    worker2.join()

    # 5. Wait for Printer to Finish Emptying the Queue
    # This ensures no logs are lost if the workers finish very quickly
    log_queue.join()

    print(f"\n{BOLD}=== All Parallel Test Cases Completed ==={RESET}")

if __name__ == "__main__":
    main()