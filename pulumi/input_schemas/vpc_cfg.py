from dataclasses import dataclass


@dataclass
class VPCCfg:
    vpc_name: str
    add_nat: bool
