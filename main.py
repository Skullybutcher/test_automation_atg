import threading
import time
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from modules.workflow import run_test_workflow

# --- UI State Management ---
# Buffers to store the logs for each thread
log_buffer_1 = []
log_buffer_2 = []

def make_layout():
    """Defines the split-screen layout."""
    layout = Layout()
    layout.split_row(
        Layout(name="left", ratio=1),
        Layout(name="right", ratio=1)
    )
    return layout

def generate_panel(logs, title, color):
    """Creates a UI panel from a list of log strings."""
    # Join logs and keep only the last 20 lines to prevent overflow
    log_text = "\n".join(logs[-20:])
    return Panel(Text.from_markup(log_text), title=title, border_style=color)

def logger_thread_1(message):
    """Callback for Thread 1 to write logs safely."""
    log_buffer_1.append(str(message))

def logger_thread_2(message):
    """Callback for Thread 2 to write logs safely."""
    log_buffer_2.append(str(message))

def main():
    config_file = "config/api_config.yaml"
    test_data_file = "config/test_case_1.yaml"

    # Setup the Rich Layout
    layout = make_layout()
    
    # Initialize Threads with their respective loggers
    thread1 = threading.Thread(
        target=run_test_workflow, 
        args=(config_file, test_data_file, logger_thread_1)
    )
    thread2 = threading.Thread(
        target=run_test_workflow, 
        args=(config_file, test_data_file, logger_thread_2)
    )

    # Start the Live Dashboard
    print("Initializing Parallel Test Dashboard...")
    with Live(layout, refresh_per_second=10, screen=False):
        thread1.start()
        thread2.start()

        # UI Loop: Keep updating the screen while threads are alive
        while thread1.is_alive() or thread2.is_alive():
            layout["left"].update(generate_panel(log_buffer_1, "THREAD 1 (Left)", "cyan"))
            layout["right"].update(generate_panel(log_buffer_2, "THREAD 2 (Right)", "yellow"))
            time.sleep(0.1)
        
        # Final update to ensure last messages are shown
        layout["left"].update(generate_panel(log_buffer_1, "THREAD 1 (Left)", "cyan"))
        layout["right"].update(generate_panel(log_buffer_2, "THREAD 2 (Right)", "yellow"))

    print("\n=== All Parallel Test Cases Completed ===")

if __name__ == "__main__":
    main()