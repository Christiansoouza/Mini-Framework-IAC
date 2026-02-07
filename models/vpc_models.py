from typing import TypedDict, List

class VpcModel(TypedDict):
    vpc_id: str
    public_subnets: List[str]
    private_subnets: List[str]