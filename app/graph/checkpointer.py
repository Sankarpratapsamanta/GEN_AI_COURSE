from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings

checkpointer =None
checkpointer_context = None


async def init_checkpointer():
    global checkpointer
    global checkpointer_context

    database_url=(
        settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    )

    checkpointer_context = AsyncPostgresSaver.from_conn_string(database_url)

    checkpointer = await checkpointer_context.__aenter__()

    await  checkpointer.setup()

    return checkpointer

def get_checkpointer():
    if checkpointer is None:
        raise RuntimeError(
            "Checkpointer is not initialized"
        )
    return checkpointer

async def close_checkpointer():
    global checkpointer
    global checkpointer_context

    if checkpointer_context:
        await checkpointer_context.__aexit__(None,None,None)

    checkpointer = None
    checkpointer_context = None