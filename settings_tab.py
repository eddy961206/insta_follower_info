import os
import threading
from tkinter import messagebox, scrolledtext
import onetimepass as otp
import tkinter as tk
from tkinter import Frame, Canvas, Entry, Listbox, Scrollbar, Text, Button, PhotoImage, BooleanVar, Checkbutton, ttk
from pathlib import Path
from ConfigManager import ConfigManager
import service
import main

class SettingsTab(Frame):
    PLACEHOLDER_OTP = '6자리 숫자'
    PLACEHOLDER_LOGIN_ID = '인스타그램 로그인ID'
    PLACEHOLDER_PASSWORD = '비밀번호'
    PLACEHOLDER_ACCOUNT = '계정이름 입력'
    PLACEHOLDER_MAX_COUNT = '숫자 입력'

    def __init__(self, master=None, notebook=None, results_tab=None, **kwargs):
        super().__init__(master, **kwargs)
        self.notebook = notebook
        self.results_tab = results_tab
        self.is_running = False
        self.create_widgets()
        self.config_manager = ConfigManager("설정정보.ini")
        if os.path.exists("설정정보.ini"):
            self.load_settings()
        self.add_placeholders()
        self.update_scrollbars()  # 초기 스크롤바 상태 업데이트


    def create_widgets(self):
        # 경로 설정
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / Path("./build/assets/frame0")

        # 상대 경로 헬퍼 함수
        def relative_to_assets(path: str) -> Path:
            return ASSETS_PATH / Path(path)

        # 캔버스 설정
        self.canvas = Canvas(
            self,
            bg="#D1D1D1",
            height=644,
            width=495,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.pack(fill="both", expand=True)


        # 'OTP 인증키' 입력 필드와 라벨
        self.otp_key_entry_image = PhotoImage(file=relative_to_assets("entry_11.png"))
        self.otp_key_entry_bg = self.canvas.create_image(178.0, 35.5, image=self.otp_key_entry_image)
        self.otp_key_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.otp_key_entry.place(x=122.0, y=27.0, width=112.0, height=15.0)
        self.canvas.create_text(30.0, 29.0, anchor="nw", text="1. OTP 인증키", fill="#000000", font=("Inter Bold", 12 * -1))
        
        # '실행' 버튼
        self.execute_button_image = PhotoImage(file=relative_to_assets("button_5.png"))
        self.execute_button = Button(self.canvas, image=self.execute_button_image, borderwidth=0, highlightthickness=0, command=self.run_main, relief="flat")
        self.execute_button.place(x=248.0, y=24.0, width=37.0, height=22.0)


        # '로그인 ID' 입력 필드와 라벨
        self.login_id_entry_image = PhotoImage(file=relative_to_assets("entry_9.png"))
        self.login_id_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.login_id_entry.place(x=122.0, y=60.0, width=167.0, height=18.0)
        self.canvas.create_text(30.0, 60.0, anchor="nw", text="2. 로그인ID", fill="#000000", font=("Inter", 12 * -1))

        # '비밀번호' 입력 필드와 라벨
        self.password_entry_image = PhotoImage(file=relative_to_assets("entry_8.png"))
        self.password_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.password_entry.place(x=122.0, y=90.0, width=167.0, height=18.0)
        self.canvas.create_text(30.0, 93.0, anchor="nw", text="3. 비밀번호", fill="#000000", font=("Inter", 12 * -1))


        ###################################################################
        ######################### 추출할 계정 정보 #########################
         
        # 추출할 계정 정보 표시 영역 사각형 (탭 배경)
        self.canvas.create_rectangle(
            30.0,
            147.0,  
            467.0,
            290.0,
            fill="#D9D9D9",
            outline="#000000")
        
        # '추출할 계정정보' 라벨
        self.canvas.create_text(30.0, 125.0, anchor="nw", text="3. 추출할 인스타그램 계정 정보", fill="#000000", font=("Inter Bold", 12 * -1))

        # '추출할 계정 이름' 입력 필드와 라벨
        self.target_acc_entry_image = PhotoImage(file=relative_to_assets("entry_9.png"))
        self.target_acc_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.target_acc_entry.place(x=76.0, y=219.0, width=112.0, height=18.0)
        self.canvas.create_text(76.0, 199.0, anchor="nw", text="추출할 계정명", fill="#000000", font=("Inter", 12 * -1))
        

        # 계정 '추가' 버튼
        self.add_account_button_image = PhotoImage(file=relative_to_assets("button_4.png"))
        self.add_account_button = Button(
            self.canvas,
            image=self.add_account_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_4 clicked"),
            relief="flat"
        )
        self.add_account_button.place(x=228.0, y=192.0, width=37.0, height=22.0)

        # 계정 '삭제' 버튼
        self.delete_account_button_image = PhotoImage(file=relative_to_assets("button_3.png"))
        self.delete_account_button = Button(
            self.canvas,
            image=self.delete_account_button_image,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_3 clicked"),
            relief="flat"
        )
        self.delete_account_button.place(x=228.0, y=224.0, width=37.0, height=22.0)

        # '추가된 계정정보' Listbox 설정
        self.account_info_listbox = Listbox(self, bg="#AAA2A2", fg="#000716")
        self.account_info_listbox.place(x=281.0, y=168.0, width=178.0, height=112.0)
        self.canvas.create_text(281.0, 153.0, anchor="nw", text="추가된 계정정보", fill="#000000", font=("Inter", 12 * -1))

        # 계정 '위로' 버튼
        self.move_up_button = Button(self.canvas, text="▲", command=self.move_up)
        self.move_up_button.place(x=380.0, y=150.0, width=20, height=15)

        # 계정 '아래로' 버튼
        self.move_down_button = Button(self.canvas, text="▼", command=self.move_down)
        self.move_down_button.place(x=410.0, y=150.0, width=20, height=15)
        

        # '추가' 버튼 동작 설정
        self.add_account_button.config(command=self.add_account_to_listbox)

        # '삭제' 버튼 동작 설정
        self.delete_account_button.config(command=self.delete_account_from_listbox)
        
        # 스크롤바 생성 (처음에는 숨김)
        self.y_scrollbar = Scrollbar(self, command=self.account_info_listbox.yview)
        self.x_scrollbar = Scrollbar(self, orient="horizontal", command=self.account_info_listbox.xview)

        self.account_info_listbox.config(yscrollcommand=self.y_scrollbar.set, xscrollcommand=self.x_scrollbar.set)

        ######################### 추출할 계정 정보 #########################
        ###################################################################


         # '계정당 추출할 최대 팔로워 수' 입력 필드와 라벨
        self.max_follower_cnt_entry_image = PhotoImage(file=relative_to_assets("entry_11.png"))
        self.max_follower_cnt_entry = Entry(self, bd=0, bg="#AAA2A2", fg="#000716", highlightthickness=0)
        self.max_follower_cnt_entry.place(x=30.0, y=321.0, width=112.0, height=18.0)
        self.canvas.create_text(30.0, 303.0, anchor="nw", text="4. 계정당 추출할 최대 팔로워 수 (필수)", fill="#000000", font=("Inter Bold", 12 * -1))
        
    ########################################################################
    ###############################  함수  #################################
    ########################################################################
        
    def run_main(self):
        self.save_settings()

        # 유효성 검사
        if not self.validate_inputs():
            return
        
        otp_key = self.otp_key_entry.get()
        if not self.validate_otp(otp_key):
            return

        # '실행' 버튼 비활성화
        self.is_running = True
        self.execute_button.config(state="disabled")

        # 사용자 입력 데이터 수집
        user_input_data = self.get_user_input_datas()

        # main_logic 함수를 별도의 스레드에서 실행
        main_logic_thread = threading.Thread(
            target=self.execute_main_logic, 
            args=(user_input_data)
        )
        main_logic_thread.start()

    def validate_otp(self, user_code):
        secret_key = 'DIOFEPCKNMKOLEJFOSJOEHIUZHEBNKAL'
        # secret_key = 'FORIENBISNXGUEOEPDDOAHIRKWLFIDJG'

        user_code = user_code.replace(" ", "")  # 띄어쓰기 및 공백 제거
        if otp.valid_totp(token=user_code, secret=secret_key):
            print('------- 프로그램 인증에 성공하였습니다. -------')
            return True
        else:
            messagebox.showinfo("인증 실패", "OTP 인증키가 올바르지 않습니다. 다시 시도해주세요.")
            self.otp_key_entry.focus_set()
            return False
                
    def execute_main_logic(self, login_id, password, accounts, max_follower_cnt):
        # '실행 결과' 탭으로 전환
        if self.notebook and self.results_tab:
            results_tab_index = self.notebook.index(self.results_tab)
            self.notebook.select(results_tab_index)

        # main_logic 함수 호출
        main.main_logic(login_id, password, accounts, int(max_follower_cnt))
        
        # 다 끝나면 '실행' 버튼 활성화
        self.is_running = False
        self.execute_button.config(state="active")  
        

    def get_user_input_datas(self):
        login_id = self.login_id_entry.get()
        password = self.password_entry.get()
        accounts = [self.account_info_listbox.get(idx) for idx in range(self.account_info_listbox.size())]
        max_follower_cnt =self.max_follower_cnt_entry.get()
                
        return (login_id, password, accounts, max_follower_cnt)


    def validate_inputs(self):
         # 'OTP 인증키' 검사
        otp_key = self.otp_key_entry.get()
        if not otp_key or otp_key == self.PLACEHOLDER_OTP:
            messagebox.showwarning("안내", "OTP 인증키를 입력해주세요.")
            self.otp_key_entry.focus_set()
            return False

        if not otp_key.isdigit():
            messagebox.showwarning("안내", "OTP 인증키는 숫자로만 구성되어야 합니다.")
            self.otp_key_entry.focus_set()
            return False

        # '로그인ID' 검사
        login_id = self.login_id_entry.get()
        if not login_id or login_id == self.PLACEHOLDER_LOGIN_ID:
            messagebox.showwarning("안내", "'로그인ID'를 입력해주세요.")
            self.login_id_entry.focus_set()
            return False
        
        # '비밀번호' 검사
        password = self.password_entry.get()
        if not password or password == self.PLACEHOLDER_PASSWORD:
            messagebox.showwarning("안내", "'비밀번호'를 입력해주세요.")
            self.password_entry.focus_set()
            return False

        # '추가된 계정정보' Listbox 검사
        if self.account_info_listbox.size() == 0:
            messagebox.showwarning("안내", "최소 1개의 추출할 계정 정보가 필요합니다. '추가된 계정정보'란에 계정정보를 추가해주세요.")
            return False

        # '계정당 추출할 최대 팔로워 수' 검사
        max_follower_cnt = self.max_follower_cnt_entry.get()
        try:
            max_follower_cnt = int(max_follower_cnt)
        except ValueError:
            messagebox.showwarning("안내", "'계정당 추출할 최대 팔로워 수'는 숫자여야 합니다.")
            self.max_follower_cnt_entry.focus_set()
            return False

        if max_follower_cnt <= 0:
            messagebox.showwarning("안내", "'계정당 추출할 최대 팔로워 수'는 1 이상이어야 합니다.")
            self.max_follower_cnt_entry.focus_set()
            return False

        return True


    def update_scrollbars(self):
        item_count = self.account_info_listbox.size()
        max_item_width = max([self.account_info_listbox.cget('width'), *(len(self.account_info_listbox.get(idx)) for idx in range(item_count))])
        
        if item_count > 6:  # 세로 스크롤바 업데이트
            self.y_scrollbar.place(x=459.0, y=158.0, height=112.0)
        else:
            self.y_scrollbar.place_forget()
        
        if max_item_width > self.account_info_listbox.cget('width'):    # 가로 스크롤바 업데이트
            self.x_scrollbar.place(x=281.0, y=270.0, width=178.0)
        else:
            self.x_scrollbar.place_forget()


    def add_account_to_listbox(self):
        target_acc = self.target_acc_entry.get()
        if target_acc:
            self.account_info_listbox.insert(tk.END, target_acc)
            self.target_acc_entry.delete(0, 'end')
            self.update_scrollbars()

    def delete_account_from_listbox(self):
        selected_index = self.account_info_listbox.curselection()[0]
        self.account_info_listbox.delete(selected_index)
        self.update_scrollbars()


    def move_up(self):
        selected = self.account_info_listbox.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                item = self.account_info_listbox.get(index)
                self.account_info_listbox.delete(index)
                self.account_info_listbox.insert(index - 1, item)
                self.account_info_listbox.select_set(index - 1)

    def move_down(self):
        selected = self.account_info_listbox.curselection()
        if selected:
            index = selected[0]
            if index < self.account_info_listbox.size() - 1:
                item = self.account_info_listbox.get(index)
                self.account_info_listbox.delete(index)
                self.account_info_listbox.insert(index + 1, item)
                self.account_info_listbox.select_set(index + 1)


    def add_placeholder_to_entry(self, entry_widget, placeholder, placeholder_color="#454343"):  
        def on_focus_in(event, placeholder=placeholder):
            if entry_widget.get() == placeholder:
                entry_widget.delete(0, tk.END)
                entry_widget.config(fg='black')

        def on_focus_out(event, placeholder=placeholder):
            if entry_widget.get() == '':
                entry_widget.insert(0, placeholder)
                entry_widget.config(fg=placeholder_color)

        if entry_widget.get() == '':
            entry_widget.insert(0, placeholder)
            entry_widget.config(fg=placeholder_color)

        entry_widget.bind("<FocusIn>", on_focus_in)
        entry_widget.bind("<FocusOut>", on_focus_out)

    def add_placeholders(self):
        self.add_placeholder_to_entry(self.otp_key_entry, self.PLACEHOLDER_OTP)
        self.add_placeholder_to_entry(self.login_id_entry, self.PLACEHOLDER_LOGIN_ID)
        self.add_placeholder_to_entry(self.password_entry, self.PLACEHOLDER_PASSWORD)
        self.add_placeholder_to_entry(self.target_acc_entry, self.PLACEHOLDER_ACCOUNT)
        self.add_placeholder_to_entry(self.max_follower_cnt_entry, self.PLACEHOLDER_MAX_COUNT)


    def load_settings(self):
        login_id = self.config_manager.load_config('실행정보', '로그인 ID')
        self.login_id_entry.insert(0, login_id)

        password = self.config_manager.load_config('실행정보', '비밀번호')
        self.password_entry.insert(0, password)

        accounts_str = self.config_manager.load_config('실행정보', '추가된 계정정보')
        if accounts_str:
            accounts = accounts_str.split('\n')
            for account in accounts:
                self.account_info_listbox.insert(tk.END, account)

        max_follower_cnt = self.config_manager.load_config('실행정보', '계정당 추출할 최대 팔로워 수')
        self.max_follower_cnt_entry.insert(0, max_follower_cnt)

    def save_settings(self):
        login_id = self.login_id_entry.get()
        self.config_manager.save_config('실행정보', '로그인 ID', login_id)

        password = self.password_entry.get()
        self.config_manager.save_config('실행정보', '비밀번호', password)

        accounts = [self.account_info_listbox.get(idx) for idx in range(self.account_info_listbox.size())]
        accounts_str = '\n'.join(accounts)
        self.config_manager.save_config('실행정보', '추가된 계정정보', accounts_str)

        max_follower_cnt = self.max_follower_cnt_entry.get()
        self.config_manager.save_config('실행정보', '계정당 추출할 최대 팔로워 수', max_follower_cnt)

        



