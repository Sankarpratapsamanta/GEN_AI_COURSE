from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.models.memory import Memory


# SHORT TERM MEMORY
async def save_message(session:AsyncSession,user_id:str,conversation_id:str,role:str,content:str):

    message = Message(
        user_id = user_id,
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message

async def get_messages(session:AsyncSession,user_id:str,conversation_id:str):
    result = await session.execute(
        select(Message).where(Message.user_id == user_id,Message.conversation_id == conversation_id).order_by(Message.id.asc())
    )

    messages = result.scalars().all()

    return [
        {
            "role":message.role,
            "content":message.content,
        }
        for message in messages
    ]



# LONG TERM MEMORY
async def save_memory(session:AsyncSession,user_id:str,content:str):
    memory = Memory(
        user_id=user_id,
        content=content
    )

    session.add(memory)
    await session.commit()
    return memory

async def get_memory(session:AsyncSession,user_id:str):
    result = await session.execute(
        select(Message).where(Message.user_id == user_id).order_by(
            Message.created_at.desc())
    )

    messages = result.scalars().all()

    return [
        memory.content
        for memory in messages
    ]