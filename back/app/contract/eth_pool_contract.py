from web3 import Web3
import json
from dotenv import load_dotenv
import os

load_dotenv()

try:
    RPC_URL = os.environ["RPC_URL"]
    TOKEN_ACCOUNT_ADDRESS = os.environ["TOKEN_ACCOUNT_ADDRESS"]
    PRIVATE_KEY = os.environ["TOKEN_ACCOUNT_PRIVATE_KEY"]
    NFT_TOKEN_ADDRESS = os.environ["NFT_TOKEN_ADDRESS"]
    SWAP_POOL_ADDRESS = os.environ["SWAP_POOL_ADDRESS"]
except KeyError:
    print("Missing Address variables")
    exit()

TOKEN_ACCOUNT_ADDRESS = Web3.to_checksum_address(TOKEN_ACCOUNT_ADDRESS)
NFT_TOKEN_ADDRESS = Web3.to_checksum_address(NFT_TOKEN_ADDRESS)
SWAP_POOL_ADDRESS = Web3.to_checksum_address(SWAP_POOL_ADDRESS)

with open("abi/LoveToken_abi.json") as f:
    token_abi = json.load(f)
with open("abi/NftSwapPool_abi.json") as f:
    pool_abi = json.load(f)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

nft_token = w3.eth.contract(address=NFT_TOKEN_ADDRESS, abi=token_abi)
swap_pool = w3.eth.contract(address=SWAP_POOL_ADDRESS, abi=pool_abi)


def set_approval():
    is_transfer_approved = nft_token.functions.isApprovedForAll(TOKEN_ACCOUNT_ADDRESS, SWAP_POOL_ADDRESS).call()
    if is_transfer_approved:
        return
    nonce = w3.eth.get_transaction_count(TOKEN_ACCOUNT_ADDRESS)
    tx = nft_token.functions.setApprovalForAll(SWAP_POOL_ADDRESS, True).build_transaction({
        'from': TOKEN_ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 100_000,
        'gasPrice': w3.to_wei('200', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)


def mint_token(user_info, token_amount):
    nonce = w3.eth.get_transaction_count(TOKEN_ACCOUNT_ADDRESS)
    tx = nft_token.functions.mint(
        TOKEN_ACCOUNT_ADDRESS,
        user_info['instagramId'],
        user_info['major'],
        user_info['majorType'],
        user_info['mbtiIeType'],
        user_info['mbtiNtsfType'],
        user_info['mbtiPjType'],
        user_info['appearanceType'],
        user_info['hobby'],
        user_info['debateStance'],
        token_amount
    ).build_transaction({
        'from': TOKEN_ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 500_000,
        'gasPrice': w3.to_wei('200', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    token_id = nft_token.functions.currentTokenId().call()
    return token_id


def get_user_info(token_id):
    user_info = nft_token.functions.getUserInfo(token_id).call()
    return user_info


def get_swap_candidates(pool_type: int):
    if pool_type == 0:
        return swap_pool.functions.getBPoolTokenIds().call()
    else:
        return swap_pool.functions.getAPoolTokenIds().call()


def swap_token(pool_type: int, token_id, target_token_id):
    if token_id is None or target_token_id is None:
        raise ValueError("No token found")

    set_approval()

    nonce = w3.eth.get_transaction_count(TOKEN_ACCOUNT_ADDRESS)
    tx = swap_pool.functions.swap(pool_type, token_id, target_token_id).build_transaction({
        'from': TOKEN_ACCOUNT_ADDRESS,
        'nonce': nonce,
        'gas': 300_000,
        'gasPrice': w3.to_wei('200', 'gwei')
    })
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    user_info = get_user_info(target_token_id)
    return user_info
