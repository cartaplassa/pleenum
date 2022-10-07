from aiogram import types, Dispatcher
from aiogram.dispatcher.storage import FSMContext
from tgbot.misc.states import TurnBased
import logging
import json
from tgbot.database.declaration import User, Pleenum, Member, Session, engine
from tgbot.database.declaration import USERNAME_MAXLENGTH, PLEENUMNAME_MAXLENGTH


"""
    chat_id = str(message.chat["id"]), 
    user_id = str(message.from_id),
    user_name = message.from_user.first_name,
    pleenum_name = message.get_args()
"""


MAX_PLEENUMS = 3


async def pleenum_create(chat_id, user_id, user_name, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User {user_name} (ID:{user_id}) has requested creation of {pleenum_name} in chat {chat_id}")
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Creation ability check
    # Pleenum exists
    if local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first():
        logging.error("Pleenum exists")
        return "Pleenum with this name already exists in this chat"
    # Overusage
    elif user and user.pleenums_created >= MAX_PLEENUMS:
        logging.error("Max amount reached for this user")
        return "You have reached max amount of pleenums, remove any other one and try again"
    # Name not allowed
    elif pleenum_name == '' or len(pleenum_name) > PLEENUMNAME_MAXLENGTH:
        logging.error("Name not allowed")
        return f"Invalid name: should be <{PLEENUMNAME_MAXLENGTH} chars and not empty"
    
    # Check passed - pleenum can be created
    # If user unrecognized - adding to db
    if not user:
        local_session.add(User(
            telegram_id = user_id, 
            user_name = user_name[:USERNAME_MAXLENGTH], 
            pleenums_created = 0
        ))
    # Adding pleenum to db
    pleenum = Pleenum(
        name = pleenum_name,
        chat_id = chat_id,
        creator_id = user_id
    )
    local_session.add(pleenum)
    local_session.commit()
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    # Adding creator as member
    local_session.add(Member(
        pleenum_id = pleenum.id,
        member_id = user_id
    ))
    # Updating pleenum amount
    local_session.query(User).filter(User.telegram_id==user_id).first().pleenums_created += 1
    # Committing
    local_session.commit()
    # Reporting successful creation
    logging.info("Success!")
    return "Pleenum was created"


async def pleenum_remove(chat_id, user_id, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User ID:{user_id} has requested removal of {pleenum_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Removal ability check
    # Pleenum not found
    if not pleenum:
        logging.error("Not found")
        return "This is not the pleenum you are looking for"
    # Requestor is not the creator
    elif not user or pleenum.creator_id != user_id:
        logging.error("Not the creator")
        return "You are not the creator of this pleenum"

    # Check passed - pleenum can be removed
    # Removing all membership records
    for each in local_session.query(Member).filter(Member.pleenum_id==pleenum.id).all():
        local_session.delete(each)
    # Removing pleenum from db
    local_session.delete(pleenum)
    # Updating pleenum amount
    user.pleenums_created -= 1
    # Garbage collection - user (will obviously reset username after recreation)
    if user.pleenums_created == 0 and not local_session.query(Member).filter(Member.member_id==user_id).all():
        local_session.delete(user)
        logging.info("User is removed after deleting their last record")
    # Committing
    local_session.commit()
    # Reporting successful creation
    logging.info("Success!")
    return "Pleenum was removed"


async def pleenum_join(chat_id, user_id, user_name, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User {user_name} (ID:{user_id}) has requested to join {pleenum_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Joining ability check
    # Pleenum not found
    if not pleenum:
        logging.error("Not found")
        return "Pleenum with this name doesn't exist. Go ahead, create one!"
    # User is a member already
    if local_session.query(Member).filter(Member.pleenum_id==pleenum.id, Member.member_id==user_id).first():
        logging.error("Already joined")
        return "You are already a member of this pleenum"

    # Check passed - pleenum can be joined
    # If user unrecognized - adding to db
    if not user:
        local_session.add(User(
            telegram_id = user_id, 
            user_name = user_name[:USERNAME_MAXLENGTH], 
            pleenums_created = 0
        ))
    # Adding membership record to db
    local_session.add(Member(
        pleenum_id = pleenum.id,
        member_id = user_id
    ))
    # Committing
    local_session.commit()
    # Reporting successful creation
    logging.info("Success!")
    return "Pleenum was joined"


async def pleenum_leave(chat_id, user_id, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User ID:{user_id} has requested to leave {pleenum_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    membership = local_session.query(Member).filter(Member.pleenum_id==pleenum.id, Member.member_id==user_id).first()
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Leaving ability check
    # Pleenum not found
    if not pleenum:
        logging.error("Not found")
        return "Pleenum with this name doesn't exist"
    # User is not a member
    elif not user or not membership:
        logging.error("Was not a member")
        return "You were not a member of this pleenum to begin with"
    
    # Check passed - pleenum can be left
    # Removing membership record
    local_session.delete(membership)
    # Garbage collection - pleenum
    if not local_session.query(Member).filter(Member.pleenum_id==pleenum.id).all():
        local_session.query(User).filter(User.telegram_id==pleenum.creator_id).first().pleenums_created -= 1
        local_session.delete(pleenum)
        logging.info("Pleenum is removed after its last member left")
    # Garbage collection - user (will obviously reset username after recreation)
    if user.pleenums_created == 0 and not local_session.query(Member).filter(Member.member_id==user_id).all():
        local_session.delete(user)
        logging.info("User is removed after deleting their last record")
    # Committing
    local_session.commit()
    # Reporting successful creation
    logging.info("Success!")
    return "Pleenum was left"


async def pleenum_call(chat_id, user_id, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User (ID:{user_id}) has requested to call {pleenum_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    # Check for pleenum
    if not pleenum:
        logging.error("Not found")
        return "Pleenum with this name doesn't exist"
    
    members = [each.member_id for each in local_session.query(Member).filter(Member.pleenum_id==pleenum.id).all()]
    logging.warning(members)
    users = local_session.query(User).filter(User.telegram_id.in_(members)).all()
    logging.warning(users) # <a href="tg://user?id={each.telegram_id}">{each.user_name}</a>
    return 'Calling pleenum: ' + ', '.join([f'<a href="tg://user?id={each.telegram_id}">{each.user_name}</a>' for each in users])


# TODO later and add changing username functionality
# async def pleenum_rename(chat_id, user_id, pleenum_name, new_name) -> str:
#     with open("tgbot/misc/pleenums.json", 'r') as f:
#         pleenums = json.load(f)
#     if chat_id not in pleenums['pleenums'] or pleenum_name not in pleenums['pleenums'][chat_id] or pleenums['pleenums'][chat_id][pleenum_name]['leader'] != user_id:
#         status = f"Can't rename pleenum {pleenum_name}"
#     else:
#         logging.info(f'Pleenum {pleenum_name} exists')
#         del pleenums['pleenums'][chat_id][pleenum_name]
#         pleenums['usage'][user_id] -= 1
#         status = f"Pleenum {pleenum_name} removed"
#         with open("tgbot/misc/pleenums.json", 'w') as f:
#             json.dump(pleenums, f, indent=4)
#     return status


async def pleenum_default(message: types.Message, state: FSMContext):
    await TurnBased.Index.set()
    await message.answer(
        "What action do you want to perform?\ncreate/remove/join/leave/call\nAlso, remind me to add inline buttons"
    )


async def choose_action(message: types.Message, state: FSMContext):
    command = message.text.lower()
    if command not in ['create', 'remove', 'join', 'leave', 'call']:
        await message.answer('Command unrecognized')
        await state.reset_state()
    else:
        await state.update_data(command=command)
        await TurnBased.Command.set()
        await message.answer(
            'Enter the pleenum name'
        )


async def perform_action(message: types.Message, state: FSMContext):
    command = await state.get_data()
    command = command['command']
    chat_id = message.chat["id"]
    user_id = message.from_id
    user_name = message.from_user.first_name
    pleenum_name = message.text

    if command == 'create':
        await message.answer(await pleenum_create(chat_id, user_id, user_name, pleenum_name))
    elif command == 'remove':
        await message.answer(await pleenum_remove(chat_id, user_id, pleenum_name))
    elif command == 'join':
        await message.answer(await pleenum_join(chat_id, user_id, user_name, pleenum_name))
    elif command == 'leave':
        await message.answer(await pleenum_leave(chat_id, user_id, pleenum_name))
    elif command == 'call':
        await message.answer(await pleenum_call(chat_id, user_id, pleenum_name))
    await state.reset_state()


async def create(message: types.Message):
    await message.answer(await pleenum_create(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        user_name = message.from_user.first_name,
        pleenum_name = message.get_args()
    ))


async def remove(message: types.Message):
    await message.answer(await pleenum_remove(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        pleenum_name = message.get_args()
    ))


async def join(message: types.Message):
    await message.answer(await pleenum_join(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        user_name = message.from_user.first_name,
        pleenum_name = message.get_args()
    ))


async def leave(message: types.Message):
    await message.answer(await pleenum_leave(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        pleenum_name = message.get_args()
    ))


async def call(message: types.Message):
    await message.answer(await pleenum_call(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        pleenum_name = message.get_args()
    ))


def register_group_tag(dp: Dispatcher):
    dp.register_message_handler(pleenum_default, commands=['pleenum'])
    dp.register_message_handler(choose_action, state=TurnBased.Index)
    dp.register_message_handler(perform_action, state=TurnBased.Command)
    dp.register_message_handler(create, commands=['create'])
    dp.register_message_handler(remove, commands=['remove'])
    dp.register_message_handler(join, commands=['join'])
    dp.register_message_handler(leave, commands=['leave'])
    dp.register_message_handler(call, commands=['call'])
