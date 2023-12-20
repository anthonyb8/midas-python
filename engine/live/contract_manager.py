from .data_client import DataClient
from ibapi.contract import Contract
from ..utils import setup_logger

data_logger = setup_logger("dataLogger", "/Users/anthony/git-projects/EventTrader/logs/data.log")

class ContractManager:

    def __init__(self, client_instance: DataClient):
        self.client = client_instance
        self.app = self.client.app
        self.validated_contracts = {}  # Dictionary to store validated contracts

    def validate_contract(self, contract: Contract) -> bool:
        """Validate a contract with IB."""
        
        # Check if the contract is already validated
        if self.is_contract_validated(contract):
            data_logger.info(f"Contract {contract.symbol} is already validated.")
            return True

        # Reset the validation attribute in case it has been used before
        self.app.is_valid_contract = None  
        self.app.validate_contract_event.clear()

        # Request contract details from IB
        reqId = self.client._get_valid_id()
        self.app.reqContractDetails(reqId=reqId, contract=contract)
        self.app.validate_contract_event.wait()

        # Store the validated contract if it's valid
        if self.app.is_valid_contract:
            self.validated_contracts[contract.symbol] = contract
            data_logger.info(f"Contract {contract.symbol} validated successfully.")
        else:
            data_logger.warning(f"Contract {contract.symbol} validation failed.")
            
        return self.app.is_valid_contract

    def is_contract_validated(self, contract: Contract) -> bool:
        """Check if a contract has already been validated."""
        return contract.symbol in self.validated_contracts
