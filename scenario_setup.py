from contracts.external_utils.auction_demo.testing import resources
from algosdk import future, encoding, logic
from algosdk.v2client import algod
import requests
from algosdk.constants import MIN_TXN_FEE
from contracts.crowdfounding import scenario_utils
import time 


def setup_env():


    # Algo client

    algod_address = "http://host.docker.internal:4001"
    algod_token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    algod_client = algod.AlgodClient(algod_token, algod_address)

    founder1 = resources.getTemporaryAccount(algod_client)
    founder2 = resources.getTemporaryAccount(algod_client)
    founder3 = resources.getTemporaryAccount(algod_client)
    
    
    
    ##########################################################################
    ######## FOUNDERS CREATE POOLS
    ##########################################################################
    
    # First address creates a crowdfounding pool: during 2 minutes and small cap
    
    pool_create_txn1 = scenario_utils.create_pool(founder1, 2, 10000) # 12300000 microAlgo pool
    pool_create_txn1_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn1).sign(founder1.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn1_signed_encoded}
    application_id1 = requests.get('http://contract:8501/sign_contract', params=query).json()

    scenario_utils.setup_pool(founder1, application_id1["application_id"], algod_client)
    

    # Second address creates a small crowdfounding pool
    
    pool_create_txn2 = scenario_utils.create_pool(founder2, 2, 1000) # 1000 microAlgo pool
    pool_create_txn2_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn2).sign(founder2.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn2_signed_encoded}
    application_id2 = requests.get('http://contract:8501/sign_contract', params=query).json()
    
    scenario_utils.setup_pool(founder2, application_id2["application_id"], algod_client)
    
    
    # Third address creates a short lasting pool
    
    target_3 = 10000000
    pool_create_txn3 = scenario_utils.create_pool(founder3, 1440, target_3) # 12300000 microAlgo pool, 3 minutes
    pool_create_txn3_signed_encoded = encoding.msgpack_encode(
                                            encoding.future_msgpack_decode(pool_create_txn3).sign(founder3.getPrivateKey())
                                                              )
    query = {"contract_txn": pool_create_txn3_signed_encoded}
    application_id3 =  requests.get('http://contract:8501/sign_contract', params=query).json()
    
    scenario_utils.setup_pool(founder3, application_id3["application_id"], algod_client)



    ##########################################################################
    ######## FOUNDERS FUND EACH OTHER POOLS
    ##########################################################################

    # Second account optin and donate third pool, it doesn't met the cap yet

    asset_id3 = scenario_utils.get_latest_token(algod_client, application_id3["application_id"])
    
    if asset_id3:
    
        scenario_utils.asset_optin(founder2, algod_client, asset_id3)
        donate_txt_to_sign = scenario_utils.donate_action(algod_client, founder2.getAddress(), 
                                                          application_id3["application_id"], 
                                                          int(target_3*0.8), asset_id3)
        scenario_utils.sign_multiple_transactions(donate_txt_to_sign, founder2.getPrivateKey(), algod_client)


    # Founders 2 and 3 complete the crowdfunding
    # Please notice that should the amount being larger than the remaining pool target, the transaction fails

    asset_id1 = scenario_utils.get_latest_token(algod_client, application_id1["application_id"])
    
    if asset_id1:
    
        scenario_utils.asset_optin(founder2, algod_client, asset_id1)
        donate_txt_to_sign = scenario_utils.donate_action(algod_client, founder2.getAddress(), 
                                                          application_id1["application_id"], 
                                                          7000, asset_id1)
        scenario_utils.sign_multiple_transactions(donate_txt_to_sign, founder2.getPrivateKey(), algod_client)
        
        scenario_utils.asset_optin(founder3, algod_client, asset_id1)
        donate_txt_to_sign = scenario_utils.donate_action(algod_client, founder3.getAddress(), 
                                                          application_id1["application_id"], 
                                                          3000, asset_id1)
        scenario_utils.sign_multiple_transactions(donate_txt_to_sign, founder3.getPrivateKey(), algod_client)
        
        
    # Third account funds the second pool, it doesn't meet the cap
    
    asset_id2 = scenario_utils.get_latest_token(algod_client, application_id2["application_id"])

    if asset_id2:
    
        scenario_utils.asset_optin(founder3, algod_client, asset_id2)
        donate_txt_to_sign = scenario_utils.donate_action(algod_client, founder3.getAddress(), 
                                                          application_id2["application_id"], 
                                                          500, asset_id2)
        scenario_utils.sign_multiple_transactions(donate_txt_to_sign, founder3.getPrivateKey(), algod_client)


    # Wait 2 min until pool1 ends
    time.sleep(120)
    scenario_utils.claim_token(founder2, application_id1["application_id"], algod_client) # founder 2 claims tokens once poo1 ended
    scenario_utils.claim_funds(founder1, application_id1["application_id"], algod_client) # founder 1 claims funds raised by its pool
    scenario_utils.claim_funds(founder3, application_id2["application_id"], algod_client) # founder 3 asks for refund (pool 2 didn't reach its goal)


    print("Founder 1, " + founder1.getAddress()  + " created pool: " + str(application_id1["application_id"]))
    print("Founder 2, " + founder2.getAddress() + " created pool: " + str(application_id2["application_id"]))
    print("Founder 3, " + founder3.getAddress() + " created pool: " + str(application_id3["application_id"]))
    

setup_env()