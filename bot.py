import os
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
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

# 你的客服 Telegram 用户名，例如 @your_service
SERVICE_USERNAME = os.getenv("SERVICE_USERNAME", "")

# 欢迎图片，可留空
WELCOME_IMAGE_URL = os.getenv("WELCOME_IMAGE_URL", "")

# 日志
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# ============================================================
# 主菜单
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
    text = (
        "您好，这里是在线客服机器人。\n\n"
        "请点击下方对应的业务板块，选择您需要办理的业务。\n\n"
        "如需人工帮助，请选择「咨询 / 解封」。"
    )

    if WELCOME_IMAGE_URL:
        try:
            await update.message.reply_photo(
                photo=WELCOME_IMAGE_URL,
                caption=text,
                reply_markup=main_menu(),
            )
            return
        except Exception as e:
            logger.warning("欢迎图片发送失败: %s", e)

    await update.message.reply_text(
        text,
        reply_markup=main_menu(),
    )


# ============================================================
# 返回主菜单
# ============================================================

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "您好，请选择您需要办理的业务：\n\n"
        "👇 点击下方菜单即可"
    )

    await query.edit_message_text(
        text=text,
        reply_markup=main_menu(),
    )


# ============================================================
# 各业务内容
# ============================================================

BUSINESS_TEXT = {

    "special_group": (
        "📌 拉专群\n\n"
        "如需创建或咨询专属群组，请联系客服。\n\n"
        "请提供：\n"
        "• 群组用途\n"
        "• 预计人数\n"
        "• 需要的服务\n\n"
        "我们会根据你的需求进行处理。"
    ),

    "public_group": (
        "📢 开公群\n\n"
        "如需创建公开群组，请联系客服。\n\n"
        "请说明：\n"
        "• 群组名称\n"
        "• 群组类型\n"
        "• 群组用途\n\n"
        "审核通过后会进一步处理。"
    ),

    "consult": (
        "💬 咨询 / 解封\n\n"
        "如果你的账号、群组或相关业务遇到问题，"
        "可以联系客服进行咨询。\n\n"
        "请尽量提供详细情况，方便工作人员处理。"
    ),

    "ad_member": (
        "💰 广告 / 会员\n\n"
        "如需咨询广告发布、会员服务等业务，"
        "请联系客服了解具体方案。\n\n"
        "请说明你的需求以及预计时间。"
    ),

    "report": (
        "🚨 纠纷 / 违规举报\n\n"
        "如发现违规内容或存在纠纷，请提交相关信息。\n\n"
        "建议提供：\n"
        "• 群组 / 用户信息\n"
        "• 相关截图\n"
        "• 具体问题描述\n\n"
        "我们会根据情况进行处理。"
    ),

    "resource": (
        "🤝 资源对接\n\n"
        "如有合作、资源交换或商务对接需求，"
        "请联系客服。\n\n"
        "请简单介绍你的资源和合作需求。"
    ),

    "suggestion": (
        "📝 投诉建议\n\n"
        "如果你对服务有意见、建议或投诉，"
        "可以在这里提交。\n\n"
        "请尽量详细描述问题，我们会认真处理。"
    ),

    "verify": (
        "🔎 自助验群\n\n"
        "为了避免进入风险群组，请先确认群组信息。\n\n"
        "请将需要查询的群组链接发送给机器人。\n\n"
        "例如：\n"
        "https://t.me/example"
    ),

    "restore": (
        "♻️ 销群恢复\n\n"
        "如果群组出现异常、误操作或需要恢复相关服务，"
        "请联系客服咨询。\n\n"
        "请提供群组链接或群组 ID，以及具体情况。"
    ),

    "guide": (
        "📖 新手必读\n\n"
        "1. 请勿相信陌生人发送的可疑链接。\n"
        "2. 不要向任何人泄露账号密码或验证码。\n"
        "3. 处理业务时请提供真实、准确的信息。\n"
        "4. 遇到问题可以随时联系客服。\n\n"
        "如有其他问题，请返回主菜单选择对应业务。"
    ),
}


# ============================================================
# 按钮处理
# ============================================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action = query.data

    # 返回主菜单
    if action == "back_menu":
        await show_main_menu(update, context)
        return

    text = BUSINESS_TEXT.get(
        action,
        "暂时没有找到对应业务，请返回主菜单。"
    )

    keyboard = []

    # 客服按钮
    if SERVICE_USERNAME:
        username = SERVICE_USERNAME
        if not username.startswith("@"):
            username = "@" + username

        keyboard.append([
            InlineKeyboardButton(
                "👨‍💻 联系人工客服",
                url=f"https://t.me/{username.replace('@', '')}"
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
# 普通消息处理
# ============================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text or ""

    # 用户发送群链接
    if "t.me/" in text or "telegram.me/" in text:
        await update.message.reply_text(
            "🔎 已收到你发送的链接。\n\n"
            "如果你需要人工核验，请点击下面联系人工客服。",
            reply_markup=(
                InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "👨‍💻 联系人工客服",
                            url=f"https://t.me/{SERVICE_USERNAME.replace('@', '')}"
                        )
                    ]
                ])
                if SERVICE_USERNAME
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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(
        "机器人发生错误:",
        exc_info=context.error
    )


# ============================================================
# 启动机器人
# ============================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "没有找到 BOT_TOKEN，请在服务器环境变量中设置 BOT_TOKEN。"
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

    # 按钮
    application.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # 普通文字
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    # 错误
    application.add_error_handler(error_handler)

    # ========================================================
    # Webhook 模式
    # ========================================================

    if not BASE_URL:
        raise RuntimeError(
            "没有找到 BASE_URL，请设置服务器公网地址。"
        )

    port = int(os.getenv("PORT", "10000"))

    webhook_path = "telegram-webhook"

    webhook_url = (
        f"{BASE_URL}/{webhook_path}"
    )

    logger.info("机器人启动")
    logger.info("Webhook: %s", webhook_url)

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
