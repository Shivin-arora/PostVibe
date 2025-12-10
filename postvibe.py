import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from datetime import datetime


db = mysql.connector.connect(
    host="localhost",
    user="root",       
    password="1234",       
    database="postvibe")

cursor = db.cursor()


current_user = None


window = tk.Tk()
window.title("PostVibe - Mini Social Media")
window.geometry("400x600")
window.resizable(False, False)
window.configure(bg='#2C2C2C')  

def clear_window():
    for widget in window.winfo_children():
        widget.destroy()



def home():
    clear_window()
    tk.Label(window, text="PostVibe", font=("Arial", 20, "bold italic"),
             fg='#F5F5F5', bg='#2C2C2C').pack(pady=10)
    tk.Button(window, text="Login", width=15, fg='#F5F5F5', bg='#D4AF37',
              command=login_page).pack(pady=10)
    tk.Button(window, text="Register", width=15, fg='#F5F5F5', bg='#D4AF37',
              command=register_page).pack(pady=5)

def login_page():
    clear_window()
    tk.Label(window, text="Login", font=("Arial", 16),
             fg='#F5F5F5', bg='#2C2C2C').pack(pady=10)

    tk.Label(window, text="Username", fg='#DCDCDC', bg='#2C2C2C').pack()
    username_entry = tk.Entry(window)
    username_entry.pack()

    tk.Label(window, text="Password", fg='#DCDCDC', bg='#2C2C2C').pack()
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    def login_user():
        global current_user
        username = username_entry.get()
        password = password_entry.get()
        cursor.execute("select * from users where username=%s and password=%s",(username, password))
        result = cursor.fetchone()
        if result:
            current_user = {'user_id': result[0], 'username': result[1]}
            feed_page()
        else:
            messagebox.showerror("Error", "Invalid Credentials")

    tk.Button(window, text="Login", width=15, fg='#F5F5F5', bg='#D4AF37',
              command=login_user).pack(pady=5)
    tk.Button(window, text="Back to Home", width=15, fg='#F5F5F5', bg='#D4AF37',
              command=home).pack(pady=5)

def register_page():
    clear_window()
    tk.Label(window, text="Register", font=("Arial", 16), fg='#F5F5F5', bg='#2C2C2C').pack(pady=10)

    tk.Label(window, text="Username", fg='#DCDCDC', bg='#2C2C2C').pack()
    username_entry = tk.Entry(window)
    username_entry.pack()

    tk.Label(window, text="Password", fg='#DCDCDC', bg='#2C2C2C').pack()
    password_entry = tk.Entry(window, show="*")
    password_entry.pack()

    def register_user():
        username = username_entry.get()
        password = password_entry.get()
        cursor.execute("select * from users where username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user is None:
            cursor.execute("insert into users (username, password) values (%s, %s)",
                           (username, password))
            db.commit()
            messagebox.showinfo("Success", "Registered! Please login.")
            login_page()
        else:
            messagebox.showinfo("Failed", "Username already exists")

    tk.Button(window, text="Register", width=15, fg='#F5F5F5', bg='#D4AF37',
              command=register_user).pack(pady=5)
    tk.Button(window, text="Back to Home", width=15, fg='#F5F5F5', bg='#D4AF37',
              command=home).pack(pady=5)

def feed_page():
    clear_window()
    tk.Label(window, text=f"Welcome, {current_user['username']}", font=("Arial", 14),
             fg='#F5F5F5', bg='#2C2C2C').pack(pady=10) 
    tk.Button(window, text="Create Post", fg='#F5F5F5', bg='#D4AF37',
              command=create_post).pack(pady=5)
    tk.Button(window, text="Logout", fg='#F5F5F5', bg='#D4AF37',
              command=logout).pack(pady=5)

    
    feed_frame = tk.Frame(window, bg='#DCDCDC', bd=2, relief="solid")  
    feed_frame.pack(pady=10, fill='both', expand=True)

    canvas = tk.Canvas(feed_frame, bg='#2C2C2C')
    scrollbar = tk.Scrollbar(feed_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='#2C2C2C')

    def update_scrollregion(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", update_scrollregion)

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")


    cursor.execute('''select posts.post_id, users.username, posts.content,posts.timestamp
    from posts,users where posts.user_id = users.user_id order by posts.timestamp DESC''')
    all_posts = cursor.fetchall()
    for post in all_posts:
        post_id, username, content, timestamp = post

     
        cursor.execute("select count(*) from likes where post_id=%s", (post_id,))
        like_count = cursor.fetchone()[0]

       
        cursor.execute("select count(*) from comments where post_id=%s", (post_id,))
        comment_count = cursor.fetchone()[0]

        post_frame = tk.Frame(scrollable_frame, bd=1, relief="solid", padx=5, pady=5, bg='#2C2C2C')
        tk.Label(post_frame, text=f"@{username} • {timestamp.strftime('%Y-%m-%d %H:%M')}",
                 fg='#DCDCDC', bg='#2C2C2C').pack(anchor='w')
        tk.Label(post_frame, text=content, wraplength=350, justify='left', fg='#DCDCDC',
                 bg='#2C2C2C').pack(anchor='w')

        info_frame = tk.Frame(post_frame, bg='#2C2C2C')
        tk.Label(info_frame, text=f"♥ {like_count} Likes", fg='#DCDCDC',
                 bg='#2C2C2C').pack(side='left', padx=5)
        tk.Label(info_frame, text=f"💬 {comment_count} Comments", fg='#DCDCDC',
                 bg='#2C2C2C').pack(side='left', padx=5)
        tk.Button(info_frame, text="Like", fg='#F5F5F5', bg='#D4AF37',
                  command=lambda pid=post_id: like_post(pid)).pack(side='left', padx=5)
        tk.Button(info_frame, text="Comment", fg='#F5F5F5', bg='#D4AF37',
                  command=lambda pid=post_id: comment_post(pid)).pack(side='left', padx=5)
        info_frame.pack(anchor='w', pady=5)

        post_frame.pack(pady=5, fill='x')

    tk.Button(window, text="Refresh Feed", fg='#F5F5F5', bg='#D4AF37', command=feed_page).pack(pady=5)



def create_post():
    content = simpledialog.askstring("New Post", "What's on your mind?")
    if content:
        cursor.execute("insert into posts (user_id, content) values (%s, %s)",
                       (current_user['user_id'], content))
        db.commit()
        messagebox.showinfo("Success", "Post Created!")
        feed_page()

def like_post(post_id):
    cursor.execute("select * from likes where user_id=%s and post_id=%s",
                   (current_user['user_id'], post_id))
    if cursor.fetchone():
        messagebox.showinfo("Info", "You already liked this post!")
    else:
        cursor.execute("insert into likes (user_id, post_id) values (%s, %s)",
                       (current_user['user_id'], post_id))
        db.commit()

        feed_page()

def comment_post(post_id):
    comment = simpledialog.askstring("Comment", "Enter your comment:")
    if comment is not None and comment.strip() != "":
        cursor.execute("insert into comments (post_id, user_id, comment_text) values (%s, %s, %s)",
                       (post_id, current_user['user_id'], comment))
        db.commit()
        feed_page()

def logout():
    global current_user
    current_user = None
    login_page()


home()
window.mainloop()
