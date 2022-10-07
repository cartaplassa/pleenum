
*(описание на русском ниже)*

# Pleenum
<img height="30em" src="https://raw.githubusercontent.com/anki-geo/ultimate-geography/a44a569a922e1d241517113e2917736af808eed7/src/media/flags/ug-flag-united_kingdom.svg" alt="english" align = "center"/> 

A simple description

## Installation & first launch
1) **[Acquire the token from @BotFather](https://t.me/botfather)**, more info on registering bots [here](https://core.telegram.org/bots#how-do-i-create-a-bot)
2) **Install [Python](https://www.python.org/downloads/)** v.>=3.10 (not tested on older versions)
3) **Get a local copy** - download the source or use `git clone`
4) **Open the local copy** - navigate through console or open terminal directly in the folder
5) **Rename `.env.dist` to `.env`**
6) **Specify your token in `.env`**, other fields can be left as they are

![Screenshot_20221008_014535](https://user-images.githubusercontent.com/99555654/194672469-68e4fc85-5ae2-4f8e-8bef-40dd5ce357e3.png)

7) (Optional) *Create and activate venv*
```
python -m venv venv
source venv/bin/activate
```
8) **Install dependencies** - 
`pip install -r requirements.txt`
9) **Launch the bot** - 
`python bot.py`.
The database will be created on the first launch here: `./tgbot/database/main.db`

## Usage 

*There is a WIP command `/pleenum` that will include inline buttons, but for now it only acts as an alternative to write other commands in one line.*

