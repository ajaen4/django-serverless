import pulumi
from pulumi_aws import ecr
import pulumi_docker as docker


class Image:
    def __init__(self, name: str, ecr_repository: ecr.Repository):
        self.name = name
        self.ecr_repository = ecr_repository

    def push_image(self, version: str):
        image_tag = f"{self.name}-{version}"
        self._authenticate()
        image = docker.Image(
            f"{self.name}-image",
            build=docker.DockerBuildArgs(
                args={
                    "BUILDKIT_INLINE_CACHE": "1",
                },
                context="../django_app/",
                dockerfile="../django_app/Dockerfile",
                platform="linux/amd64",
            ),
            image_name=self.ecr_repository.repository_url.apply(
                lambda repository_url: f"{repository_url}:{image_tag}"
            ),
            registry=docker.RegistryArgs(
                username="AWS",
                password=pulumi.Output.secret(self.auth_token.password),
                server=self.ecr_repository.repository_url,
            ),
        )

        return image.image_name

    def _authenticate(self):
        self.auth_token = ecr.get_authorization_token_output(
            registry_id=self.ecr_repository.registry_id
        )
