import os
import logging
import threading

from flask import Flask
from telegram import Update, BotCommand
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

if not BOT_TOKEN:
    raise RuntimeError("没有找到 BOT_TOKEN，请在 Render Environment Variables 中设置。")


# =========================================================
# 日志
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# =========================================================
# Render 健康检查网页
# =========================================================

app_web = Flask(__name__)


@app_web.route("/")
def index():
    return "Telegram Bot is running."


@app_web.route("/health")
def health():
    return "OK"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )


# =========================================================
# /start
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = (
        "新币客服\n"
        "机器人\n\n"
        "您好，欢迎使用客服机器人。\n"
        "请点击下方菜单选择您需要办理的业务。"
    )

    await update.message.reply_text(text)


# =========================================================
# 各业务命令
# =========================================================

async def laqun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "拉群服务\n\n"
        "如需创建或咨询专属群组，请联系客服。\n\n"
        "请提供：\n"
        "• 群组用途\n"
        "• 预计人数\n"
        "• 需要的服务"
    )


async def yanqun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "自助验群\n\n"
        "请发送您需要验证的群编号或相关信息。"
    )


async def xiaoshou(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "销群恢复\n\n"
        "如果群组出现异常、误操作或需要恢复相关服务，"
        "请提供群组编号或相关信息进行咨询。"
    )


async def zixun(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "咨询 / 解封\n\n"
        "如果您的账号、群组或相关业务遇到问题，"
        "可以在这里进行咨询。\n\n"
        "请尽量详细描述遇到的问题。"
    )


async def kefu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service_username = os.getenv("SERVICE_USERNAME", "").strip()

    if service_username:
        await update.message.reply_text(
            f"人工客服\n\n"
            f"如需人工协助，请联系：{service_username}"
        )
    else:
        await update.message.reply_text(
            "人工客服\n\n"
            "请发送您遇到的问题，我们会进一步处理。"
        )


# =========================================================
# 关键词自动回复
# =========================================================

async def keyword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # -----------------------------------------------------
    # 关键词
    # -----------------------------------------------------

    if "拉群" in text or "拉专群" in text:
        await laqun(update, context)
        return

    if "验群" in text or "自助验群" in text:
        await yanqun(update, context)
        return

    if "销群恢复" in text or "恢复" in text:
        await xiaoshou(update, context)
        return

    if "咨询" in text or "解封" in text:
        await zixun(update, context)
        return

    if "客服" in text or "人工" in text:
        await kefu(update, context)
        return

    # =====================================================
    # 第一次普通消息提示
    # =====================================================
    #
    # 关键部分：
    #
    # welcome_sent = False
    #
    # 第一次收到普通消息：
    #     回复一次
    #
    # 后面再发送：
    #     直接 return
    #
    # =====================================================

    if not context.user_data.get("welcome_sent", False):

        context.user_data["welcome_sent"] = True

        await update.message.reply_text(
            "已收到您的消息。\n"
            "请点击下方菜单选择您需要办理的业务。"
        )

        return

    # =====================================================
    # 已经发送过提示
    # 后面的普通消息不再自动回复
    # =====================================================

    return


# =========================================================
# 设置 Telegram 左下角菜单
# =========================================================

async def setup_commands(application: Application):

    commands = [
        BotCommand("start", "开始"),
        BotCommand("laqun", "拉专群"),
        BotCommand("yanqun", "自助验群"),
        BotCommand("xiaoshou", "销群恢复"),
        BotCommand("zixun", "咨询 / 解封"),
        BotCommand("kefu", "人工客服"),
    ]

    await application.bot.set_my_commands(commands)

    logger.info("Telegram 菜单命令设置完成")


# =========================================================
# 错误处理
# =========================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    logger.error(
        "机器人发生错误：",
        exc_info=context.error
    )


# =========================================================
# 主程序
# =========================================================

def main():

    logger.info("正在启动 Telegram Bot...")

    # Render 网页服务
    web_thread = threading.Thread(
        target=run_web,
        daemon=True
    )

    web_thread.start()

    # 创建机器人
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(setup_commands)
        .build()
    )

    # -----------------------------------------------------
    # 命令
    # -----------------------------------------------------

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("laqun", laqun)
    )

    application.add_handler(
        CommandHandler("yanqun", yanqun)
    )

    application.add_handler(
        CommandHandler("xiaoshou", xiaoshou)
    )

    application.add_handler(
        CommandHandler("zixun", zixun)
    )

    application.add_handler(
        CommandHandler("kefu", kefu)
    )

    # -----------------------------------------------------
    # 普通文字
    # -----------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            keyword_handler
        )
    )

    # -----------------------------------------------------
    # 错误处理
    # -----------------------------------------------------

    application.add_error_handler(error_handler)

    logger.info("Bot 已启动，开始接收消息...")

    # -----------------------------------------------------
    # Polling
    # -----------------------------------------------------

    application.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# =========================================================
# 启动
# =========================================================

if __name__ == "__main__":
    main()
