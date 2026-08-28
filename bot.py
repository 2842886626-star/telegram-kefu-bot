import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ============================================================
# 基础设置
# ============================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
SERVICE_USERNAME = os.getenv("SERVICE_USERNAME", "").strip()
WELCOME_IMAGE_URL = os.getenv("WELCOME_IMAGE_URL", "").strip()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# 底部固定菜单
# ============================================================

def bottom_menu():
    keyboard = [
        ["📋 业务菜单", "💬 联系客服"],
        ["📖 新手必读", "🔎 自助验群"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


# ============================================================
# 业务菜单
# ============================================================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("拉专群", callback_data="special_group"),
            InlineKeyboardButton("开公群", callback_data="public_group"),
        ],
        [
            InlineKeyboardButton("咨询 / 解封", callback_data="consult"),
            InlineKeyboardButton("购买广告 / 会员", callback_data="ad_member"),
        ],
        [
            InlineKeyboardButton("纠纷 / 违规举报", callback_data="report"),
            InlineKeyboardButton("资源对接", callback_data="resource"),
        ],
        [
            InlineKeyboardButton("投诉建议", callback_data="suggestion"),
            InlineKeyboardButton("自助验群", callback_data="verify"),
        ],
        [
            InlineKeyboardButton("销群恢复", callback_data="restore"),
            InlineKeyboardButton("新手必读", callback_data="guide"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ============================================================
# /start
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    text = (
        "您好，这里是在线客服机器人。🤖\n\n"
        "请点击下方对应的业务板块，"
        "选择您需要办理的业务。\n\n"
        "如需人工帮助，请点击「💬 联系客服」。"
    )

    if WELCOME_IMAGE_URL:
        try:
            await update.message.reply_photo(
                photo=WELCOME_IMAGE_URL,
                caption=text,
                reply_markup=main_menu(),
            )

            await update.message.reply_text(
                "👇 常用功能",
                reply_markup=bottom_menu(),
            )

            return

        except Exception as e:
            logger.warning(
                "欢迎图片发送失败: %s",
                e
            )

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )

    await update.message.reply_text(
        "👇 常用功能",
        reply_markup=bottom_menu(),
    )


# ============================================================
# 显示业务菜单
# ============================================================

async def show_business_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📋 业务菜单\n\n"
        "请选择你需要办理的业务：",
        reply_markup=main_menu(),
    )


# ============================================================
# 联系客服
# ============================================================

async def contact_service(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if SERVICE_USERNAME:

        username = SERVICE_USERNAME.replace("@", "").strip()

        keyboard = [
            [
                InlineKeyboardButton(
                    "👨‍💻 联系人工客服",
                    url=f"https://t.me/{username}"
                )
            ]
        ]

        await update.message.reply_text(
            "💬 联系客服\n\n"
            "点击下面按钮联系人工客服。",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    else:

        await update.message.reply_text(
            "💬 联系客服\n\n"
            "目前还没有设置人工客服账号。\n"
            "请稍后再试。",
        )


# ============================================================
# 新手必读
# ============================================================

async def guide(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "📖 新手必读\n\n"
        "1. 请勿相信陌生人发送的可疑链接。\n"
        "2. 不要向任何人泄露账号密码或验证码。\n"
        "3. 办理业务时请提供真实、准确的信息。\n"
        "4. 遇到问题可以联系客服。\n\n"
        "如需办理业务，请点击「📋 业务菜单」。",
        reply_markup=bottom_menu(),
    )


# ============================================================
# 自助验群
# ============================================================

async def verify(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "🔎 自助验群\n\n"
        "请将需要查询的 Telegram 群组链接发送给我。\n\n"
        "例如：\n"
        "https://t.me/example",
        reply_markup=bottom_menu(),
    )


# ============================================================
# 业务内容
# ============================================================

BUSINESS_TEXT = {

    "special_group":
        "📌 拉专群\n\n"
        "如需创建或咨询专属群组，请联系客服。\n\n"
        "请提供：\n"
        "• 群组用途\n"
        "• 预计人数\n"
        "• 需要的服务",

    "public_group":
        "📢 开公群\n\n"
        "如需创建公开群组，请联系客服。\n\n"
        "请说明：\n"
        "• 群组名称\n"
        "• 群组类型\n"
        "• 群组用途",

    "consult":
        "💬 咨询 / 解封\n\n"
        "如果你的账号、群组或相关业务遇到问题，"
        "可以联系客服进行咨询。\n\n"
        "请尽量提供详细情况。",

    "ad_member":
        "💰 广告 / 会员\n\n"
        "如需咨询广告发布、会员服务等业务，"
        "请联系客服了解具体方案。",

    "report":
        "🚨 纠纷 / 违规举报\n\n"
        "如发现违规内容或存在纠纷，请提交相关信息。\n\n"
        "建议提供：\n"
        "• 群组 / 用户信息\n"
        "• 相关截图\n"
        "• 具体问题描述",

    "resource":
        "🤝 资源对接\n\n"
        "如有合作、资源交换或商务对接需求，"
        "请联系客服。",

    "suggestion":
        "📝 投诉建议\n\n"
        "如果你对服务有意见、建议或投诉，"
        "可以提交相关情况。",

    "verify":
        "🔎 自助验群\n\n"
        "请将需要查询的群组链接发送给机器人。\n\n"
        "例如：\n"
        "https://t.me/example",

    "restore":
        "♻️ 销群恢复\n\n"
        "如果群组出现异常、误操作或需要恢复相关服务，"
        "请联系客服咨询。",

    "guide":
        "📖 新手必读\n\n"
        "请注意账号安全，不要泄露密码、验证码等信息。"
}


# ============================================================
# Inline 按钮处理
# ============================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    action = query.data

    # 返回主菜单
    if action == "back_menu":

        await query.edit_message_text(
            text="📋 请选择你需要办理的业务：",
            reply_markup=main_menu(),
        )

        return

    text = BUSINESS_TEXT.get(
        action,
        "暂时没有找到对应业务，请返回主菜单。"
    )

    keyboard = []

    if SERVICE_USERNAME:

        username = SERVICE_USERNAME.replace("@", "").strip()

        keyboard.append([
            InlineKeyboardButton(
                "👨‍💻 联系人工客服",
                url=f"https://t.me/{username}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ 返回主菜单",
            callback_data="back_menu"
        )
    ])

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ============================================================
# 普通文字消息
# ============================================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text or ""

    # 底部菜单
    if text == "📋 业务菜单":
        await show_business_menu(update, context)
        return

    if text == "💬 联系客服":
        await contact_service(update, context)
        return

    if text == "📖 新手必读":
        await guide(update, context)
        return

    if text == "🔎 自助验群":
        await verify(update, context)
        return

    # 群链接
    if "t.me/" in text or "telegram.me/" in text:

        keyboard = []

        if SERVICE_USERNAME:

            username = SERVICE_USERNAME.replace("@", "").strip()

            keyboard.append([
                InlineKeyboardButton(
                    "👨‍💻 联系人工客服",
                    url=f"https://t.me/{username}"
                )
            ])

        await update.message.reply_text(
            "🔎 已收到你发送的链接。\n\n"
            "请根据需要联系人工客服。",
            reply_markup=(
                InlineKeyboardMarkup(keyboard)
                if keyboard
                else main_menu()
            ),
        )

        return

    await update.message.reply_text(
        "您好，请使用下面的菜单选择业务：",
        reply_markup=main_menu(),
    )


# ============================================================
# 错误处理
# ============================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "机器人发生错误:",
        exc_info=context.error
    )


# ============================================================
# 启动
# ============================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "没有找到 BOT_TOKEN，请在 Render 环境变量中设置 BOT_TOKEN。"
        )

    if not BASE_URL:
        raise RuntimeError(
            "没有找到 BASE_URL，请在 Render 环境变量中设置 BASE_URL。"
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    application.add_handler(
        CommandHandler("start", start)
    )

    # Inline 按钮
    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # 普通消息
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    application.add_error_handler(
        error_handler
    )

    port = int(
        os.getenv("PORT", "10000")
    )

    webhook_path = "telegram-webhook"

    webhook_url = (
        f"{BASE_URL}/{webhook_path}"
    )

    logger.info(
        "机器人启动"
    )

    logger.info(
        "Webhook: %s",
        webhook_url
    )

    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
