from dependency_injector import containers, providers

from core.settings_model import Settings


class ConfigContainer(containers.DeclarativeContainer):
    # config loading from pydantic
    config = providers.Configuration(pydantic_settings=[Settings()])

    # di 동작 범위 선언
    wiring_config = containers.WiringConfiguration(
        modules=[
            __name__,
        ],
    )


config_container = ConfigContainer()
# This is used for when config required before container init.
# e.g. main.py, migrations
config = config_container.config
