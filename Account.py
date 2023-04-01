import hashlib
import json
import base64

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature


class Account:
    # Default balance is 100 if not sent during account creation
    # nonce is incremented once every transaction to ensure tx can't be replayed and can be ordered (similar to Ethereum)
    # private and public pem strings should be set inside __generate_key_pair
    def __init__(self, sender_id, balance=100):
        self._id = sender_id
        self._balance = balance
        # The initial balance value is used to store a copy of the initial balance before any transaction was done
        self._initial_balance=balance
        self._nonce = 0
        self._private_pem = None
        self._public_pem = None
        self.__generate_key_pair()

    @property
    def id(self):
        return self._id

    @property
    def public_key(self):
        return self._public_pem

    # This method will get the initial balance for the final retry of all transactions
    @property
    def initial_balance(self):
        return self._initial_balance

    def balance(self):
        return self._balance

    def increase_balance(self, value):
        self._balance += value

    def decrease_balance(self, value):
        self._balance -= value
    # This method will increase the initial balance of the receiver , used for the final retry of all transactions
    def increase_initial_balance(self, value):
        self._initial_balance += value

    # This method will decrease the initial balance of the sender , used for the final retry of all transactions
    def decrease_initial_balance(self, value):
        self._initial_balance -= value

    def __generate_key_pair(self):
        # Implement key pair generation logic
        # Convert them to pem format strings and store in the class attributes already defined
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # derive the public key from the private key
        public_key = private_key.public_key()
        # ---serialize the private key as bytes---
        self._private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # ---serialize the public key as bytes---
        self._public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def create_transaction(self, receiver_id, value, tx_metadata=''):

        nonce = self._nonce + 1
        transaction_message = {'sender': self._id, 'receiver': receiver_id, 'value': value, 'tx_metadata': tx_metadata,
                               'nonce': nonce}
        hash_string = json.dumps(transaction_message, sort_keys=True)

        encoded_hash_string = hash_string.encode('utf-8')

        # Take sha256 hash of the serialized message, and then convert to bytes format
        message_hash = hashlib.sha256(encoded_hash_string).hexdigest()
        encoded_message_hash = message_hash.encode('utf-8')


        private_key = serialization.load_pem_private_key(self._private_pem, password=None, )

        # Implement digital signature of the hash of the message
        signature = base64.b64encode(private_key.sign(
            encoded_message_hash,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )).decode('utf-8')

        self._nonce = nonce
        return {'message': transaction_message, 'signature': signature}





