### Docker files

In this folder there are three files responding to 3 different needs for this project:

- **Backend solution**: a container being responsible of preparing, creating and sending transactions to an algorand node. A user can sign transactions on its own possibly, except for the one creating the crowdfunding pool for which he needs to send it back signed to the backend solution.

- **Contract database**: a POSTGRES database is used to tracks the created crowdfunding pools. Only the smart contracts being created and signed via the backend solution are tracked, and only these can be shown in the webapp.
Please notice that the backend solution only tracks created smart contracts, it does not have a multisignature involvement with the funder.

- **Scenario setup**: this container is meant to have a limited lifecycle. It provides a scenario setting, showing 3 actors creating pools, interacting each others pools and eventually unfreezing their tokens and retrieving their raised funds if successful. Once done, the container exits.





