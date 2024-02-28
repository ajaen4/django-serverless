from pulumi import Config

from networking import Networking
from containers import ECSServices
from input_schemas import Input

config = Config()

input = Input.from_cfg(config)

networking = Networking(input.vpc_cfg)

ECSServices(networking, input.django_srvs_cfg)
