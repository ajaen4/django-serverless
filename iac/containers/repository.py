from pulumi_aws import ecr


class Repository:
    def __init__(self, name: str) -> None:
        self.ecr_repository = ecr.Repository(
            name,
            name=name,
            image_scanning_configuration=ecr.RepositoryImageScanningConfigurationArgs(
                scan_on_push=True,
            ),
            image_tag_mutability="MUTABLE",
            force_delete=True,
        )

    def get_repository(self) -> ecr.Repository:
        return self.ecr_repository
