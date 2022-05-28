from pyteal import *
from pyteal.ast.bytes import Bytes
     


def approval():

   
    # Actors
    # Vale la pena aggiungere l'info o il nome della crowdfound
    founder_actor = Bytes("founder")  # byteslice, actor asking for founds
    token_id = Bytes("token_id") 

    
    # Actions
    op_create_founding_pool = Bytes("create_pool") 

    # Other 
    founding_name = Bytes("founding_name")
    pool_target = Bytes("pool_target")
    start_time_key = Bytes("start")
    end_time_key = Bytes("end")


    # Forse questi 3 possono dare problemi
    target_reserve =  Btoi(Txn.application_args[0])
    starttime_founding =  Btoi(Txn.application_args[1])
    endtime_founding =  Btoi(Txn.application_args[2])
    pool_name =  Txn.application_args[3]

    app_address = ScratchVar()


    on_create = Seq(

                Assert(

                    And(
                        Txn.application_args.length() == Int(4),   
                        target_reserve > Int(0),
                        Global.latest_timestamp() < starttime_founding,
                        Global.latest_timestamp() < endtime_founding,
                        starttime_founding < endtime_founding, # questo potrebbe essere una durata minima 
                    )
                ),

                App.globalPut(founder_actor, Txn.sender()),
                App.globalPut(start_time_key, starttime_founding),
                App.globalPut(end_time_key,endtime_founding),
                App.globalPut(pool_target, target_reserve),
                App.globalPut(founding_name, pool_name),
                Approve()
    )

    on_setup = Seq(
        
        Assert(

            And(
            
                Gtxn[0].type_enum() == TxnType.Payment, # first txn is payment
                Gtxn[1].type_enum() == TxnType.ApplicationCall, # second txn is call
                # Aggiungere lunghezza del gruppo
            )

        ),

        Seq(

            InnerTxnBuilder.Begin(),

            InnerTxnBuilder.SetFields({

                TxnField.type_enum: TxnType.AssetConfig,
                TxnField.config_asset_total: App.globalGet(pool_target)),
                TxnField.config_asset_decimals: Int(3),
                TxnField.config_asset_default_frozen: Int(1), # dovrebbe essere true
                TxnField.config_asset_unit_name: Bytes("unit"),
                TxnField.config_asset_name: Itob(Global.latest_timestamp()),#Bytes("base32",Txn.sender()),
                TxnField.config_asset_manager: Global.current_application_address(),
                TxnField.config_asset_reserve: Global.current_application_address(),
                TxnField.config_asset_freeze: Global.current_application_address(),
                TxnField.config_asset_clawback: Global.current_application_address(),
                    
                }),
          

            InnerTxnBuilder.Submit()

        ),

        App.globalPut(token_id, InnerTxn.created_asset_id()), #assigning new token id to the app

        Approve()

    )


    program = Cond(

        [Txn.application_id() == Int(0), on_create],

        [And(
           Txn.on_completion() == OnComplete.NoOp,
           Txn.application_args[0] == Bytes("setup")
        ), on_setup],
    )

    return program

def clear():
    return Approve()

if __name__ == "__main__":
    with open("build/auction_approval.teal", "w") as f:
        compiled = compileTeal(approval(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("build/auction_clear_state.teal", "w") as f:
        compiled = compileTeal(clear(), mode=Mode.Application, version=5)
        f.write(compiled)
