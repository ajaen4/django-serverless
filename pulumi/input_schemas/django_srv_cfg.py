from dataclasses import dataclass


@dataclass
class SuperUserCfg:
    username: str
    email: str


@dataclass
class BackendCfg:
    django_project: str
    superuser: SuperUserCfg
    cpu: int = 256
    memory: int = 512
    lb_port: int = 80
    container_port: int = 8000
    desired_count: int = 1
    workers_per_instance: str = 1


@dataclass
class DBCfg:
    engine: str
    version: str
    family: str
    db_name: str
    port: str


@dataclass
class DjangoServiceCfg:
    service_name: str
    backend_cfg: BackendCfg
    db_cfg: DBCfg
