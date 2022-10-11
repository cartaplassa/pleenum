from aiogram import types, Dispatcher
from aiogram.dispatcher.storage import FSMContext
from tgbot.misc.states import TurnBased
import logging
import json
from tgbot.database.declaration import User, Pleenum, Member, Session, engine
from tgbot.database.declaration import USERNAME_MAXLENGTH, PLEENUMNAME_MAXLENGTH


MAX_PLEENUMS = 3


async def pleenum_create(chat_id, user_id, user_name, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User {user_name} (ID:{user_id}) has requested creation of {pleenum_name} in chat {chat_id}")
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Creation ability check
    # Pleenum exists
    if local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first():
        logging.error("Pleenum exists")
        return f"Pleenum <code>{pleenum_name}</code> already exists in this chat"
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
            user_name = user_name[:USERNAME_MAXLENGTH]
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
    return f"Pleenum <code>{pleenum_name}</code> was created"


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
        return f"You are not the creator of <code>{pleenum_name}</code>"

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
    return f"Pleenum <code>{pleenum_name}</code> was removed"


async def pleenum_join(chat_id, user_id, user_name, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User {user_name} (ID:{user_id}) has requested to join {pleenum_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Joining ability check
    # Pleenum not found
    if not pleenum:
        logging.error("Not found")
        return f"Pleenum <code>{pleenum_name}</code> doesn't exist. Go ahead, create one!"
    # User is a member already
    if local_session.query(Member).filter(Member.pleenum_id==pleenum.id, Member.member_id==user_id).first():
        logging.error("Already joined")
        return f"You are already a member of <code>{pleenum_name}</code>"

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
    return f"Pleenum <code>{pleenum_name}</code> was joined"


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
        return f"Pleenum <code>{pleenum_name}</code> doesn't exist"
    # User is not a member
    elif not user or not membership:
        logging.error("Was not a member")
        return f"You were not a member of <code>{pleenum_name}</code> to begin with"
    
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
    return f"Pleenum <code>{pleenum_name}</code> was left"


async def pleenum_call(chat_id, user_id, pleenum_name) -> str:
    local_session = Session(bind=engine)
    logging.info(f"User (ID:{user_id}) has requested to call {pleenum_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==pleenum_name, Pleenum.chat_id==chat_id).first()
    # Check for pleenum
    if not pleenum:
        logging.error("Not found")
        return f"Pleenum <code>{pleenum_name}</code> doesn't exist"
    
    members = [each.member_id for each in local_session.query(Member).filter(Member.pleenum_id==pleenum.id).all()]
    logging.warning(members)
    users = local_session.query(User).filter(User.telegram_id.in_(members)).all()
    logging.warning(users)
    return f'Calling pleenum <code>{pleenum_name}</code>: ' + ', '.join([f'<a href="tg://user?id={each.telegram_id}">{each.user_name}</a>' for each in users])


async def pleenum_change_nickname(user_id, new_nick):
    local_session = Session(bind=engine)
    logging.info(f"User (ID:{user_id}) has requested to change nickname to {new_nick}")
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Check if user is active
    if user.pleenums_created == 0 and not local_session.query(Member).filter(Member.member_id==user_id).all():
        local_session.delete(user)
        logging.info("User is not recorded in DB")
        return "Create or join any pleenum first"
    
    # Changing nickname
    user.user_name = new_nick[:USERNAME_MAXLENGTH]

    # Committing
    local_session.commit()
    # Reporting successful creation
    logging.info("Success!")
    return "Nickname was changed"


async def pleenum_rename(chat_id, user_id, old_name, new_name):
    local_session = Session(bind=engine)
    logging.info(f"User (ID:{user_id}) has requested to change pleenum {old_name} to {new_name} in chat {chat_id}")
    pleenum = local_session.query(Pleenum).filter(Pleenum.name==old_name, Pleenum.chat_id==chat_id).first()
    user = local_session.query(User).filter(User.telegram_id==user_id).first()
    # Renaming ability check
    # Pleenum not found
    if not pleenum:
        logging.error("Not found")
        return "This is not the pleenum you are looking for"
    # Requestor is not the creator
    elif not user or pleenum.creator_id != user_id:
        logging.error("Not the creator")
        return f"You are not the creator of <code>{old_name}</code>"
    
    # Changing name
    pleenum.name = new_name

    # Committing
    local_session.commit()
    # Reporting successful creation
    logging.info("Success!")
    return f"Pleenum was renamed to <code>{new_name}</code>"


async def pleenum_default(message: types.Message, state: FSMContext):
    await TurnBased.Index.set()
    await message.answer(
        "What action do you want to perform?\ncreate/remove/join/leave/call\nAlso, remind me to add inline buttons"
    )


async def choose_action(message: types.Message, state: FSMContext):
    command = message.text.lower()
    if command in ['create', 'remove', 'join', 'leave', 'call', 'newnick']:
        await state.update_data(command=command)
        await TurnBased.Command.set()
        await message.answer(
            'Enter your new nickname' if command == 'newnick' else 'Enter the pleenum name'
        )
    elif command == 'rename':
        pass
    else:
        await message.answer('Command unrecognized')
        await state.reset_state()


async def perform_action(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    command = state_data['command']
    chat_id = message.chat["id"]
    user_id = message.from_id
    user_name = message.from_user.first_name
    name_from_text = message.text

    if command == 'create':
        await message.answer(await pleenum_create(
            chat_id = chat_id, 
            user_id = user_id, 
            user_name = user_name, 
            pleenum_name = name_from_text
        ))
        await state.reset_state()
    elif command == 'remove':
        await message.answer(await pleenum_remove(
            chat_id = chat_id, 
            user_id = user_id, 
            pleenum_name = name_from_text
        ))
        await state.reset_state()
    elif command == 'join':
        await message.answer(await pleenum_join(
            chat_id = chat_id, 
            user_id = user_id, 
            user_name = user_name, 
            pleenum_name = name_from_text
        ))
        await state.reset_state()
    elif command == 'leave':
        await message.answer(await pleenum_leave(
            chat_id = chat_id, 
            user_id = user_id, 
            pleenum_name = name_from_text
        ))
        await state.reset_state()
    elif command == 'call':
        await message.answer(await pleenum_call(
            chat_id = chat_id, 
            user_id = user_id, 
            pleenum_name = name_from_text
        ))
        await state.reset_state()
    elif command == 'newnick':
        await message.answer(await pleenum_change_nickname(
            user_id = user_id, 
            new_nick = name_from_text
        ))
        await state.reset_state()
    elif command == 'rename':
        await message.answer('Enter new name')
        await state.update_data(
            chat_id = chat_id, 
            user_id = user_id, 
            old_name = name_from_text
        )
        await TurnBased.NewName.set()


async def perform_rename(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    await message.answer(await pleenum_rename(
        chat_id = state_data['chat_id'],
        user_id = state_data['user_id'],
        old_name = state_data['old_name'],
        new_name = message.text
    ))
    await state.reset_state()


async def rename(message: types.Message, state: FSMContext):
    # Dunno if useful \|/
    await TurnBased.Name.set()
    await message.answer('Enter new name')
    await state.update_data(
        chat_id=message.chat["id"], 
        user_id=message.from_id, 
        old_name=message.get_args()
    )
    await TurnBased.NewName.set()


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


# Admin function
async def add(message: types.Message): 
    await message.answer(await pleenum_join(
        chat_id = message.chat["id"], 
        user_id = message.reply_to_message.from_id,
        user_name = message.reply_to_message.from_user.first_name,
        pleenum_name = message.get_args()
    ))


async def leave(message: types.Message):
    await message.answer(await pleenum_leave(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        pleenum_name = message.get_args()
    ))


# Admin function
async def purge(message: types.Message):
    await message.answer(await pleenum_leave(
        chat_id = message.chat["id"], 
        user_id = message.reply_to_message.from_id,
        pleenum_name = message.get_args()
    ))


async def call(message: types.Message):
    await message.answer(await pleenum_call(
        chat_id = message.chat["id"], 
        user_id = message.from_id,
        pleenum_name = message.get_args()
    ))


async def change_nickname(message: types.Message):
    await message.answer(await pleenum_change_nickname(
        user_id = message.from_id,
        new_nick = message.get_args()
    ))


def register_group_tag(dp: Dispatcher):
    dp.register_message_handler(pleenum_default, commands=['pleenum'])
    dp.register_message_handler(choose_action, state=TurnBased.Index)
    dp.register_message_handler(perform_action, state=TurnBased.Command)
    dp.register_message_handler(perform_rename, state=TurnBased.NewName)
    dp.register_message_handler(create, commands=['create'])
    dp.register_message_handler(remove, commands=['remove'])
    dp.register_message_handler(join, commands=['join'])
    dp.register_message_handler(add, commands=['add'], is_admin=True)
    dp.register_message_handler(leave, commands=['leave'])
    dp.register_message_handler(purge, commands=['purge'], is_admin=True)
    dp.register_message_handler(call, commands=['call'])
    dp.register_message_handler(rename, commands=['rename'])
    dp.register_message_handler(change_nickname, commands=['newnick'])
