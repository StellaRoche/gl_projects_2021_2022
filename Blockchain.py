import json
import hashlib
import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.exceptions import InvalidSignature

from Block import Block


class Blockchain:
    # Basic blockchain init
    # Includes the chain as a list of blocks in order, pending transactions, and known accounts
    # Includes the current value of the hash target. It can be changed at any point to vary the difficulty
    # Also initiates a genesis block
    def __init__(self, hash_target):
        self._chain = []
        #This will store all transactions not added to the block
        self._pending_transactions = []
        # This will store all transactions for which the balances have been checked ready to be added to the block
        self._balance_checked_transactions = []
        # This will store all transactions that have been rejected because of insufficient balances
        self._insufficient_balance_transactions = []
        self._chain.append(self.__create_genesis_block())
        self._hash_target = hash_target
        self._accounts = {}

    def __str__(self):
        return f"Chain:\n{self._chain}\n\nPending Transactions: {self._pending_transactions}\nInsufficient Balance Transactions: {self._insufficient_balance_transactions}\n "

    @property
    def hash_target(self):
        return self._hash_target

    @hash_target.setter
    def hash_target(self, hash_target):
        self._hash_target = hash_target


    # Creating the genesis block, taking arbitrary previous block hash since there is no previous block
    # Using the famous bitcoin genesis block string here :)
    def __create_genesis_block(self):
        genesis_block = Block(0, [], 'The Times 03/Jan/2009 Chancellor on brink of second bailout for banks',
                              None, 'Genesis block using same string as bitcoin!')
        return genesis_block

    def __validate_transaction(self, transaction):

        # Serialize transaction data with keys ordered, and then convert to bytes format
        hash_string = json.dumps(transaction['message'], sort_keys=True)
        encoded_hash_string = hash_string.encode('utf-8')

        # Take sha256 hash of the serialized message, and then convert to bytes format
        message_hash = hashlib.sha256(encoded_hash_string).hexdigest()
        encoded_message_hash = message_hash.encode('utf-8')

        # Signature - Encode to bytes and then Base64 Decode to get the original signature format back
        signature = base64.b64decode(transaction['signature'].encode('utf-8'))

        try:
            # Load the public_key object and verify the signature against the calculated hash
            sender_public_pem = self._accounts.get(transaction['message']['sender']).public_key
            sender_public_key = serialization.load_pem_public_key(sender_public_pem)

            sender_public_key.verify(signature, encoded_message_hash, padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                                                                  salt_length=padding.PSS.MAX_LENGTH),
                                     hashes.SHA256())

        except InvalidSignature:

            return False

        return True

    def __process_transactions(self, transactions):
        # Appropriately transfer value from the sender to the receiver
        # For all transactions, first check that the sender has enough balance.
        # Return False otherwise


        i = 0
        while i < len(transactions):
            # The sender's balance is checked to ensure that there is sufficient balance to do the transaction
            if (self._accounts.get(transactions[i]['message']['sender']).balance()) >= transactions[i]['message'][
                'value']:
                # The sender's balance is reduced with the transaction value
                self._accounts[transactions[i]['message']['sender']].decrease_balance(
                    transactions[i]['message']['value'])
                # The receiver's balance is increased with the transaction value
                self._accounts[transactions[i]['message']['receiver']].increase_balance(
                    transactions[i]['message']['value'])
                # The transaction after being checked is now appended to the balance_checked_transactions list
                self._balance_checked_transactions.append(transactions[i])
                i = i + 1

            else:
                # If balance for transaction was insufficient the transaction is rejected and put in the insufficient_balance_transactions list
                self._insufficient_balance_transactions.append(transactions[i])
                i = i + 1
        print("\nBalance checked transactions")
        print(self._balance_checked_transactions)
        print("\nInsufficient balance transactions")
        print(self._insufficient_balance_transactions)
        return True

    # Creates a new block and appends to the chain
    # Also clears the pending transactions as they are part of the new block now
    def create_new_block(self):

        if self.__process_transactions(self._pending_transactions):
            new_block = Block(len(self._chain), self._balance_checked_transactions, self._chain[-1].block_hash,
                              self._hash_target)
            self._chain.append(new_block)
            # The pending transactions list and balance_checked_transactions list is emptied once the block is created
            self._pending_transactions = []
            self._balance_checked_transactions = []
            return new_block
        else:
            return False

    # Simple transaction with just one sender, one receiver, and one value
    # Created by the account and sent to the blockchain instance
    def add_transaction(self, transaction):

        if self.__validate_transaction(transaction):
            self._pending_transactions.append(transaction)
            return True
        else:
            print(f'ERROR: Transaction: {transaction} failed signature validation')
            return False

    def __validate_chain_hash_integrity(self):
        # Run through the whole blockchain and ensure that previous hash is actually the hash of the previous block
        # Return False otherwise
        for index in range(1, len(self._chain)):

            if (self._chain[index].previous_block_hash != self._chain[index - 1].hash_block()):
                print(f'Previous block hash mismatch in block index: {index}')
                return False

            return True

    def __validate_block_hash_target(self):
        # Run through the whole blockchain and ensure that block hash meets hash target criteria, and is the actual hash of the block
        # Return False otherwise
        for index in range(1, len(self._chain)):
            if (int(self._chain[index].hash_block(), 16) >= int(self._chain[index].hash_target, 16)):
                print(f'Hash target not achieved in block index: {index}')
                return False
            if (int(self._chain[index].hash_block(), 16) != self._chain[index].block_hash):
                print(f'Current block hash mismatch with actual block hash: {index}')
                return False

        return True

    def __validate_complete_account_balances(self):
        # Run through the whole blockchain and ensure that balances never become negative from any transaction
        # Return False otherwise


        for i in range(1,len(self._chain)):

            for j in (i._transactions):

                a = j['message']['sender']
                b = j['message']['receiver']
                v = j['message']['value']

                # We now used the initial_balance where we had saved the initial balance before any transaction was done
                if self._accounts[a].initial_balance < 0 or self._accounts[a].initial_balance < j['message']['value']:
                    return False
                else:
                    self._accounts[a].decrease_initial_balance(v)
                    self._accounts[b].increase_initial_balance(v)
        return True


    # Blockchain validation function
    # Runs through the whole blockchain and applies appropriate validations
    def validate_blockchain(self):
        # Call __validate_chain_hash_integrity and implement that method. Return False if check fails
        # Call __validate_block_hash_target and implement that method. Return False if check fails
        # Call __validate_complete_account_balances and implement that method. Return False if check fails
        if not self.__validate_chain_hash_integrity():
            return False

            if not self.__validate_block_hash_target():
                return False

                if not __validate_complete_account_balances():
                    return False

        return True

    def add_account(self, account):
        self._accounts[account.id] = account

    def get_account_balances(self):
        return [{'id': account.id, 'balance': account.balance()} for account in self._accounts.values()]

    def get_initial_account_balances(self):
        return [{'id': account.id, 'balance': account.initial_balance} for account in self._accounts.values()]



