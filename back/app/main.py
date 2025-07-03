from fastapi import FastAPI

from app.model.swap_info import SwapRequest
from app.token.eth_token_exchanger import EthereumTokenExchanger
from app.token.token_exchanger import TokenExchanger

app = FastAPI()


@app.post("/swap")
async def swap_token(swap_request: SwapRequest):
    token_exchanger: TokenExchanger = EthereumTokenExchanger()
    return token_exchanger.swap_token(swap_request)
