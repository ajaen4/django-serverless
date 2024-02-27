from pulumi import Config

from networking import Networking
from containers import ECSService

config = Config()

networking = Networking(config)
ECSService(networking.get_vpc_id())
