import logging
import argparse
from datetime import datetime, timedelta
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, filters,
    MessageHandler, TypeHandler , ApplicationHandlerStop,
    JobQueue)

from teleborsa import news,news_head
from telequota import prezzo,print_stock

import os


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id in ALLOWED_USERS:
        pass
    elif not ALLOWED_USERS:
        pass
    else:
        raise ApplicationHandlerStop

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    next_run = now.replace(second=0, microsecond=0)
    if now.minute < 30:
        next_run = next_run.replace(minute=30)
    else:
        next_run = (next_run + timedelta(hours=1)).replace(minute=0)

    jobs = context.job_queue.jobs()
    job_exists = any(job.name == "update_news_job" for job in jobs)

    if job_exists:
        await update.message.reply_text(
            f"Already scheduled!"
        )
        raise ApplicationHandlerStop

    context.job_queue.run_repeating(
        update_news_job,
        interval = 30*60,
        chat_id=group_id,
        first = (next_run - now).total_seconds())

    formatted_time = next_run.strftime("%H:%M:%S")

    await update.message.reply_text(
        f"Scheduling started. Next run at: {formatted_time}"
    )

async def start_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    next_run = now.replace(second=0, microsecond=0)
    if now.minute < 15:
        next_run = next_run.replace(minute=15)
    elif now.minute < 30:
        next_run = next_run.replace(minute=30)
    elif now.minute < 45:
        next_run = next_run.replace(minute=40)
    else:
        next_run = (next_run + timedelta(hours=1)).replace(minute=0)

    jobs = context.job_queue.jobs()

    job_exists = any(job.name == "stock_job" for job in jobs)

    if job_exists:
        await update.message.reply_text(
            f"Already scheduled!"
        )
        raise ApplicationHandlerStop

    context.job_queue.run_once(
        stock_job,
        when=(next_run - now).total_seconds(),
        chat_id=group_id)

    formatted_time = next_run.strftime("%H:%M:%S")

    await update.message.reply_text(
        f"Scheduling started. Next run at: {formatted_time}"
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.job_queue.stop()
    await update.message.reply_text("Recurring jobs have been stopped!")

async def get_last_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        df = print_stock()
        for row in df.iter_rows(named=True):
            messaggio = f"{row['price']} -- {row['timestamp']}"
            await context.bot.send_message(chat_id=group_id, text=messaggio)
    except Exception as e:
        await context.bot.send_message(chat_id=group_id, text= f"Error in un update news job: {e}")

async def update_news_job(context: ContextTypes.DEFAULT_TYPE):
       # print(f"update_news_job triggered with context: {context}")
        chat_id=group_id
        try:
            df = news()
            for row in df.iter_rows(named=True):
                messaggio = f"{row['date']} -- {row['news']} -- {row['link']}"
                await context.bot.send_message(chat_id=group_id, text=messaggio)
        except Exception as e:
            await context.bot.send_message(chat_id=group_id, text= f"Error in un update news job: {e}")

async def stock_job(context: ContextTypes.DEFAULT_TYPE):
       # print(f"update_news_job triggered with context: {context}")
        chat_id=group_id
#        try:
#           df = prezzo(driver_path = driver_path_input)
#           for row in df.iter_rows(named=True):
#                messaggio = (f"{row['price']}\u20ac  -- at {row['timestamp']}")
#                await context.bot.send_message(chat_id=group_id, text=messaggio)
#        except Exception as e:
#            await context.bot.send_message(chat_id=group_id, text= f"Error in stock job: {e}")

        now = datetime.now()

        next_run = now.replace(second=0, microsecond=0)

        if now.hour >= 18:  # After 18:00, schedule for 8:00 the next day
            next_run = (next_run + timedelta(days=1)).replace(hour=8, minute=0)
        elif now.minute < 15:
            next_run = next_run.replace(minute=15)
        elif now.minute < 30:
            next_run = next_run.replace(minute=30)
        elif now.minute < 45:
            next_run = next_run.replace(minute=45)
        else:
            next_run = (next_run + timedelta(hours=1)).replace(minute=0)

        context.job_queue.run_once(
            stock_job,
            when=(next_run - now).total_seconds(),
            chat_id=chat_id,
            name="stock_job"
        )

async def get_current_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = prezzo(driver_path = driver_path_input)
    #print(f"il prezzo df e; {price}")
    try:
        if not price.is_empty():
            for row in price.iter_rows(named=True):
                messaggio = (f"{row['price']}\u20ac  -- at {row['timestamp']}")
                await mex(update, context, messaggio)
    except:
        await mex(update, context, "Now updated news available!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text= update.message.text
    )

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=group_id,
        text='funziona'
    )

