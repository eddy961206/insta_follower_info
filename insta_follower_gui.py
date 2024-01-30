import tkinter as tk
from tkinter import ttk, messagebox
from settings_tab import SettingsTab
from results_tab import ResultsTab
import time
import ctypes
import sys
from TextRedirector import TextRedirector
from single_instance import SINGLE_INSTANCE_MUTEX

# 글로벌 변수
global results_tab

def main():

    mutex_name = "Global\\InstaFollowerFetchMutex"  # 고유한 이름 지정
    single_instance_mutex = SINGLE_INSTANCE_MUTEX(mutex_name)

    # 프로그램이 하나만 작동 되도록 확인
    if single_instance_mutex.already_running():
        messagebox.showinfo("경고", "프로그램이 이미 실행 중입니다. 프로그램을 종료합니다.")
        sys.exit()

    try:
        root = tk.Tk()
        root.title("린치핀 인스타 팔로워 추출 프로그램 v1.1")
        root.iconbitmap('./_internal/instagram.ico')    # EXE 묶을 때 용도!! 
        # root.iconbitmap('instagram.ico')  # 개발 용도

        root.geometry("495x400")

        tab_control = ttk.Notebook(root)

        # '기본 설정' 탭과 '실행 결과' 탭 생성 및 추가
        results_tab = ResultsTab(tab_control)
        settings_tab = SettingsTab(tab_control, notebook=tab_control, results_tab=results_tab)

        tab_control.add(settings_tab, text='기본 설정')
        tab_control.add(results_tab, text='실행 결과')

        tab_control.pack(expand=1, fill='both')

        # TextRedirector 설정
        sys.stdout = TextRedirector(results_tab.result_text)

        root.mainloop()
    except Exception as e:
        messagebox.showinfo("오류", f"프로그램 실행 오류: {e}\n프로그램이 예기치 못하게 중단 되었습니다.")
        
    finally:
        if single_instance_mutex.mutex:
            ctypes.windll.kernel32.CloseHandle(single_instance_mutex.mutex)

if __name__ == "__main__":
    main()