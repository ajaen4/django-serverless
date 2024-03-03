from dataclasses import dataclass

from pulumi import Config
from .django_srv_cfg import DjangoServiceCfg, BackendCfg, DBCfg
from .vpc_cfg import VPCCfg


@dataclass
class Input:
    vpc_cfg: VPCCfg
    django_srvs_cfg: list[DjangoServiceCfg] = None

    @classmethod
    def from_cfg(cls, iac_cfg: Config):
        django_srvs_cfg_fmt = Input.serialize_django_srvs_cfg(iac_cfg)
        vpc_cfg_fmt = Input.serialize_vpc_cfg(iac_cfg)

        return cls(
            vpc_cfg=vpc_cfg_fmt,
            django_srvs_cfg=django_srvs_cfg_fmt,
        )

    @staticmethod
    def serialize_vpc_cfg(iac_cfg: Config) -> dict:
        name = iac_cfg.get("vpc_name")
        add_nat = iac_cfg.get_bool("add_nat", default=False)

        return VPCCfg(
            vpc_name=name,
            add_nat=add_nat,
        )

    @staticmethod
    def serialize_django_srvs_cfg(iac_cfg: Config) -> list[DjangoServiceCfg]:
        django_srvs_cfg = iac_cfg.get_object("django_services", {})
        django_srvs_cfg_fmt = list()

        for name, config in django_srvs_cfg.items():
            django_project = config["django_project"]

            backend_cfg = config.get("backend")
            extra_container_args = dict()
            if "cpu" in backend_cfg:
                extra_container_args["cpu"] = backend_cfg["cpu"]
            if "memory" in backend_cfg:
                extra_container_args["memory"] = backend_cfg["memory"]
            if "lb_port" in backend_cfg:
                extra_container_args["lb_port"] = backend_cfg["lb_port"]
            if "container_port" in backend_cfg:
                extra_container_args["container_port"] = backend_cfg["container_port"]
            if "desired_count" in backend_cfg:
                extra_container_args["desired_count"] = backend_cfg["desired_count"]

            backend_cfg_fmt = BackendCfg(
                **extra_container_args,
            )

            db_cfg = config.get("db")
            db_cfg_fmt = DBCfg(
                engine=db_cfg["engine"],
                version=db_cfg["version"],
                family=db_cfg["family"],
            )

            django_srvs_cfg_fmt.append(
                DjangoServiceCfg(
                    service_name=name,
                    django_project=django_project,
                    backend_cfg=backend_cfg_fmt,
                    db_cfg=db_cfg_fmt,
                )
            )

        return django_srvs_cfg_fmt
