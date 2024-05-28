import pulumi
from pulumi_aws import ecr
import pulumi_docker as docker


class Image:
    def __init__(
        self, name: str, django_project: str, ecr_repository: ecr.Repository
    ) -> None:
        self.name = name
        self.django_project = django_project
        self.ecr_repository = ecr_repository

    def push_image(self, version: str) -> pulumi.Output:
        image_tag = f"{self.name}-{version}"
        self._authenticate()
        image = docker.Image(
            f"{self.name}-image",
            build=docker.DockerBuildArgs(
                args={
                    "BUILDKIT_INLINE_CACHE": "1",
                },
                context=f"../django_services/{self.django_project}/",
                dockerfile=f"../django_services/{self.django_project}/Dockerfile",
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

    def _authenticate(self) -> None:
        self.auth_token = ecr.get_authorization_token_output(
            registry_id=self.ecr_repository.registry_id
        )
