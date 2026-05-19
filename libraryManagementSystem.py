from tkinter import *
from tkinter import ttk
import tkinter.messagebox as messagebox
import csv
import os
from datetime import datetime

BOOKS_FILE = "books.csv"
ISSUED_FILE = "issued_books.csv"

# ── Colour palette ──────────────────────────────────────────────────────────
BG         = "#1e2a3a"
SIDEBAR_BG = "#16202e"
CARD_BG    = "#243447"
ACCENT     = "#4a9eff"
SUCCESS    = "#2ecc71"
WARNING    = "#e67e22"
TEXT       = "#ecf0f1"
TEXT_DIM   = "#95a5a6"


class LibraryApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1200x700+50+50")
        self.root.configure(bg=BG)
        self._build_ui()
        self._show_frame("reports")

    # ── UI skeleton ─────────────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        bar = Frame(self.root, bg=SIDEBAR_BG, height=58)
        bar.pack(fill=X)
        bar.pack_propagate(False)
        Label(bar, text="  Library Management System",
              font=("Arial", 22, "bold"), bg=SIDEBAR_BG, fg=TEXT).pack(side=LEFT, padx=10, pady=8)
        Label(bar, text=datetime.now().strftime("%B %d, %Y"),
              font=("Arial", 11), bg=SIDEBAR_BG, fg=TEXT_DIM).pack(side=RIGHT, padx=20)

        # Body
        body = Frame(self.root, bg=BG)
        body.pack(fill=BOTH, expand=True)

        # Sidebar
        sidebar = Frame(body, bg=SIDEBAR_BG, width=195)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        Label(sidebar, text="NAVIGATION", font=("Arial", 8, "bold"),
              bg=SIDEBAR_BG, fg=TEXT_DIM).pack(pady=(18, 4), padx=14, anchor=W)

        self.nav_btns = {}
        for key, label in [
            ("reports", "   Reports"),
            ("add",     "   Add Book"),
            ("issue",   "   Issue Book"),
            ("return",  "   Return Book"),
            ("search",  "   Search Book"),
        ]:
            b = Button(sidebar, text=label, font=("Arial", 12),
                       bg=SIDEBAR_BG, fg=TEXT, bd=0, pady=11,
                       anchor=W, width=17, cursor="hand2",
                       activebackground=CARD_BG, activeforeground=ACCENT,
                       command=lambda k=key: self._show_frame(k))
            b.pack(fill=X, pady=1)
            self.nav_btns[key] = b

        # Content area
        self.content = Frame(body, bg=BG)
        self.content.pack(side=LEFT, fill=BOTH, expand=True)

        # Status bar
        self.status_var = StringVar(value="Ready")
        sb = Frame(self.root, bg=SIDEBAR_BG, height=28)
        sb.pack(fill=X, side=BOTTOM)
        sb.pack_propagate(False)
        Label(sb, textvariable=self.status_var, font=("Arial", 9),
              bg=SIDEBAR_BG, fg=TEXT_DIM).pack(side=LEFT, padx=14, pady=4)

        # Build every page
        self.frames = {}
        self._build_add_frame()
        self._build_issue_frame()
        self._build_return_frame()
        self._build_search_frame()
        self._build_reports_frame()

    def _show_frame(self, name):
        for f in self.frames.values():
            f.pack_forget()
        for k, b in self.nav_btns.items():
            b.configure(bg=CARD_BG if k == name else SIDEBAR_BG,
                        fg=ACCENT  if k == name else TEXT)
        self.frames[name].pack(fill=BOTH, expand=True)
        refresh = {"reports": self._refresh_reports,
                   "issue":   self._refresh_issue_table,
                   "return":  self._refresh_return_table,
                   "search":  self._refresh_search_results}
        if name in refresh:
            refresh[name]()

    # ── File helpers ─────────────────────────────────────────────────────────

    def _load_books(self):
        books = []
        if not os.path.exists(BOOKS_FILE):
            return books
        try:
            with open(BOOKS_FILE, 'r', newline='') as f:
                for row in csv.DictReader(f):
                    row['quantity']  = int(row['quantity'])
                    row['available'] = int(row['available'])
                    books.append(row)
        except Exception as e:
            messagebox.showerror("File Error", f"Cannot load books:\n{e}")
        return books

    def _save_books(self, books):
        try:
            with open(BOOKS_FILE, 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['book_id','name','author','quantity','available'])
                w.writeheader(); w.writerows(books)
        except Exception as e:
            messagebox.showerror("File Error", f"Cannot save books:\n{e}")

    def _load_issued(self):
        issued = []
        if not os.path.exists(ISSUED_FILE):
            return issued
        try:
            with open(ISSUED_FILE, 'r', newline='') as f:
                for row in csv.DictReader(f):
                    issued.append(row)
        except Exception as e:
            messagebox.showerror("File Error", f"Cannot load issued records:\n{e}")
        return issued

    def _save_issued(self, issued):
        try:
            with open(ISSUED_FILE, 'w', newline='') as f:
                w = csv.DictWriter(f, fieldnames=['issue_id','student_name','book_id',
                                                   'book_name','issue_date','return_date'])
                w.writeheader(); w.writerows(issued)
        except Exception as e:
            messagebox.showerror("File Error", f"Cannot save issued records:\n{e}")

    # ── Reusable widget helpers ───────────────────────────────────────────────

    def _section_label(self, parent, text):
        Label(parent, text=text, font=("Arial", 15, "bold"),
              bg=BG, fg=ACCENT).pack(anchor=W, pady=(0, 12))

    def _card(self, parent):
        return Frame(parent, bg=CARD_BG)

    def _field(self, card, label, row, var=None):
        var = var or StringVar()
        Label(card, text=label, font=("Arial", 11), bg=CARD_BG, fg=TEXT_DIM
              ).grid(row=row, column=0, sticky=W, padx=14, pady=8)
        Entry(card, textvariable=var, font=("Arial", 11),
              bg="#1a2736", fg=TEXT, insertbackground=TEXT,
              relief=FLAT, bd=5, width=32
              ).grid(row=row, column=1, sticky=W, padx=14, pady=8)
        return var

    def _btn(self, parent, text, cmd, color=None):
        return Button(parent, text=text, font=("Arial", 11, "bold"),
                      bg=color or ACCENT, fg="white", bd=0,
                      padx=18, pady=7, cursor="hand2",
                      activebackground=color or ACCENT,
                      command=cmd)

    def _tree(self, parent, columns, headings, widths):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("L.Treeview",
                        background=CARD_BG, foreground=TEXT,
                        fieldbackground=CARD_BG, rowheight=27,
                        font=("Arial", 10))
        style.configure("L.Treeview.Heading",
                        background=SIDEBAR_BG, foreground=ACCENT,
                        font=("Arial", 10, "bold"))
        style.map("L.Treeview", background=[("selected", "#2a4a7f")])

        wrap = Frame(parent, bg=CARD_BG)
        tv   = ttk.Treeview(wrap, columns=columns, show="headings", style="L.Treeview")
        vsb  = ttk.Scrollbar(wrap, orient=VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=vsb.set)
        for col, hd, w in zip(columns, headings, widths):
            tv.heading(col, text=hd)
            tv.column(col, width=w, anchor=W)
        tv.pack(side=LEFT, fill=BOTH, expand=True)
        vsb.pack(side=RIGHT, fill=Y)
        return wrap, tv

    # ── Add Book page ─────────────────────────────────────────────────────────

    def _build_add_frame(self):
        frame = Frame(self.content, bg=BG, padx=28, pady=22)
        self.frames["add"] = frame
        self._section_label(frame, "Add New Book")

        card = self._card(frame)
        card.pack(fill=X, pady=(0, 18))
        self.v_id     = self._field(card, "Book ID :",     0)
        self.v_name   = self._field(card, "Book Name :",   1)
        self.v_author = self._field(card, "Author Name :", 2)
        self.v_qty    = self._field(card, "Quantity :",    3)

        bf = Frame(card, bg=CARD_BG)
        bf.grid(row=4, column=0, columnspan=2, pady=14, padx=14, sticky=W)
        self._btn(bf, "  Add Book  ", self._add_book, SUCCESS).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "  Clear  ",    self._clear_add, TEXT_DIM).pack(side=LEFT)

        Label(frame, text="Current Books", font=("Arial", 12, "bold"),
              bg=BG, fg=TEXT).pack(anchor=W, pady=(8, 4))
        wrap, self.add_tv = self._tree(frame,
            ("id","name","author","qty","avail"),
            ("Book ID","Book Name","Author","Total","Available"),
            (80, 260, 210, 70, 85))
        wrap.pack(fill=BOTH, expand=True)
        self._refresh_add_table()

    def _refresh_add_table(self):
        self.add_tv.delete(*self.add_tv.get_children())
        for b in self._load_books():
            self.add_tv.insert("", END, values=(
                b['book_id'], b['name'], b['author'], b['quantity'], b['available']))

    def _add_book(self):
        bid    = self.v_id.get().strip().upper()
        name   = self.v_name.get().strip()
        author = self.v_author.get().strip()
        qty_s  = self.v_qty.get().strip()

        if not all([bid, name, author, qty_s]):
            messagebox.showwarning("Missing Fields", "Please fill in all fields.")
            return
        try:
            qty = int(qty_s)
            if qty < 1: raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Quantity", "Quantity must be a positive whole number.")
            return

        books = self._load_books()
        if any(b['book_id'] == bid for b in books):
            messagebox.showwarning("Duplicate ID", f"Book ID '{bid}' already exists.")
            return

        books.append({'book_id': bid, 'name': name, 'author': author,
                      'quantity': qty, 'available': qty})
        self._save_books(books)
        messagebox.showinfo("Success", f"Book '{name}' added successfully!")
        self._clear_add()
        self._refresh_add_table()
        self.status_var.set(f"Book '{name}' added.")

    def _clear_add(self):
        for v in (self.v_id, self.v_name, self.v_author, self.v_qty):
            v.set("")

    # ── Issue Book page ───────────────────────────────────────────────────────

    def _build_issue_frame(self):
        frame = Frame(self.content, bg=BG, padx=28, pady=22)
        self.frames["issue"] = frame
        self._section_label(frame, "Issue Book to Student")

        card = self._card(frame)
        card.pack(fill=X, pady=(0, 18))
        self.v_stu_name = self._field(card, "Student Name :", 0)
        self.v_iss_bid  = self._field(card, "Book ID :",      1)

        bf = Frame(card, bg=CARD_BG)
        bf.grid(row=2, column=0, columnspan=2, pady=14, padx=14, sticky=W)
        self._btn(bf, "  Issue Book  ", self._issue_book).pack(side=LEFT)

        Label(frame, text="Available Books", font=("Arial", 12, "bold"),
              bg=BG, fg=TEXT).pack(anchor=W, pady=(8, 4))
        wrap, self.issue_tv = self._tree(frame,
            ("id","name","author","avail"),
            ("Book ID","Book Name","Author","Available"),
            (80, 300, 230, 90))
        wrap.pack(fill=BOTH, expand=True)

    def _refresh_issue_table(self):
        self.issue_tv.delete(*self.issue_tv.get_children())
        for b in self._load_books():
            if b['available'] > 0:
                self.issue_tv.insert("", END, values=(
                    b['book_id'], b['name'], b['author'], b['available']))

    def _issue_book(self):
        student = self.v_stu_name.get().strip()
        bid     = self.v_iss_bid.get().strip().upper()
        if not student or not bid:
            messagebox.showwarning("Missing Fields", "Please enter student name and book ID.")
            return

        books  = self._load_books()
        issued = self._load_issued()

        for book in books:
            if book['book_id'] == bid:
                if book['available'] > 0:
                    book['available'] -= 1
                    iid = f"ISS{len(issued) + 1:04d}"
                    issued.append({'issue_id': iid, 'student_name': student,
                                   'book_id': bid, 'book_name': book['name'],
                                   'issue_date': datetime.now().strftime('%Y-%m-%d'),
                                   'return_date': ''})
                    self._save_books(books)
                    self._save_issued(issued)
                    messagebox.showinfo("Issued",
                        f"Book : {book['name']}\nTo   : {student}\nID   : {iid}")
                    self.v_stu_name.set("")
                    self.v_iss_bid.set("")
                    self._refresh_issue_table()
                    self.status_var.set(f"Issued '{book['name']}' to {student}.")
                else:
                    messagebox.showwarning("Not Available",
                        f"'{book['name']}' has no copies available right now.")
                return
        messagebox.showerror("Not Found", f"Book ID '{bid}' not found.")

    # ── Return Book page ──────────────────────────────────────────────────────

    def _build_return_frame(self):
        frame = Frame(self.content, bg=BG, padx=28, pady=22)
        self.frames["return"] = frame
        self._section_label(frame, "Return Book")

        card = self._card(frame)
        card.pack(fill=X, pady=(0, 18))
        self.v_ret_id = self._field(card, "Issue ID :", 0)

        bf = Frame(card, bg=CARD_BG)
        bf.grid(row=1, column=0, columnspan=2, pady=14, padx=14, sticky=W)
        self._btn(bf, "  Return Book  ", self._return_book, SUCCESS).pack(side=LEFT)

        Label(frame, text="Currently Issued Books", font=("Arial", 12, "bold"),
              bg=BG, fg=TEXT).pack(anchor=W, pady=(8, 4))
        wrap, self.ret_tv = self._tree(frame,
            ("iid","student","bid","bname","date"),
            ("Issue ID","Student Name","Book ID","Book Name","Issue Date"),
            (90, 190, 80, 270, 100))
        wrap.pack(fill=BOTH, expand=True)

    def _refresh_return_table(self):
        self.ret_tv.delete(*self.ret_tv.get_children())
        for r in self._load_issued():
            if not r['return_date']:
                self.ret_tv.insert("", END, values=(
                    r['issue_id'], r['student_name'], r['book_id'],
                    r['book_name'], r['issue_date']))

    def _return_book(self):
        iid = self.v_ret_id.get().strip().upper()
        if not iid:
            messagebox.showwarning("Missing Field", "Please enter the Issue ID.")
            return

        books  = self._load_books()
        issued = self._load_issued()

        for rec in issued:
            if rec['issue_id'] == iid:
                if rec['return_date']:
                    messagebox.showwarning("Already Returned",
                        f"This book was already returned on {rec['return_date']}.")
                    return
                rec['return_date'] = datetime.now().strftime('%Y-%m-%d')
                for b in books:
                    if b['book_id'] == rec['book_id']:
                        b['available'] += 1
                        break
                self._save_books(books)
                self._save_issued(issued)
                messagebox.showinfo("Returned",
                    f"Book    : {rec['book_name']}\n"
                    f"Student : {rec['student_name']}\n"
                    f"Date    : {rec['return_date']}")
                self.v_ret_id.set("")
                self._refresh_return_table()
                self.status_var.set(f"'{rec['book_name']}' returned.")
                return
        messagebox.showerror("Not Found", f"Issue ID '{iid}' not found.")

    # ── Search Book page ──────────────────────────────────────────────────────

    def _build_search_frame(self):
        frame = Frame(self.content, bg=BG, padx=28, pady=22)
        self.frames["search"] = frame
        self._section_label(frame, "Search Book")

        card = self._card(frame)
        card.pack(fill=X, pady=(0, 18))

        self.search_by  = StringVar(value="name")
        self.search_kw  = StringVar()

        Label(card, text="Search by :", font=("Arial", 11),
              bg=CARD_BG, fg=TEXT_DIM).grid(row=0, column=0, sticky=W, padx=14, pady=(12,4))

        rbf = Frame(card, bg=CARD_BG)
        rbf.grid(row=0, column=1, sticky=W, padx=14)
        for txt, val in [("Book Name", "name"), ("Author Name", "author")]:
            Radiobutton(rbf, text=txt, variable=self.search_by, value=val,
                        bg=CARD_BG, fg=TEXT, selectcolor=CARD_BG,
                        activebackground=CARD_BG,
                        font=("Arial", 11)).pack(side=LEFT, padx=(0, 16))

        Label(card, text="Keyword :", font=("Arial", 11),
              bg=CARD_BG, fg=TEXT_DIM).grid(row=1, column=0, sticky=W, padx=14, pady=8)
        kw_entry = Entry(card, textvariable=self.search_kw, font=("Arial", 11),
                         bg="#1a2736", fg=TEXT, insertbackground=TEXT,
                         relief=FLAT, bd=5, width=32)
        kw_entry.grid(row=1, column=1, sticky=W, padx=14, pady=8)
        kw_entry.bind("<Return>", lambda _: self._search_book())

        bf = Frame(card, bg=CARD_BG)
        bf.grid(row=2, column=0, columnspan=2, pady=14, padx=14, sticky=W)
        self._btn(bf, "  Search  ",   self._search_book).pack(side=LEFT, padx=(0, 8))
        self._btn(bf, "  Show All  ", self._refresh_search_results, TEXT_DIM).pack(side=LEFT)

        self.search_lbl = Label(frame, text="All Books", font=("Arial", 12, "bold"),
                                bg=BG, fg=TEXT)
        self.search_lbl.pack(anchor=W, pady=(8, 4))

        wrap, self.search_tv = self._tree(frame,
            ("id","name","author","qty","avail"),
            ("Book ID","Book Name","Author","Total","Available"),
            (80, 270, 210, 70, 90))
        wrap.pack(fill=BOTH, expand=True)

    def _refresh_search_results(self):
        self.search_tv.delete(*self.search_tv.get_children())
        for b in self._load_books():
            self.search_tv.insert("", END, values=(
                b['book_id'], b['name'], b['author'], b['quantity'], b['available']))
        self.search_lbl.config(text="All Books")

    def _search_book(self):
        kw = self.search_kw.get().strip().lower()
        if not kw:
            self._refresh_search_results(); return

        by      = self.search_by.get()
        results = [b for b in self._load_books()
                   if kw in b['name'].lower()   and by == "name"
                   or kw in b['author'].lower() and by == "author"]

        self.search_tv.delete(*self.search_tv.get_children())
        for b in results:
            self.search_tv.insert("", END, values=(
                b['book_id'], b['name'], b['author'], b['quantity'], b['available']))
        self.search_lbl.config(text=f"Results — {len(results)} found")
        self.status_var.set(f"{len(results)} result(s) for '{kw}'.")

    # ── Reports page ──────────────────────────────────────────────────────────

    def _build_reports_frame(self):
        frame = Frame(self.content, bg=BG, padx=28, pady=22)
        self.frames["reports"] = frame
        self._section_label(frame, "Library Reports")

        # Stat cards
        stats_row = Frame(frame, bg=BG)
        stats_row.pack(fill=X, pady=(0, 18))

        self.sv = {}
        for key, label, color in [
            ("titles",  "Book Titles",   ACCENT),
            ("copies",  "Total Copies",  ACCENT),
            ("avail",   "Available",     SUCCESS),
            ("issued",  "Issued",        WARNING),
        ]:
            c = Frame(stats_row, bg=CARD_BG, padx=18, pady=14)
            c.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
            v = StringVar(value="0")
            self.sv[key] = v
            Label(c, textvariable=v, font=("Arial", 30, "bold"),
                  bg=CARD_BG, fg=color).pack()
            Label(c, text=label, font=("Arial", 10),
                  bg=CARD_BG, fg=TEXT_DIM).pack()

        Label(frame, text="All Books", font=("Arial", 12, "bold"),
              bg=BG, fg=TEXT).pack(anchor=W, pady=(0, 4))
        w1, self.rep_books = self._tree(frame,
            ("id","name","author","qty","avail","status"),
            ("Book ID","Book Name","Author","Total","Avail","Status"),
            (72, 215, 180, 58, 58, 100))
        w1.pack(fill=BOTH, expand=True, pady=(0, 14))

        Label(frame, text="Currently Issued", font=("Arial", 12, "bold"),
              bg=BG, fg=TEXT).pack(anchor=W, pady=(0, 4))
        w2, self.rep_issued = self._tree(frame,
            ("iid","student","bid","bname","date"),
            ("Issue ID","Student","Book ID","Book Name","Issue Date"),
            (88, 165, 80, 240, 95))
        w2.pack(fill=BOTH, expand=True)

    def _refresh_reports(self):
        books  = self._load_books()
        issued = self._load_issued()
        active = [r for r in issued if not r['return_date']]

        self.sv['titles'].set(str(len(books)))
        self.sv['copies'].set(str(sum(b['quantity'] for b in books)))
        self.sv['avail'].set(str(sum(b['available'] for b in books)))
        self.sv['issued'].set(str(len(active)))

        self.rep_books.delete(*self.rep_books.get_children())
        for b in books:
            self.rep_books.insert("", END, values=(
                b['book_id'], b['name'], b['author'],
                b['quantity'], b['available'],
                "Available" if b['available'] > 0 else "Unavailable"))

        self.rep_issued.delete(*self.rep_issued.get_children())
        for r in active:
            self.rep_issued.insert("", END, values=(
                r['issue_id'], r['student_name'], r['book_id'],
                r['book_name'], r['issue_date']))


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == '__main__':
    root = Tk()
    LibraryApp(root)
    root.mainloop()
