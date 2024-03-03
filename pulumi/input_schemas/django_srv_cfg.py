from dataclasses import dataclass


@dataclass
class BackendCfg:
    cpu: int = 256
    memory: int = 512
    lb_port: int = 80
    container_port: int = 8000
    desired_count: int = 1


@dataclass
class DBCfg:
    engine: str
    version: str
    family: str


@dataclass
class DjangoServiceCfg:
    service_name: str
    django_project: str
    backend_cfg: BackendCfg
    db_cfg: DBCfg
