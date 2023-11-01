import os

import click
import uvicorn

from application.core.config.config_container import config


@click.command()
@click.option(
    "--env",
    type=click.Choice(["local", "dev", "prod"], case_sensitive=False),
    default="local",
)
@click.option(
    "--debug",
    type=click.BOOL,
    is_flag=True,
    default=False,
)
def main(env: str, debug: bool):
    os.environ["ENV_FILE"] = f".env.{env}"
    print(f"RUNNING ENV is {env}")
    os.environ["DEBUG"] = str(debug)
    uvicorn.run(
        app="application.server:app",
        host=config.APP_HOST(),
        port=config.APP_PORT(),
        reload=True if config.ENV() != "production" else False,
        workers=1,
    )


if __name__ == "__main__":
    main()