![Screenshot_20221007_235303](https://user-images.githubusercontent.com/99555654/194669231-b6966739-7415-432a-9804-1571fa6c612a.png)

- First step is to create a pleenum. Just use the `/create` command and pass your desired name as an argument. There is a 64-char name length limit, which is more than reasonable, but the shorter - the better, you'll have to write the name each time you call the pleenum.

![Screenshot_20221007_233636](https://user-images.githubusercontent.com/99555654/194669270-6ffe27d0-7f34-46fe-9438-4562ef638190.png)

*The bot keeps track of how many pleenums are created by a user and stores the amount in the database. The limit of pleenums (3 by default) that can be created is a constant `MAX_PLEENUMS` located in `./tgbot/handlers/group_tag.py`. It is not hardcoded in the database and can be rewritten at any time, but will require restarting the bot to take effect.*

![Screenshot_20221007_235449](https://user-images.githubusercontent.com/99555654/194669300-631611d9-5d18-4db5-b7bd-e8af084798b4.png)

- Users can join pleenums by using the `/join` command with specifying the name of the pleenum.

![Screenshot_20221007_233953](https://user-images.githubusercontent.com/99555654/194669316-3e93cad5-6315-46c2-b102-6b57389234df.png)

- Call the pleenum with `/call` command and its name. Every member will get a notification that they were mentioned in the chat. But be aware that there are currently no restrictions on how often this command can be used and it is not required to be a member to call a pleenum.

![Screenshot_20221007_234958](https://user-images.githubusercontent.com/99555654/194669333-aa153f82-6dcb-4912-a9d9-8e6885dcbbc0.png)

- You can remove a pleenum with the respective `/remove` command. All the membership records in the DB will be purged in the process. As of now, only the creator of the pleenum can remove it.

![Screenshot_20221007_235038](https://user-images.githubusercontent.com/99555654/194669341-0ad33b18-8e33-44aa-b299-0eb50c0c13a1.png)

- Enter `/leave` to leave the pleenum. When the last member leaves the pleenum, it will be automatically removed.

![Screenshot_20221007_235021](https://user-images.githubusercontent.com/99555654/194669348-418b2bb3-cb6c-4a82-b592-acec07fb7a9c.png)

## A note on DB organization
- DB structure:

![Screenshot_20221008_000327](https://user-images.githubusercontent.com/99555654/194669364-4b893ca3-e44b-4f4a-9902-4835531770d2.png)
- As a way to keep the storage capacity low, users are entered in the database when they create or join their first pleenum and purged when they remove or leave their last. This has to be kept in mind later, when the option to change nickname is implemented, because if the user creates or joins the pleenum again, their custom nickname will be reset in the process.



# Pleenum
<img height="30em" src="https://raw.githubusercontent.com/anki-geo/ultimate-geography/a44a569a922e1d241517113e2917736af808eed7/src/media/flags/ug-flag-russia.svg" alt="russian" align = "center"/>

Простое описание

## Установка и первый запуск
1) **[Получите токен у @BotFather](https://t.me/botfather)**, узнать больше о процессе регистрации ботов [здесь](https://core.telegram.org/bots#how-do-i-create-a-bot)
2) **Установите [Python](https://www.python.org/downloads/)** версии 3.10 или выше (тестов на совместимость с предыдущими версиями не проводилось)
3) **Сохраните локальную копию** - скачайте исходный код с сайта или воспользуйтесь `git clone`
4) **Переместитесь в локальную копию** через консоль или открыв терминал в файловом менеджере
5) **Переименуйте файл `.env.dist` в `.env`**
6) **В файле `.env` укажите полученный токен**, другие значения можно оставить как есть

![Screenshot_20221008_014535](https://user-images.githubusercontent.com/99555654/194672469-68e4fc85-5ae2-4f8e-8bef-40dd5ce357e3.png)

7) (Не обязательно) *Создайте и активируйте виртуальное окружение*
```
python -m venv venv
source venv/bin/activate
```
8) **Установите зависимости** - 
`pip install -r requirements.txt`
9) **Запустите бота** - 
`python bot.py`.
База данных будет создана при первом запуске здесь: `./tgbot/database/main.db`

## Использование

*В боте присутствует команда `/pleenum`, которая в данный момент в разработке. Пока инлайн-кнопки не реализованы, ей можно воспользоваться и вводить действия и имена поочерёдно, в отличие от остальных команд, где каждое действие прописывается в одном сообщении.*

![Screenshot_20221007_235303](https://user-images.githubusercontent.com/99555654/194669231-b6966739-7415-432a-9804-1571fa6c612a.png)

- Для начала создайте плинум. Введите команду `/create` и укажите желаемое имя. На длину имени установлен лимит в 64 символа, но чем короче имя тем лучше - его надо вводить при каждом вызове.

![Screenshot_20221007_233636](https://user-images.githubusercontent.com/99555654/194669270-6ffe27d0-7f34-46fe-9438-4562ef638190.png)

*Для каждого пользователя бот хранит в базе данных количество созданных им плинумов. Максимальное разрешённое количество (по умолчанию - 3) прописано в константе `MAX_PLEENUMS` , расположенной в `./tgbot/handlers/group_tag.py`. Этот лимит не хранится в БД и может быть переписан в любое время, но изменение будет принято только после перезапуска бота.*

![Screenshot_20221007_235449](https://user-images.githubusercontent.com/99555654/194669300-631611d9-5d18-4db5-b7bd-e8af084798b4.png)

- Пользователи могут присоединиться к плинуму, воспольовавшись командой `/join` и указав имя плинума.

![Screenshot_20221007_233953](https://user-images.githubusercontent.com/99555654/194669316-3e93cad5-6315-46c2-b102-6b57389234df.png)

- Вызов плинума осуществляется с помощью команды `/call` и его названия. Каждый участник плинума получит уведомление о теге в чате. Однако в данный момент не реализовано никаких ограничений частоты использования команды. Также не обязательно быть участником плинума, чтобы его вызвать.

![Screenshot_20221007_234958](https://user-images.githubusercontent.com/99555654/194669333-aa153f82-6dcb-4912-a9d9-8e6885dcbbc0.png)

- Плинум может быть удалён с помощью команды `/remove`. Все записи об участии пользователей в плинуме будут удалены из базы данных. В данный момент удалить плинум может только его создатель.

![Screenshot_20221007_235038](https://user-images.githubusercontent.com/99555654/194669341-0ad33b18-8e33-44aa-b299-0eb50c0c13a1.png)

- Введите `/leave`, чтобы покинуть плинум. Плинум будет удалён, когда его покинет последний участник.

![Screenshot_20221007_235021](https://user-images.githubusercontent.com/99555654/194669348-418b2bb3-cb6c-4a82-b592-acec07fb7a9c.png)

## Касательно организации БД
- Структура БД:

![Screenshot_20221008_000327](https://user-images.githubusercontent.com/99555654/194669364-4b893ca3-e44b-4f4a-9902-4835531770d2.png)
- В целях оптимизации хранения, пользователи вносятся в базу данных при создании или вступлении в первый плинум и удаляются из неё при выходе или удалении последнего. Это важный нюанс, т.к. после реализации возможности изменения имён пользователей, новые имена будут сохранены только до тех пор, пока пользователь состоит или является создателем хотя бы одного плинума.
