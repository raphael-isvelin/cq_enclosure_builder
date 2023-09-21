class ProjectInfo:
    def __init__(
        self,
        name: str = "My project",
        version: str = "1.0.0"
    ):
        self.name = name
        self.version = version

    def __str__(self):
        return f"{self.name} v{self.version}"