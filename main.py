import telebot
from telebot import types
import sqlite3
from datetime import datetime


tname = None
ttext = None
status = 'NOT DONE'




token = ''
bot = telebot.TeleBot(token)

@bot.message_handler( commands = ['start'] )
def main(message):
    mark = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton("Добавить задач", callback_data = "add")
    button2 = types.InlineKeyboardButton("Посмотреть задач", callback_data = "view")
    button3 = types.InlineKeyboardButton("Удалить задач", callback_data = "delete")
    button4 = types.InlineKeyboardButton(" Отметка задач как выполненных.", callback_data = "done")
    mark.add(button1,button2)
    mark.add(button3,button4)
    bot.send_message(message.chat.id, "Привет!", reply_markup = mark)




@bot.callback_query_handler(func = lambda callback: True)
def tasks(callback):
    if callback.data == 'add':

        db = sqlite3.connect('task.db')
        c = db.cursor()
        c.execute(""" 
        CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name varchar(100) not null,
        task_text varchar(200) not null,
        creation_date  TEXT NOT NULL,
        status text NOT NULL)       
        """)
        db.commit()
        c.close()
        db.close()

        bot.send_message(callback.message.chat.id,"Имя вашего задач - ")
        bot.register_next_step_handler(callback.message,taskname)


    elif callback.data == 'view':

        #орындалмағандар


        db = sqlite3.connect('task.db')
        cur = db.cursor()
        cur.execute("""
            SELECT task_name
            FROM tasks
            WHERE status == "NOT DONE" 
            """)

        taskname_inbase = cur.fetchall()

        cur.execute("""
            SELECT task_text
            FROM tasks
            WHERE status == "NOT DONE" 
            """)
        tasktext_inbase = cur.fetchall()



        cur.execute("""
                    SELECT creation_date
                    FROM tasks
                    WHERE status == "NOT DONE" 
                    """)
        date_inbase = cur.fetchall()
        tasks_message = ""

        for name, text, date in zip (taskname_inbase,tasktext_inbase, date_inbase):
            task_name = name[0]
            task_name = task_name.strip("[]()\"'")
            task_text = text[0]
            task_text = task_text.strip("[]()\"'")

            tdate = date[0]
            tdate = tdate.strip("[]()\"'")

            tasks_message += f"Имя задачи: {task_name}\nОписание задачи: {task_text}\nДата написания задачи: {tdate}\n\n"

        bot.send_message(callback.message.chat.id, f"Не сделанные задачи:\n\n {tasks_message}")

        #Орындалмағандар

        cur.execute("""
                    SELECT task_name
                    FROM tasks
                    WHERE status == "DONE" 
                    """)

        donetaskname_inbase = cur.fetchall()

        cur.execute("""
                    SELECT task_text
                    FROM tasks
                    WHERE status == "DONE" 
                    """)
        donetasktext_inbase = cur.fetchall()

        cur.execute("""
                    SELECT creation_date
                    FROM tasks
                    WHERE status == "DONE" 
                    """)
        donedate_inbase = cur.fetchall()

        db.commit()
        cur.close()
        db.close()


        donetasks_message = ""

        for dname, dtext, ddate in zip(donetaskname_inbase, donetasktext_inbase, donedate_inbase):
            dtask_name = dname[0]
            dtask_name = dtask_name.strip("[]()\"'")
            dtask_text = dtext[0]
            dtask_text = dtask_text.strip("[]()\"'")
            ddate = ddate[0]
            ddate = ddate.strip("[]()\"'")

            donetasks_message += f"Имя задачи: {dtask_name}\nОписание задачи: {dtask_text}\nДата написания задачи: {ddate}\n\n"



        bot.send_message(callback.message.chat.id, f"Cделанные задачи:\n\n {donetasks_message}")

    elif callback.data == "done":
        db = sqlite3.connect('task.db')
        cur = db.cursor()
        cur.execute("""
        SELECT id
        from tasks
        WHERE status == "NOT DONE"
               """)

        notdoneid = cur.fetchall()
        cur.execute("""
                SELECT task_name
                from tasks
                WHERE status == "NOT DONE"
                       """)
        notdonename = cur.fetchall()

        notdonemessage = ""
        db.commit()
        cur.close()
        db.close()



        for id, name in zip(notdoneid,notdonename):
            nid = id[0]
            nname = name[0]
            nname = nname.strip("[]()\"'")
            notdonemessage += (f"ID задачи: {nid}\n Имя задачи: {nname} \n\n\n")

        bot.send_message(callback.message.chat.id, f"Выберите ID задач которого вы сделали:\n{notdonemessage}")
        bot.register_next_step_handler(callback.message,donemessage)


    elif callback.data == 'delete':
        db = sqlite3.connect('task.db')
        cur = db.cursor()
        cur.execute("""
                SELECT id
                from tasks
                       """)

        deleteid = cur.fetchall()
        cur.execute("""
                        SELECT task_name
                        from tasks
                               """)
        deletename = cur.fetchall()
        cur.execute("""
                                SELECT status
                                from tasks
                                       """)
        deletestatus = cur.fetchall()

        deletemessage = ""
        db.commit()
        cur.close()
        db.close()

        for id, name, status in zip(deleteid, deletename, deletestatus):
            nid = id[0]
            nname = name[0]
            nname = nname.strip("[]()\"'")
            deletestat = status[0]
            deletemessage += (f"ID задачи: {nid}\n Имя задачи: {nname}\n Статус задачи: {deletestat}  \n\n\n")


        bot.send_message(callback.message.chat.id, f"Выберите ID задач которого вы хотите удалить:\n{deletemessage}")
        bot.register_next_step_handler(callback.message, delmessage)







@bot.message_handler()

def delmessage(message):
    try:
        iddelete = int(message.text)
        db = sqlite3.connect('task.db')
        cur = db.cursor()
        cur.execute(f"""
                  SELECT task_name
                  from tasks
                  WHERE id == "{iddelete}"
                         """)

        namedone = cur.fetchall()
        cur.execute(f"""
                      DELETE from  tasks
                      WHERE id == "{iddelete}"
                             """)
        db.commit()
        cur.close()
        db.close()
        bot.send_message(message.chat.id,f"Вы удалили задачу {namedone}")
    except:
        bot.send_message(message.chat.id,"Исользуйте цифру и укажите правильную ID")





def donemessage(message):

    userid = int(message.text)
    db = sqlite3.connect('task.db')
    cur = db.cursor()
    cur.execute(f"""
           SELECT task_name
           from tasks
           WHERE id == "{userid}"
                  """)

    namedone = cur.fetchall()
    cur.execute(f"""
               UPDATE  tasks
               SET status = "DONE"
               WHERE id == "{userid}"
                      """)

    db.commit()
    cur.close()
    db.close()



    bot.send_message(message.chat.id,f"Вы выполнили задачу {namedone}")


def taskname(message):
    global tname
    tname = message.text
    bot.send_message(message.chat.id, "Опишите вашу задачу - ")
    bot.register_next_step_handler(message, tasktext)

def tasktext(message):
    ttext = message.text
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "NOT DONE"
    db = sqlite3.connect('task.db')
    c = db.cursor()
    c.execute(f""" INSERT INTO tasks(task_name, task_text, creation_date, status) VALUES
    ("{tname}","{ttext}","{current_time}","{status}")""")
    db.commit()
    c.close()
    db.close()

    bot.send_message(message.chat.id, "Done!")

bot.polling()





