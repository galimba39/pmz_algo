from pyteal import compileTeal,Mode
from . import contract # working inside the docker
from algosdk.constants import MIN_TXN_FEE
from algosdk import future
from base64 import b64decode


def fullyCompileContract(client, contract) -> bytes:

    teal = compileTeal(contract, mode=Mode.Application, version=6)
    response = client.compile(teal)

    return b64decode(response["result"])


def createCrowdFoundindTxt(
    client,
    sender,
    pool_name,
    target,
    startTime,
    endTime):

    """
        asdads
    """
    
    globalSchema = future.transaction.StateSchema(num_uints=4,num_byte_slices=2)
    localSchema = future.transaction.StateSchema(num_uints=0,num_byte_slices=0)

    app_args = [
        target.to_bytes(8, "big"),
        startTime.to_bytes(8, "big"),
        endTime.to_bytes(8, "big"),
        pool_name

    ]

    parameters = client.suggested_params()

    create_txn = future.transaction.ApplicationCreateTxn(
        sender = sender,
        on_complete= future.transaction.OnComplete.NoOpOC,
        approval_program = fullyCompileContract(client,contract.approval()),
        clear_program = fullyCompileContract(client,contract.clear()),
        global_schema = globalSchema,
        local_schema = localSchema,
        app_args=app_args,
        sp=parameters,
        
    )

    return create_txn


def inspect_transaction(txid, algod_client):

    import json
    import base64

    try:
        confirmed_txn = future.transaction.wait_for_confirmation(algod_client, txid, 4)

        print("Transaction information: {}".format(
            json.dumps(confirmed_txn, indent=4)))
        print("Decoded note: {}".format(base64.b64decode(
            confirmed_txn["txn"]["txn"]["note"]).decode()))
        
        return confirmed_txn

    except Exception as err:
        print(err)

        return None
        
        
        
def return_application_id(txid, algod_client):

    import json
    import base64

    try:
        confirmed_txn = future.transaction.wait_for_confirmation(algod_client, txid, 4)
        return confirmed_txn["application-index"]

    except Exception as err:
        print(err)

        return None