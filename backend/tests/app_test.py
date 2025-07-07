import asyncio
from backend.src.app import create_app


async def test():
    app = await create_app()
    print(app)


asyncio.run(test())
