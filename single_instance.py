import ctypes

class SINGLE_INSTANCE_MUTEX:
    """Windows Mutex를 사용하여 단일 인스턴스 실행을 보장하는 클래스"""

    def __init__(self, mutex_name):
        self.mutex_name = mutex_name
        self.mutex = None

    def already_running(self):
        self.mutex = ctypes.windll.kernel32.CreateMutexA(None, False, self.mutex_name)
        last_error = ctypes.windll.kernel32.GetLastError()
        return last_error == 183  # ERROR_ALREADY_EXISTS
