from aiogram import Bot
from aiogram import Dispatcher
from aiogram import executor
from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.types import CallbackQuery
from aiogram.types import Message
from json import dumps
from json import loads
from json import load
import db
import config

questions = load(open("questions.json", "r", encoding="utf-8"))

bot = Bot(token=config.TOKEN) #Ваш токен
dp = Dispatcher(bot=bot)


def compose_markup(question: int):
    km = InlineKeyboardMarkup(row_width=3)
    for i in range(len(questions[question]["variants"])):
        cd = {
            "question": question,
            "answer": i
        }
        km.insert(InlineKeyboardButton(questions[question]["variants"][i], callback_data=dumps(cd)))
    return km


def reset(uid: int):
    db.set_in_process(uid, False)
    db.change_questions_passed(uid, 0)
    db.change_questions_message(uid, 0)
    db.change_current_question(uid, 0)


@dp.callback_query_handler(lambda c: True)
async def answer_handler(callback: CallbackQuery):
    data = loads(callback.data)
    q = data["question"]
    is_correct = questions[q]["correct_answer"] - 1 == data["answer"]
    passed = db.get_questions_passed(callback.from_user.id)
    msg = db.get_questions_message(callback.from_user.id)
    if is_correct:
        passed += 1
        db.change_questions_passed(callback.from_user.id, passed)
    if q + 1 > len(questions) - 1:
        reset(callback.from_user.id)
        await bot.delete_message(callback.from_user.id, msg)
        await bot.send_message(
            callback.from_user.id,
            f"🎉 *Ура*, ви пройшли це випробування\\! Або вам було весело\\?\n\n🔒 У будь\\-якому випадку, тест завершено\\.\n✅ Правильних відповідей\\: *{passed} з {len(questions)}*\\.\n\n🔄 *Пройти тест знову* \\- /play", parse_mode="MarkdownV2"
        )
        return
    await bot.edit_message_text(
        questions[q + 1]["text"],
        callback.from_user.id,
        msg,
        reply_markup=compose_markup(q + 1),
        parse_mode="MarkdownV2"
    )


@dp.message_handler(commands=["play"])
async def go_handler(message: Message):
    if not db.is_exists(message.from_user.id):
        db.add(message.from_user.id)
    if db.is_in_process(message.from_user.id):
        await bot.send_message(message.from_user.id, "🚫 Ви не можете почати тест, тому що *ви вже його проходите*\\.", parse_mode="MarkdownV2")
        return
    db.set_in_process(message.from_user.id, True)
    msg = await bot.send_message(
        message.from_user.id,
        questions[0]["text"],
        reply_markup=compose_markup(0),
        parse_mode="MarkdownV2"
    )
    db.change_questions_message(message.from_user.id, msg.message_id)
    db.change_current_question(message.from_user.id, 0)
    db.change_questions_passed(message.from_user.id, 0)


@dp.message_handler(commands=["finish"])
async def quit_handler(message: Message):
    if not db.is_in_process(message.from_user.id):
        await bot.send_message(message.from_user.id, "❗️Ви ще *не почали тест*\\.", parse_mode="MarkdownV2")
        return
    reset(message.from_user.id)
    await bot.send_message(message.from_user.id, "✅ Ви успішно *закінчили тест*\\.", parse_mode="MarkdownV2")


@dp.message_handler(commands=["start"])
async def start(message: Message):
    await message.answer("👋 *Привіт\\!* \n🧠 *Пропоную перевірити ваше логічне мислення\\.*\n\n📝 Потрібно буде відповісти на *15 запитань*\\. \n⏱ Якщо думатимете як слід, що я рекомендую, тест займе *близько 10 хвилин*\\. \n\n⁉️ *Кожне питання* — логічна умова, обставини ситуації\\. \n📄 До кожної умови я пропоную *кілька варіантів відповідей*, логічних наслідків\\. \n\n⁉️ Вірним є *тільки одне* слідство, його вам і треба вибрати\\. \n🔍 Постарайтеся *абстрагуватися від реального світу* і приймати рішення, грунтуючись тільки на цих умовах\\.\n\n*Почати тест* \\- /play\n*Закінчити тест* \\- /finish\n*Технічна підтримка* \\- /help", parse_mode="MarkdownV2")


@dp.message_handler(commands=['help'])
async def cmd_answer(message: Message):
    await message.answer("⁉️<b> Якщо у вас є проблеми.</b> \n✉️ <b>Напишіть мені</b> <a href='https://t.me/nikit0ns'>@nikitons</a><b>.</b>", disable_web_page_preview=True, parse_mode="HTML")
    

def main() -> None:
    executor.start_polling(dp, skip_updates=True)


if __name__ == "__main__":
    main()
