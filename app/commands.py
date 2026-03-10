from dataclasses import dataclass
from typing import Awaitable, Callable

import telegram
from telegram import BotCommand

from app.bingo import get_bingo_item_count, get_random_bingo
from app.checkin import add_checkin, get_active_checkins
from app.forecast import (
    MOUNTAIN_ELEVATION,
    VILLAGE_ELEVATION,
    get_weather_data,
    send_daily_forecast,
)
from app.joke import get_joke
from app.layers import get_layers_advice
from app.mother_of_all_file import (
    get_address,
    get_addresshotel,
    get_back,
    get_flip,
    get_mansplain_image_url,
    get_name,
    get_rng,
)
from app.mountainview import get_saalbach_webcam_url
from app.restaurant import get_random_restaurant
from app.shotcaller import get_shotcaller_message

CommandHandler = Callable[[telegram.Bot, dict], Awaitable[None]]


@dataclass
class Command:
    name: str
    description: str
    handler: CommandHandler


COMMANDS: dict[str, Command] = {}


def command(name: str, description: str):
    def decorator(func: CommandHandler) -> CommandHandler:
        COMMANDS[name] = Command(name=name, description=description, handler=func)
        return func

    return decorator


async def send_message(bot: telegram.Bot, msg: str, chat_id: int) -> None:
    await bot.send_message(text=msg, chat_id=chat_id)


def get_bot_commands() -> list[BotCommand]:
    return [BotCommand(command=cmd.name, description=cmd.description) for cmd in COMMANDS.values()]


async def register_command_preview(bot: telegram.Bot) -> None:
    await bot.set_my_commands(get_bot_commands())


def generate_help_message() -> str:
    lines = ["🤖 *Available Commands*\n"]
    for cmd in COMMANDS.values():
        lines.append(f"/{cmd.name} - {cmd.description}")
    return "\n".join(lines)


@command("help", "Show all available commands")
async def handle_help(bot: telegram.Bot, message: dict) -> None:
    help_text = generate_help_message()
    await bot.send_message(
        text=help_text,
        chat_id=message["chat"]["id"],
        parse_mode="Markdown",
    )


@command("lol", "Get a lol response")
async def handle_lol(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, "lol to you, nerd!", message["chat"]["id"])


@command("businessidea", "Generate a business idea")
async def handle_businessidea(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, "AI brothel!", message["chat"]["id"])


@command("joke", "Get joke of the day")
async def handle_joke(bot: telegram.Bot, message: dict) -> None:
    joke = await get_joke()
    await send_message(bot, joke, message["chat"]["id"])


@command("rng", "Random number generator (usage: /rng{number})")
async def handle_rng(bot: telegram.Bot, message: dict) -> None:
    number = get_rng(message["text"])
    await send_message(bot, number, message["chat"]["id"])


@command("dishes", "Pick someone to do the dishes")
async def handle_dishes(bot: telegram.Bot, message: dict) -> None:
    name = get_name(message)
    text = f"Today, {name} will be doing the dishes!! LOL loser 😙"
    await send_message(bot, text, message["chat"]["id"])


@command("addresshotel", "Get the hotel address")
async def handle_addresshotel(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, get_addresshotel(), message["chat"]["id"])


@command("address", "Get the WISPO address")
async def handle_address(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, get_address(), message["chat"]["id"])


@command("flip", "Flip a table")
async def handle_flip(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, get_flip(), message["chat"]["id"])


@command("back", "Put the table back")
async def handle_back(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, get_back(), message["chat"]["id"])


@command("whoisbuyingthenextround", "Find out who's buying the next round")
async def handle_whoisbuyingthenextround(bot: telegram.Bot, message: dict) -> None:
    await send_message(bot, "Ties", message["chat"]["id"])


@command("mansplain", "Get a mansplain")
async def handle_mansplain(bot: telegram.Bot, message: dict) -> None:
    await bot.send_photo(
        chat_id=message["chat"]["id"],
        photo=get_mansplain_image_url(),
        caption="No more text needed",
    )


@command("mountainview", "Get a live webcam from Saalbach Hinterglemm")
async def handle_mountainview(bot: telegram.Bot, message: dict) -> None:
    webcam_url, cam_name = get_saalbach_webcam_url()
    caption = f"📸 {cam_name} – Saalbach Hinterglemm 🏔️⛷️"
    await bot.send_photo(
        chat_id=message["chat"]["id"],
        photo=webcam_url,
        caption=caption,
    )


@command("forecast", "Get today's weather forecast")
async def handle_forecast_command(bot: telegram.Bot, message: dict) -> None:
    await send_daily_forecast()


@command("layers", "What to wear today (weather-based)")
async def handle_layers(bot: telegram.Bot, message: dict) -> None:
    village_data = await get_weather_data(VILLAGE_ELEVATION, include_wind=True)
    mountain_data = await get_weather_data(MOUNTAIN_ELEVATION, include_wind=True)
    text = get_layers_advice(village_data, mountain_data)
    await bot.send_message(
        text=text,
        chat_id=message["chat"]["id"],
        parse_mode="Markdown",
    )


@command("shotcaller", "Pick someone to take a shot")
async def handle_shotcaller(bot: telegram.Bot, message: dict) -> None:
    text = get_shotcaller_message(message)
    await bot.send_message(
        chat_id=message["chat"]["id"],
        text=text,
        parse_mode="Markdown",
    )


@command("whichrestaurant", "Get a restaurant tip in Saalbach-Hinterglemm")
async def handle_whichrestaurant(bot: telegram.Bot, message: dict) -> None:
    text = get_random_restaurant()
    await bot.send_message(
        chat_id=message["chat"]["id"],
        text=text,
        parse_mode="Markdown",
    )


@command("checkin", "Check in at a location (usage: /checkin <location>, <group size>)")
async def handle_checkin(bot: telegram.Bot, message: dict) -> None:
    text = add_checkin(message)
    await bot.send_message(
        chat_id=message["chat"]["id"],
        text=text,
        parse_mode="Markdown",
    )


@command("whereiseveryone", "See where everyone is right now")
async def handle_whereiseveryone(bot: telegram.Bot, message: dict) -> None:
    text = get_active_checkins()
    await bot.send_message(
        chat_id=message["chat"]["id"],
        text=text,
        parse_mode="Markdown",
    )


@command("bingo", f"Random challenge - first to photo wins beer ({get_bingo_item_count()} options)")
async def handle_bingo(bot: telegram.Bot, message: dict) -> None:
    bingo = get_random_bingo()
    await bot.send_message(
        chat_id=message["chat"]["id"],
        text=bingo,
        parse_mode="Markdown",
    )


async def handle_command(bot: telegram.Bot, message: dict) -> bool:
    text = message.get("text", "")
    for cmd_name, cmd in COMMANDS.items():
        if cmd_name in text:
            await cmd.handler(bot, message)
            return True
    return False
