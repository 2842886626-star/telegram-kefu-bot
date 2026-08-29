import os
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# =========================================================
# 基础配置
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

BASE_URL = os.getenv(
    "BASE_URL",
    "https://telegram-kefu-bot.onrender.com"
).strip().rstrip("/")

PORT = int(os.getenv("PORT", "10000"))

# =========================================================
# 日志
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# 2列 × 5行菜单
# =========================================================

def main_menu():

    keyboard = [
        ["拉专群", "开公群"],
        ["咨询 / 解封", "广告 / 会员"],
        ["纠纷 / 举报", "资源对接"],
        ["投诉建议", "自助验群"],
        ["销群恢复", "新手必读"],
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="请选择业务",
    )


# =========================================================
# /start 欢迎语
# =========================================================

WELCOME_TEXT = (
    "您好，这里是新币担保在线人工客服。\n"
    "请点击下方对应的业务板块，选择您要办理的业务。\n"
    "验群请点击「自助验群」，输入您所在的群编号验证。"
)


# =========================================================
# 业务回复
# =========================================================

BUSINESS = {

    "拉专群": (
        "拉专群\n"
        "如需创建或咨询专属群组，请提供以下信息：\n"
        "群组用途\n"
        "预计人数\n"
        "需要的服务"
    ),

    "开公群": (
        "开公群\n"
        "如需开设公开群组，请提供：\n"
        "群组名称\n"
        "群组类型\n"
        "群组用途"
    ),

    "咨询 / 解封": (
        "咨询 / 解封\n"
        "如果您的账号、群组或相关业务遇到问题，"
        "可以在这里进行咨询。\n"
        "请尽量详细描述遇到的问题。"
    ),

    "广告 / 会员": (
        "广告 / 会员\n"
        "如需咨询广告发布或会员服务，"
        "请说明您的具体需求以及预计时间。"
    ),

    "纠纷 / 举报": (
        "纠纷 / 举报\n"
        "如发现违规内容或存在纠纷，"
        "请提供相关群组、用户信息以及具体情况。"
    ),

    "资源对接": (
        "资源对接\n"
        "如有合作、资源交换或商务对接需求，"
        "请简单介绍您的资源以及合作需求。"
    ),

    "投诉建议": (
        "投诉建议\n"
        "如果您对服务有意见、建议或投诉，"
        "请详细说明相关情况。"
    ),

    "自助验群": (
        "自助验群\n"
        "请输入您所在的群编号进行验证。\n"
        "例如：123456789\n"
        "请直接发送群编号。"
    ),

    "销群恢复": (
        "销群恢复\n"
        "如果群组出现异常、误操作或需要恢复相关服务，"
        "请提供群组编号或相关信息进行咨询。"
    ),

    "新手必读": (
        "新手必读\n"
        "1. 请勿相信陌生人发送的可疑链接。\n"
        "2. 不要向任何人泄露密码或验证码。\n"
        "3. 办理业务时请提供准确的信息。\n"
        "4. 遇到问题可以通过菜单选择对应业务。"
    ),
}


# =========================================================
# /start
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu()
    )


# =========================================================
# 菜单消息
# =========================================================

async def message_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = (update.message.text or "").strip()

    # 点击菜单
    if text in BUSINESS:

        await update.message.reply_text(
            BUSINESS[text],
            reply_markup=main_menu()
        )

        return

    # 用户发送其他文字
    await update.message.reply_text(
        "已收到您的消息。\n"
        "请点击下方菜单选择您需要办理的业务。",
        reply_markup=main_menu()
    )


# =========================================================
# 错误处理
# =========================================================

async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE
):

    logger.error(
        "机器人发生错误",
        exc_info=context.error
    )


# =========================================================
# 主程序
# =========================================================

def main():

    if not BOT_TOKEN:
        raise RuntimeError(
            "没有找到 BOT_TOKEN，请检查 Render 环境变量。"
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

    # 普通消息 + 菜单
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    # 错误处理
    application.add_error_handler(
        error_handler
    )

    # =====================================================
    # Render Webhook
    # =====================================================

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
        port=PORT,
        url_path=webhook_path,
        webhook_url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=Update.ALL_TYPES,
    )


# =========================================================
# 程序入口
# =========================================================

if __name__ == "__main__":
    main()
