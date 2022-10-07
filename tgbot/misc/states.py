from aiogram.dispatcher.filters.state import StatesGroup, State


class TurnBased(StatesGroup):
    Index = State()
    Command = State()
    Name = State()
