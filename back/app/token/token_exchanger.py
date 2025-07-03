from abc import ABC, abstractmethod

from app.model.swap_info import SwapRequest


class TokenExchanger(ABC):

    @abstractmethod
    def swap_token(self, swap_request: SwapRequest):
        pass
