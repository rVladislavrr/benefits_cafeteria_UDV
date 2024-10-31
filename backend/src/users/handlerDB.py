import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from ..config import settings
from .helper import get_payload_refresh, get_active_payload
from .models import UsersORM, UserProfilesORM
from sqlalchemy import select, update, asc, desc, func
from fastapi import HTTPException, Depends, status, Query
from .shemas import UserRegister, UserAuthorization, UserAll, UserUpdate
from ..base import get_async_session


async def check_conflict_user(userData, session):
    query = select(UsersORM).where(UsersORM.email == userData.email)
    if (await session.execute(query)).scalar():
        raise HTTPException(status_code=409, detail="User already exists")


async def register_user_db(userData: UserRegister, session: AsyncSession = Depends(get_async_session)):
    await check_conflict_user(userData, session)
    hash_password = hashlib.sha256(userData.password.encode('utf-8')).hexdigest()
    userOrm = UsersORM(email=userData.email, hash_password=hash_password)
    session.add(userOrm)
    await session.flush()
    userProfile = UserProfilesORM(user_uuid=userOrm.uuid,
                                  firstname=userData.firstname,
                                  lastname=userData.lastname,
                                  middlename=userData.middlename,
                                  )
    session.add(userProfile)
    await session.commit()

    return userOrm


async def find_auth_user(user_Auth: UserAuthorization, session: AsyncSession = Depends(get_async_session)):
    query = select(UsersORM).where(user_Auth.email == UsersORM.email)
    user = (await session.execute(query)).scalar()

    enter_hash_password = hashlib.sha256(user_Auth.password.encode('utf-8')).hexdigest()

    if not user or enter_hash_password != user.hash_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='email or password wrong')
    return user


async def get_user_uuid_req(user_uuid: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(UsersORM).where(user_uuid == UsersORM.uuid).options(selectinload(UsersORM.benefits_records))
        if user := (await session.execute(query)).scalar():
            return user
        raise Exception
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")


async def get_user_uuid(user_uuid: str, session: AsyncSession = Depends(get_async_session)):
    try:
        query = select(UsersORM).where(user_uuid == UsersORM.uuid)
        if user := (await session.execute(query)).scalar():
            return user
        raise Exception
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")


def get_user_token_sub_creator(
        name_foo,
):
    async def get_user_token_sub(payload=Depends(name_foo), session: AsyncSession = Depends(get_async_session)):
        try:
            return await get_user_uuid(payload.get('uuid'), session)
        except HTTPException:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token invalid")

    return get_user_token_sub


refresh_get_user = get_user_token_sub_creator(get_payload_refresh)


async def get_users_offset(start: int = Query(0, ge=0), offset: int = Query(5, ge=1, le=20),
                           order_by: str = Query('name'),
                           sort_order: str = Query("asc"),
                           session: AsyncSession = Depends(get_async_session)):
    order = {"name": UserProfilesORM.firstname,
             "email": UsersORM.email,
             "create_at": UsersORM.create_at,
             "job_title": UserProfilesORM.job_title}.get(order_by)

    if not order:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, )
    query = select(UsersORM).join(UserProfilesORM)

    if sort_order == "asc":
        query = query.order_by(asc(order))
    elif sort_order == 'desc':
        query = query.order_by(desc(order))
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    query = query.slice(start, start + offset)
    users = (await session.execute(query)).unique().scalars()
    query = select(func.count()).select_from(UsersORM)
    result = await session.execute(query)
    count = result.scalar()
    return {'users': [UserAll.model_validate(u, from_attributes=True) for u in users], 'len': count}


async def update_user_db(user_id: str, new_user: UserUpdate, session: AsyncSession = Depends(get_async_session)):
    attributs = ['firstname', 'lastname', 'middlename', 'legal_entity', 'job_title']
    profile = {}

    if any([hasattr(new_user, att) for att in attributs]):
        for att in attributs:
            if hasattr(new_user, att):
                if attribute := getattr(new_user, att):
                    profile[att] = attribute
                delattr(new_user, att)
    flag = False
    if new_user.dict(exclude_unset=True):
        try:
            stmt = update(UsersORM).where(user_id == UsersORM.uuid).values(**new_user.dict(exclude_unset=True))
            await session.execute(stmt)
            flag = True
        except:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="conflict")
    if profile:
        stmt2 = update(UserProfilesORM).where(user_id == UserProfilesORM.user_uuid).values(**profile)
        await session.execute(stmt2)
        flag = True

    if not flag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty")

    await session.commit()
    user = await get_user_uuid(user_id, session)

    return user


async def get_FirstLastName(user=Depends(get_active_payload), session=Depends(get_async_session)):
    userOrm = await get_user_uuid(user.uuid, session)
    return {"firstname": userOrm.profile.firstname, "lastname": userOrm.profile.lastname,
            'super_user': userOrm.super_user}


async def get_coins_db(user=Depends(get_active_payload), session=Depends(get_async_session)):
    userOrm = await get_user_uuid(user.uuid, session)
    return {'ucoin': userOrm.ucoin}


async def get_user_info_benefit(user_inf=Depends(get_active_payload), session=Depends(get_async_session)):
    query = select(UsersORM).where(user_inf.uuid == UsersORM.uuid).options(selectinload(UsersORM.benefits_records))
    userOrm = (await session.execute(query)).scalar()
    return userOrm


async def create_super_user(session=Depends(get_async_session)):
    try:
        hash_password = hashlib.sha256(settings.password.encode('utf-8')).hexdigest()
        userOrm = UsersORM(email=settings.email, hash_password=hash_password)
        session.add(userOrm)
        await session.flush()
        userProfile = UserProfilesORM(user_uuid=userOrm.uuid,
                                      firstname=settings.firstname,
                                      lastname=settings.lastname,
                                      middlename=settings.middlename,
                                      )
        session.add(userProfile)
    except Exception as e:
        print(e)
        return e
    await session.commit()
    print(userOrm)
    return
