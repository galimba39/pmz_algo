### Setup the environment

1) Setup the sandbox. Go to the sandbox folder and run

> ./sandbox up

2) Build up the backend. In this folder, run

> docker-compose up --build

The docker compose will start 3 nodes: one sql server, storing contracts, an API backend and a setup scripts, creating 3 pools from 3 users. The compose will be ready once  a similar image shows up 

<p align="center">
  <img src="images/docker_ok.png" width="600" alt="accessibility text">
</p>

### Api interaction

Currently you can interact with the backend API this way:

> **get the address info**:  http://localhost:8501/address_info?address=PUBLICKEY


> **create a crowdfunding pool** http://localhost:8501/create_contract?sender=PUBLICKEY&pool_name=prova&target=10000&startTime=1653775200&endTime=1653948000

(in the case above the pool is named "prova", has a fundraising target of 10000 microalgos, with the corresponding _StartTime_ and _endTime_ will be setup by the address _PUBLICKEY_)

> **Retrieve all contracts** http://localhost:8501/get_all_contracts

The request above returns all contracts that have been created using the crowdfunding pool api above


**Please notice** that in order to make it works, the algorand address asking to build the contract must be founded.
Back to the algorand folder, run
> ./sandbox enter algod

and the 

> goal clerk send -a 100000000 -f 6B2KSSG2ZWW3X3NNONJ4NNFWJXBHGI3K7VUZHISFKUVP2UEXF22QJDF7WY -t PUBLICKEY
