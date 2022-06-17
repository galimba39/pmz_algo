# 1. Search transaction address time
import json
from algosdk.v2client import indexer

# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8501")

#NON RIESCO AD INSERIRE address
response = myindexer.search_transactions_by_address(
    address="", start_time="2020-06-03T10:00:00-05:00")

print("Transaction Start Time 2020-06-03T10:00:00-05:00 = " +
      json.dumps(response, indent=2, sort_keys=True))
	  
# 2. address block
print("block: 7048877 = " + json.dumps(response, indent=2, sort_keys=True))

# 3. address block range 
#NON RIESCO AD INSERIRE address
response = myindexer.search_transactions_by_address(
    address="", min_round=7048876, max_round=7048878)

print("min-max rounds: 7048876-7048878 = " +
      json.dumps(response, indent=2, sort_keys=True))
	  
# 4. address tx id
#NON RIESCO AD INSERIRE address
response = myindexer.search_transactions_by_address(
    address="",
    txid="QZS3B2XBBS47S6X5CZGKKC2FC7HRP5VJ4UNS7LPGHP24DUECHAAA")

print("txid: QZS3B2XBBS47S6X5CZGKKC2FC7HRP5VJ4UNS7LPGHP24DUECHAAA = " +
      json.dumps(response, indent=2, sort_keys=True))
	  
# 5. address tx time
#NON RIESCO AD INSERIRE address
response = myindexer.search_transactions_by_address(
    address="",
    txn_type="acfg")

print("txn_type: acfg = " +
      json.dumps(response, indent=2, sort_keys=True))

# 6. address sign type
#NON RIESCO AD INSERIRE address
response = myindexer.search_transactions_by_address(
    address="", sig_type="msig")

print("sig_type: msig = " +
      json.dumps(response, indent=2, sort_keys=True))
