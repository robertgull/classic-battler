import asyncio
from src.app import create_app


async def test():
    app = await create_app()
    print(app)


asyncio.run(test())
