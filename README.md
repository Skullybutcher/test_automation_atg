# Avi Load Balancer Automation Framework

A robust, multi-threaded automation framework designed to interact with the Avi Load Balancer Mock API. This framework executes test cases in parallel, ensuring high performance and thread safety.

## 🚀 Key Features

* **Parallel Execution:** Implements the **Producer-Consumer pattern** using Python's `queue.Queue` to run test workflows concurrently without blocking.
* **Thread-Safe Logging:** Worker threads push logs to a central queue, while a dedicated **Daemon Printer Thread** handles terminal output. This ensures clean, non-interleaved logs even under high load.
* **Robust Error Handling:** Encapsulates workflows in `try/except` blocks to catch and report critical failures without crashing the entire automation suite.
* **Modular Design:** Separates configuration, API logic, workflow steps, and mock tools for maintainability.

## 🛠️ Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configuration:**
    * Update `config/api_config.yaml` with your credentials if necessary.
    * Review `config/test_case_1.yaml` to modify test parameters.

## ▶️ Execution

Run the main script to execute parallel test cases with the enhanced logging engine:

```bash
python main.py