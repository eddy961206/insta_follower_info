from datetime import datetime
import os
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox

class ResultsTab(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        # 실행 결과 레이블
        self.result_label = tk.Label(self, text="실행 결과")
        self.result_label.pack(side=tk.TOP, pady=(5, 0))

        # 실행 결과 저장 버튼
        self.save_button = tk.Button(self, text="결과 txt파일로 저장하기", command=self.save_results)
        self.save_button.place(relx=1.0, y=0, x=-20, anchor="ne")
        
        # 실행 결과 표시 영역
        self.result_text = scrolledtext.ScrolledText(self, height=50)
        self.result_text.pack(padx=5, pady=(0, 5), fill=tk.BOTH, expand=True)

        # 사용자의 입력을 무시하되, 복사는 허용
        self.result_text.bind("<Key>", lambda e: "break")
        self.result_text.bind("<Control-c>", self.copy_text)
        self.result_text.bind("<Command-c>", self.copy_text)  # 맥 사용자의 경우

    def copy_text(self, event):
        # 선택된 텍스트를 복사하는 함수
        try:
            self.result_text.clipboard_clear()
            text = self.result_text.get("sel.first", "sel.last")
            self.result_text.clipboard_append(text)
        except tk.TclError:
            pass  # 선택된 텍스트가 없으면 아무것도 하지 않음
        return "break"  # 기본 이벤트 처리 중단
    
    
    def save_results(self):
        results_folder = "실행결과"
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)

        current_time = datetime.now().strftime("%y%m%d_%H%M")
        file_name = f"{current_time}_실행결과.txt"
        file_path = os.path.join(results_folder, file_name)

        # 텍스트 없으면 무반응
        if not self.result_text.get("1.0", tk.END).strip():
            return

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.result_text.get("1.0", tk.END))

        messagebox.showwarning("안내", f"'{results_folder}' 폴더에 결과가 저장되었습니다.")
