from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db.models import Post


async def get_post(
    session: AsyncSession, chat_id, user_id: int, message_id: int
) -> Post:
    result = await session.execute(
        select(Post).filter(
            Post.chat_id == chat_id,
            Post.user_id == user_id,
            Post.message_id == message_id,
        )
    )
    return result.scalars().first()


async def create_post(
    session: AsyncSession,
    chat_id: str,
    user_id: str,
    message_id: str,
    group_topic: str,
    text: str | None = None,
    photo: str | None = None,
    caption: str | None = None,
    assessment: int = 0,
) -> Post:
    db_post = Post(
        chat_id=chat_id,
        user_id=user_id,
        message_id=message_id,
        group_topic=group_topic,
        text=text,
        photo=photo,
        caption=caption,
        assessment=assessment,
    )
    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)
    return db_post


async def voting(
    session: AsyncSession, chat_id, user_id: int, message_id: int, vote: bool
) -> Post:
    db_post = await get_post(session, chat_id, user_id, message_id)
    if not db_post:
        raise NoResultFound("Post not found")

    if vote:
        db_post.assessment += 1
    else:
        db_post.assessment -= 1

    await session.commit()
    await session.refresh(db_post)

    return db_post
