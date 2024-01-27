import onetimepass as otp
import time

def get_code(secret_key):
    return otp.get_totp(secret_key)

def validate_otp(secret_key, user_code, attempts=5):
    failed_attempts = 0
    for _ in range(attempts):
        user_code = user_code.replace(" ", "")  # 띄어쓰기 및 공백 제거
        if otp.valid_totp(token=user_code, secret=secret_key):
            print('------- 프로그램 인증에 성공하였습니다. -------')
            return True
        else:
            failed_attempts += 1
            print('인증 실패. 다시 시도해주세요.')
    if failed_attempts >= 5:
        print("5회 이상 인증을 실패하여 프로그램을 종료합니다..")
        time.sleep(2)
    return False
