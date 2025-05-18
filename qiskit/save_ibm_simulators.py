# --- Standard Library ---
import os

# --- Third-Party Libraries ---
import dill
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_aer import AerSimulator
from dotenv import load_dotenv

# --- Configurations ---
load_dotenv()

# --- Paths & Directories ---
IBM_SIMULATORS_BASE_PATH = os.getenv("IBM_SIMULATORS_BASE_PATH")

# --- API Token ---
IBM_TOKEN = os.getenv("IBM_API_TOKEN")


def save_ibm_simulators(channel: str, token: str, base_path: str, verbose: bool = True) -> None:
    """
    Save AerSimulator objects (configured from IBM backends) using dill into structured folders.

    Args:
        channel (str): QiskitRuntimeService channel (e.g., 'ibm_quantum').
        token (str): IBM Quantum API token.
        base_path (str): Absolute path to store the 'ibm_simulators' directory.
        verbose (bool): If True, print status messages.
    """
    target_backends = ["ibm_brisbane", "ibm_sherbrooke"]

    simulation_methods = [
        "aer_simulator_statevector",
        "aer_simulator_density_matrix",
        "aer_simulator_stabilizer",
        "aer_simulator_matrix_product_state",
        "aer_simulator_extended_stabilizer",
        "aer_simulator_unitary",
        "aer_simulator_superop",
        "aer_simulator_statevector_gpu",
        "aer_simulator_density_matrix_gpu",
        "aer_simulator_unitary_gpu"
    ]

    # Create main directory
    root_dir = os.path.join(base_path, "ibm_simulators")
    os.makedirs(root_dir, exist_ok=True)

    try:
        service = QiskitRuntimeService(channel=channel, token=token)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize QiskitRuntimeService: {e}")

    for backend_name in target_backends:
        try:
            backend = service.backend(backend_name)
        except Exception as e:
            if verbose:
                print(f"Failed to load backend '{backend_name}': {e}")
            continue

        backend_dir = os.path.join(root_dir, backend_name)
        os.makedirs(backend_dir, exist_ok=True)

        for method in simulation_methods:
            try:
                device = "GPU" if method.endswith("_gpu") else "CPU"
                base_method = method.replace("aer_simulator_", "").replace("_gpu", "")
                simulator = AerSimulator.from_backend(backend)
                simulator.set_options(method=base_method, device=device)

                filename = f"{method}.dill"
                filepath = os.path.join(backend_dir, filename)
                with open(filepath, "wb") as f:
                    dill.dump(simulator, f)

                if verbose:
                    print(f"Saved simulator '{filepath}'")

            except Exception as e:
                if verbose:
                    print(f"Failed to save simulator for '{backend_name}' with method '{method}': {e}")

# Example usage:
# Uncomment the following lines to run the function

save_ibm_simulators(
    channel="ibm_quantum",
    token=IBM_TOKEN,
    base_path=IBM_SIMULATORS_BASE_PATH,
    verbose=True
)