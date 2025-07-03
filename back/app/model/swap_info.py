from typing import Optional

from pydantic import BaseModel


class MBTIType(BaseModel):
    ie_type: int
    ntsf_type: int
    pj_type: int


class ProfileInfo(BaseModel):
    major_type: int
    mbti_type: MBTIType
    appearance_type: int
    hobby: int
    debate_stance: int


class SwapRequest(BaseModel):
    instagram_id: str
    gender: int
    major: str
    user_profile: ProfileInfo
    prefer_profile: Optional[ProfileInfo] = None
