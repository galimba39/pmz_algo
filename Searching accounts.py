# 1. Account info 
import json
from algosdk.v2client import indexer

# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8501")

response = myindexer.account_info(
    address="7WENHRCKEAZHD37QMB5T7I2KWU7IZGMCC3EVAO7TQADV7V5APXOKUBILCI")
print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))

# 2. Account Asset ID
response = myindexer.accounts(
    asset_id=312769)
print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))

# 3. Search transanctions note
import base64
note_prefix = 'showing prefix'.encode()

response = myindexer.search_transactions(note_prefix=note_prefix)

print("note_prefix = " + json.dumps(response, indent=2, sort_keys=True))

# 4. asset min balance
	response = myindexer.accounts(
    asset_id=312769, min_balance=100)
print("Account Info: " + json.dumps(response, indent=2, sort_keys=True))

# 5. asset balances
response = myindexer.asset_balances(asset_id=2044572)
print("Asset Balance: " + json.dumps(response, indent=2, sort_keys=True))




