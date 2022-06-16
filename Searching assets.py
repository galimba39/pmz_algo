# 1. search assets name
import json
from algosdk.v2client import indexer

# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8501")

response = myindexer.search_assets(
    name="")
print("Asset Name Info: " + json.dumps(response, indent=2, sort_keys=True))

# 2. search assets
response = myindexer.search_assets(
    asset_id=2044572)

print("Asset Info: " + json.dumps(response, indent=2, sort_keys=True))

# 3. asset balances
response = myindexer.asset_balances(
    asset_id=2044572)
print("Asset Balance: " + json.dumps(response, indent=2, sort_keys=True))

# 4. asset transactions role
response = myindexer.search_asset_transactions(asset_id=2044572, address_role="receiver", address="UF7ATOM6PBLWMQMPUQ5QLA5DZ5E35PXQ2IENWGZQLEJJAAPAPGEGC3ZYNI")

print("Asset Transaction Info: " + json.dumps(response, indent=2, sort_keys=True))