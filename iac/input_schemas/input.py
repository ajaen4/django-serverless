from dataclasses import dataclass, field

from pulumi import Config
from .django_srv_cfg import DjangoServiceCfg, BackendCfg, DBCfg, SuperUserCfg
from .vpc_cfg import VPCCfg


@dataclass
class Input:
    vpc_cfg: VPCCfg
    django_srvs_cfg: list[DjangoServiceCfg] = field(default_factory=list)

    @classmethod
    def from_cfg(cls, iac_cfg: Config) -> "Input":
        django_srvs_cfg_fmt = Input.serialize_django_srvs_cfg(iac_cfg)
        vpc_cfg_fmt = Input.serialize_vpc_cfg(iac_cfg)

        return cls(
            vpc_cfg=vpc_cfg_fmt,
            django_srvs_cfg=django_srvs_cfg_fmt,
        )

    @staticmethod
    def serialize_vpc_cfg(iac_cfg: Config) -> VPCCfg:
        name = iac_cfg.get("vpc_name") or "vpc"
        add_nat = iac_cfg.get_bool("add_nat") or False

        return VPCCfg(
            vpc_name=name,
            add_nat=add_nat,
        )

    @staticmethod
    def serialize_django_srvs_cfg(iac_cfg: Config) -> list[DjangoServiceCfg]:
        django_srvs_cfg: dict = iac_cfg.get_object("django_services") or {}
        django_srvs_cfg_fmt = list()

        for name, config in django_srvs_cfg.items():
            backend_cfg = config.get("backend")
            extra_container_args = dict()
            if "cpu" in backend_cfg:
                extra_container_args["cpu"] = backend_cfg["cpu"]
            if "memory" in backend_cfg:
                extra_container_args["memory"] = backend_cfg["memory"]
            if "lb_port" in backend_cfg:
                extra_container_args["lb_port"] = backend_cfg["lb_port"]
            if "container_port" in backend_cfg:
                extra_container_args["container_port"] = backend_cfg[
                    "container_port"
                ]

            if "desired_count" in backend_cfg:
                extra_container_args["desired_count"] = backend_cfg[
                    "desired_count"
                ]
            if "workers_per_instance" in backend_cfg:
                extra_container_args["workers_per_instance"] = str(
                    backend_cfg["workers_per_instance"]
                )

            superuser_cfg = backend_cfg["superuser"]
            superuser_cfg_fmt = SuperUserCfg(
                username=superuser_cfg["username"],
                email=superuser_cfg["email"],
            )

            backend_cfg_fmt = BackendCfg(
                django_project=backend_cfg["django_project"],
                superuser=superuser_cfg_fmt,
                **extra_container_args,
            )

            db_cfg = config.get("db")
            db_cfg_fmt = DBCfg(
                engine=db_cfg["engine"],
                version=db_cfg["version"],
                family=db_cfg["family"],
                db_name=db_cfg["db_name"],
                db_user=db_cfg["db_user"],
                port=db_cfg["port"],
            )

            django_srvs_cfg_fmt.append(
                DjangoServiceCfg(
                    service_name=name,
                    backend_cfg=backend_cfg_fmt,
                    db_cfg=db_cfg_fmt,
                )
            )

        return django_srvs_cfg_fmt
