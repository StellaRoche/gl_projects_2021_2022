import time
import json

from Block import Block
from Blockchain import Blockchain
from Account import Account

hash_target = ('000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')

alice_account = Account('alice')
bob_account = Account('bob')
carol_account = Account('carol')
dave_account = Account('dave')


block_chain = Blockchain(hash_target)
time.sleep(1)

block_chain.add_account(alice_account)
block_chain.add_account(bob_account)
block_chain.add_account(carol_account)
block_chain.add_account(dave_account)



block_chain.add_transaction(alice_account.create_transaction('bob', 20))
block_chain.add_transaction(bob_account.create_transaction('carol', 30))
block_chain.add_transaction(carol_account.create_transaction('alice', 50))
block_chain.create_new_block()
time.sleep(1)


block_chain.add_transaction(alice_account.create_transaction('dave', 20))
block_chain.add_transaction(dave_account.create_transaction('carol', 35))
block_chain.add_transaction(bob_account.create_transaction('alice', 100))
# This should fail after validation check
block_chain.create_new_block()

# The code below is added to show creation of extra block, and balance checks before creation and pending transactions

block_chain.add_transaction(alice_account.create_transaction('dave', 20))
# This transaction will not be added in the block as Dave's balance is lesser than the transaction value of 335, hence it will be in the Insufficient balance list
block_chain.add_transaction(dave_account.create_transaction('bob', 335))
block_chain.create_new_block()

# The below two transactions will be in the Pending Transactions list

block_chain.add_transaction(alice_account.create_transaction('dave', 20))
block_chain.add_transaction(dave_account.create_transaction('carol', 35))


print(block_chain)
print("\n Individual account balances after block creation")
print(block_chain.get_account_balances())


validation_result = block_chain.validate_blockchain()
if (validation_result):
    print('\nValidation successful')
else:
    print('\nValidation failed')