async def list_jobs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jobs = context.job_queue.jobs()
    if not jobs:
        await update.message.reply_text("No jobs are currently scheduled.")
    else:
        message = "Scheduled Jobs:\n"
        for job in jobs:
            next_run = job.next_t if job.next_t else "Unknown"
            message += f"- {job.name}: next run at {next_run}\n"
        await update.message.reply_text(message)

async def mex(update: Update, context: ContextTypes.DEFAULT_TYPE, testo: str):
    text_input = testo
    await context.bot.send_message(
        chat_id=group_id,
        text= text_input
    )

async def update_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mex(update, context, "in lavorazione")

    df = news()
    try:
        if not df.is_empty():
            for row in df.iter_rows(named=True):
                messaggio = (f"{row['date']} -- {row['news']} -- {row['link']}")
                await mex(update, context, messaggio)
        elif df.is_empty():
            await mex(update, context, "No updated news available!")
    except:
        await mex(update, context, "No updated news available!")

async def head_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
 
    df = news_head()
    try:
        if not df.is_empty():
            for row in df.iter_rows(named=True):
                messaggio = (f"{row['date']} -- {row['news']} -- {row['link']}")
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text= messaggio)
        elif df.is_empty():
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text= "No news available")
    except:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text= "No news available")

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--token', help = 'Bot Token', required = True)
    parser.add_argument('-a', '--allowed',type=int, nargs='+', help = 'Allowed users IDs')
    parser.add_argument('-g', '--group', help = 'ID of receiving group chat', required=True)
    parser.add_argument('-d', '--driver', help = 'Custom path for Geckodriver', required=False)

    args = parser.parse_args()

    global driver_path_input
    driver_path_input = args.driver if args.driver else None
    print(driver_path_input)

    api_token = args.token
    global ALLOWED_USERS

    if args.allowed:
        ALLOWED_USERS = args.allowed
    else:
        ALLOWED_USERS = []

    global group_id
    group_id = args.group

    application = ApplicationBuilder().token(api_token).build()
    handler = TypeHandler(Update, callback)
    application.add_handler(handler, -1)


    start_handler = CommandHandler('start', start)
    last_stock = CommandHandler('last_stock', get_last_stock)
    stock_handler = CommandHandler('start_stock', start_stock)
    invio_handler = CommandHandler('test', test)
    jobs_handler = CommandHandler('list_jobs', list_jobs)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    update_handler = CommandHandler('update_news', update_news)
    stop_handler = CommandHandler('stop', stop)
    current_price_handler = CommandHandler('get_price', get_current_price)
    head_news_handler = CommandHandler('head_news', head_news)

    application.add_handler(start_handler)
    application.add_handler(stock_handler)
    application.add_handler(last_stock)
    application.add_handler(stop_handler)
    application.add_handler(jobs_handler)
    application.add_handler(echo_handler)
    application.add_handler(invio_handler)
    application.add_handler(update_handler)
    application.add_handler(current_price_handler)
    application.add_handler(head_news_handler) 

    application.run_polling()

if __name__ == '__main__':
    main()
