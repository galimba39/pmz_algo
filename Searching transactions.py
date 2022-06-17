# 1. SDK client instantiations¶
import json
from algosdk.v2client import indexer

# instantiate indexer client
myindexer = indexer.IndexerClient(indexer_token="", indexer_address="http://localhost:8501")

# 2. Search transactions min_amount
response = myindexer.search_transactions(
    min_amount=10)

# Pretty Printing JSON string 
print("Transaction Info: " + json.dumps(response, indent=2, sort_keys=True))

# 3. Search transactions limit
response = myindexer.search_transactions(
    min_amount=10, limit=2)

# Pretty Printing JSON string 
print("Transaction Info: " + json.dumps(response, indent=2, sort_keys=True))

# 4. Search transactions paging 
nexttoken = ""
numtx = 1

# loop using next_page to paginate until there are no more transactions in the response
# for the limit (max is 1000  per request)

while (numtx > 0):

    response = myindexer.search_transactions(
        min_amount=100000000000000, limit=2, next_page=nexttoken) 
    transactions = response['transactions']
    numtx = len(transactions)
    if (numtx > 0):
        nexttoken = response['next-token']
        # Pretty Printing JSON string 
        print("Tranastion Info: " + json.dumps(response, indent=2, sort_keys=True))
		
		