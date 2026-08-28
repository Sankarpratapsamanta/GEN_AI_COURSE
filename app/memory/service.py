from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.models.memory import Memory
from app.schemas.memory_schema import MemoryDecision
from app.llm import llm
from app.database.session import AsyncSessionLocal

structured_memory_llm =(llm.with_structured_output(MemoryDecision))


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
async def save_memory(user_id:str,content:str):
    async with AsyncSessionLocal() as session:
        memory = Memory(
            user_id=user_id,
            content=content
        )

        session.add(memory)
        await session.commit()
        return memory

async def get_memory(user_id:str):

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Memory).where(Memory.user_id == user_id).order_by(
                Memory.created_at.desc())
        )

        messages = result.scalars().all()


        return [
            memory.content
            for memory in messages
        ]

async def extract_memory(message:str):
    result = await structured_memory_llm.ainvoke(
        [
            {
                "role":"system",
                "content":"""
                You are a long-term memory extraction system.
                
                Only remember information that is useful across future conversations.
                
                Good example:
                
                - User's name
                - User's profession
                - User's technical preferences
                - Persistent preferences
                - Ongoing projects
                
                Do Not remember:
                
                - Greetings
                - Temporary question
                - One-time requests
                - Normal conversation
                - Information that won't be useful later
                
                Return whether the message should be remebered and the concise memory if appropriate.
                """
            },
            {
                "role":"user",
                "content":message
            }
        ]
    )

    return result

