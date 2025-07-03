from app.contract.eth_pool_contract import mint_token, get_swap_candidates, swap_token, get_user_info
from app.model.swap_info import SwapRequest, ProfileInfo, MBTIType
from app.token.token_exchanger import TokenExchanger
from app.util.encrypt_util import encrypt, decrypt


class EthereumTokenExchanger(TokenExchanger):

    def swap_token(self, swap_request: SwapRequest):
        user_profile = swap_request.user_profile
        user_preference = swap_request.prefer_profile
        pool_type = swap_request.gender

        user_info = {
            "instagramId": encrypt(swap_request.instagram_id),
            "major": encrypt(swap_request.major),
            "majorType": user_profile.major_type,
            "mbtiIeType": user_profile.mbti_type.ie_type,
            "mbtiNtsfType": user_profile.mbti_type.ntsf_type,
            "mbtiPjType": user_profile.mbti_type.pj_type,
            "appearanceType": user_profile.appearance_type,
            "hobby": user_profile.hobby,
            "debateStance": user_profile.debate_stance
        }

        token_amount = self.calculate_token_amount(pool_type)
        token_id = mint_token(user_info, token_amount)

        target_token_id = self.find_swap_target(pool_type, user_preference)
        swapped_token = swap_token(pool_type, token_id, target_token_id)

        if swapped_token is None:
            raise Exception('swap token not found')

        swapped_user_info = self.convert_token_info_to_swap_request(pool_type, swapped_token)
        return swapped_user_info

    def find_swap_target(self, pool_type: int, user_preference: ProfileInfo):
        swap_candidates = get_swap_candidates(pool_type)
        match_point = self.calculate_match_point(len(swap_candidates))
        max_score = 0
        max_target = 0
        for token_id in swap_candidates:
            target_user = get_user_info(token_id)
            target_user = self.convert_token_info_to_swap_request(pool_type, target_user)
            score = self.calculate_score(target_user.user_profile, user_preference)
            if score > max_score:
                max_score = score
                max_target = token_id
            if score >= match_point:
                return token_id
        return max_target

    @staticmethod
    def calculate_token_amount(pool_type: int):
        if pool_type == 0:
            return 1
        else:
            return 2

    @staticmethod
    def calculate_match_point(pool_size: int):
        if pool_size < 3:
            return 1
        elif pool_size < 5:
            return 2
        elif pool_size < 7:
            return 3
        elif pool_size < 10:
            return 4
        else:
            return 5

    @staticmethod
    def convert_token_info_to_swap_request(pool_type, token_info):
        return SwapRequest(
            instagram_id=decrypt(token_info[0]),
            gender=abs(pool_type - 1),
            major=decrypt(token_info[1]),
            user_profile=ProfileInfo(
                major_type=token_info[2],
                mbti_type=MBTIType(
                    ie_type=token_info[3],
                    ntsf_type=token_info[4],
                    pj_type=token_info[5]
                ),
                appearance_type=token_info[6],
                hobby=token_info[7],
                debate_stance=token_info[8]
            )
        )

    @staticmethod
    def calculate_score(target_user, user_preference):
        score = 0
        if target_user.major_type == user_preference.major_type:
            score += 1
        if target_user.mbti_type.ie_type == user_preference.mbti_type.ie_type:
            score += 1
        if target_user.mbti_type.ntsf_type == user_preference.mbti_type.ntsf_type:
            score += 1
        if target_user.mbti_type.pj_type == user_preference.mbti_type.pj_type:
            score += 1
        if target_user.appearance_type == user_preference.appearance_type:
            score += 1
        if target_user.hobby == user_preference.hobby:
            score += 1
        if target_user.debate_stance == user_preference.debate_stance:
            score += 1
        return score
