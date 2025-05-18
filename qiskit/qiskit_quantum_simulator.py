# --- Standard Library ---
import os

# --- Third-Party Libraries ---
import dill
from qiskit import transpile
from qiskit_ibm_runtime import SamplerV2 as Sampler
from dotenv import load_dotenv

# --- Configurations---
load_dotenv()


class QiskitQuantumSimulator:
    """
    A flexible wrapper for running IBM Quantum circuits on pre-serialized Qiskit Aer simulators,
    supporting multiple simulation methods and GPU acceleration.
    """

    # 🔧 Set this to the absolute path where 'ibm_simulators' folder is located
    __IBM_SIMULATORS_BASE_PATH = os.getenv("IBM_SIMULATORS_BASE_PATH")


    __SUPPORTED_SIMULATION_METHODS = {
        'aer_simulator_statevector',
        'aer_simulator_density_matrix',
        'aer_simulator_stabilizer',
        'aer_simulator_matrix_product_state',
        'aer_simulator_extended_stabilizer',
        'aer_simulator_unitary',
        'aer_simulator_superop',
        'aer_simulator_statevector_gpu',
        'aer_simulator_density_matrix_gpu',
        'aer_simulator_unitary_gpu'
    }

    __AVAILABLE_BACKENDS = {
        'ibm_brisbane',
        'ibm_sherbrooke'
    }

    def __init__(self, ibm_backend: str, simulation_method: str = 'aer_simulator_statevector'):
        """
        Initialize the simulator using a serialized AerSimulator.

        Args:
            ibm_backend (str): One of the supported backend names.
            simulation_method (str): One of the supported simulation methods.
        """
        self.__set_ibm_backend(ibm_backend)
        self.__set_simulator(simulation_method)

    def __load_simulator(self, filepath: str):
        """Loads a preconfigured AerSimulator from a .dill file."""
        try:
            with open(filepath, 'rb') as f:
                simulator = dill.load(f)
            if not hasattr(simulator, 'run'):
                raise TypeError("Loaded object is not a valid AerSimulator.")
            return simulator
        except Exception as e:
            raise IOError(f"Failed to load AerSimulator from {filepath}: {e}")

    def __set_ibm_backend(self, ibm_backend: str):
        """
        Sets the backend name.

        Args:
            ibm_backend (str): Must be one of the supported backend names.

        Raises:
            ValueError: If the backend is not supported.
        """
        if ibm_backend not in self.__AVAILABLE_BACKENDS:
            raise ValueError(
                f"Unsupported IBM backend: '{ibm_backend}'.\n"
                f"Available backends: {self.__AVAILABLE_BACKENDS}"
            )
        self.__ibm_backend_name = ibm_backend

    def __set_simulator(self, method: str):
        """
        Sets the simulation method and loads the corresponding AerSimulator.

        Args:
            method (str): Must be one of the supported simulation methods.

        Raises:
            ValueError: If the method is not supported.
        """
        if method not in self.__SUPPORTED_SIMULATION_METHODS:
            raise ValueError(
                f"Unsupported simulation method: '{method}'.\n"
                f"Supported methods: {self.__SUPPORTED_SIMULATION_METHODS}"
            )
        self.__simulation_method = method

        # 🗂 Construct full path to the .dill file based on folder structure
        folder_path = os.path.join(self.__IBM_SIMULATORS_BASE_PATH, "ibm_simulators", self.__ibm_backend_name)
        filename = f"{method}.dill"
        filepath = os.path.join(folder_path, filename)

        self.__simulator = self.__load_simulator(filepath)

    def transpile_circuit(self, circuit):
        """Transpiles the circuit for the current simulator."""
        return transpile(circuit, backend=self.__simulator, optimization_level=1)

    def run(self, circuit):
        """Runs the transpiled circuit using Qiskit's Aer Sampler."""
        transpiled = self.transpile_circuit(circuit)
        sampler = Sampler(mode=self.__simulator)
        return sampler.run([transpiled])
    
    def available_simulation_methods(self):
        """Returns the available simulation methods."""
        return self.__SUPPORTED_SIMULATION_METHODS

    def available_backends(self):
        """Returns the available IBM backends."""
        return self.__AVAILABLE_BACKENDS

    @property
    def ibm_backend(self):
        """Returns the IBM backend name."""
        return self.__ibm_backend_name

    @property
    def simulator(self):
        """Returns the loaded AerSimulator instance."""
        return self.__simulator

    @property
    def simulation_method(self):
        """Returns the current simulation method."""
        return self.__simulation_method