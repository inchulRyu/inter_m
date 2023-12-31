from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
import random

import time
import re

from datetime import datetime

wait_sec = 60

# 예매할 자리 수 (최대 2매)
wanted_seats_count = 1

# 인터파크 아이디 생년월일
birth_date = ""

# 결제할 카카오톡 정보
# 핸드폰 번호
kakao_phone_number = ""
# 생년월일
kakao_birth_date = ""

driver = webdriver.Chrome()

def alert_check():
    global driver
    # 경고창이 있는지 확인
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text  # 경고창의 내용을 가져옴
        print("경고창 내용:", alert_text)
        alert.accept()  # "확인" 버튼 클릭        
        # 경고창이 존재하면 True 반환
        is_alert_present = True
    except NoAlertPresentException:
        # 경고창이 존재하지 않으면 False 반환
        is_alert_present = False
    
    return is_alert_present  

def book_Delivery_check():
    global driver
    formBook = driver.find_elements(By.XPATH, "//form[@name='formBook']")
    if formBook:
        formBook[0].get_attribute("action")
        action_value = formBook[0].get_attribute("action")

        if action_value:
            # action 값에 따라 다른 조치를 취할 수 있습니다.
            if "/Book/BookPrice.asp" in action_value:
                # /Book/BookPrice.asp에 대한 처리
                return False
            elif "/Book/BookDelivery.asp" in action_value:
                # BookDelivery.asp에 대한 처리   
                return True 
            else:
                return False
        else:
            return False
    else:
        return False


# 로그인 페이지 열기
driver.get('https://ticket.interpark.com/Gate/TPLogin.asp?CPage=B&MN=Y&tid1=main_gnb&tid2=right_top&tid3=login&tid4=login')

# 사용자가 직접 로그인
input("로그인 한 후에는 'y'를 입력하고 Enter 누르세요.")

driver.get('https://tickets.interpark.com/special/sports/promotion?seq=22')

try:
    # 'layer-popup_pc__dlt6l' 클래스가 있는지 확인
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "layer-popup_pc__dlt6l")))

    # 'layer-popup_close__hGFj5 layer-popup_close_pc__0eVp3' 클래스를 가진 버튼 찾기
    close_button = driver.find_element(By.CLASS_NAME, "layer-popup_close__hGFj5.layer-popup_close_pc__0eVp3")

    # 버튼 클릭
    close_button.click()
except:
    # 'layer-popup_pc__dlt6l' 클래스가 없으면 아무것도 하지 않음
    pass

reservation_btn = driver.find_element(By.XPATH, '//*[@id="__next"]/div/div/div/div[2]/div[2]/ul/li[7]/div/div[3]/button')
reservation_btn.click()


## 좌석 선택 창
# 새 창 전환하기
# 새 창이나 탭이 열릴 때까지 기다림
WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 1)
window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])

find_seat = False

while True:
    # iframe으로 전환
    # 나올 때까지 기다리기
    # # 새 창이나 탭의 로딩을 기다림
    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmSeat")))
    iframe_seat = driver.find_element(By.ID, "ifrmSeat")
    driver.switch_to.frame(iframe_seat)

    # 보안문자 넘어가기
    # display: none; 검사
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "capchaLayer")))
    capcha_layer = driver.find_element(By.CLASS_NAME, 'capchaLayer')
    style_attribute = capcha_layer.get_attribute("style")

    # 'display: none;'이 포함되어 있는지 확인
    if "display: none;" not in style_attribute:
        # print("capcha_layer는 표시되어 있습니다.")    
        WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CLASS_NAME, "capchaBtns")))
        fncheckbtn = driver.find_element(By.CLASS_NAME, 'capchaBtns')

        # JavaScript를 사용하여 onclick 이벤트 변경
        script = """
        var element = document.querySelector('.capchaBtns a');
        if (element) {
            element.setAttribute('onclick', 'fnCheckOK()');
        }
        """
        driver.execute_script(script)

        fncheckbtn.click()

    # 남은 자리 확인.
    # .groundList 클래스 아래의 .list 클래스를 가진 요소 찾기
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".groundList .list")))
    # WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    # seat_list_element = driver.find_element(By.CSS_SELECTOR, ".groundList .list")

    # 0이 아닌 곳이 있나 확인.
    # JavaScript를 사용하여 rc 속성이 0이 아닌 <a> 요소 찾기
    available_seats_script = """
    var links = document.querySelectorAll('.groundList .list a');
    var availableSeats = [];
    for (var i = 0; i < links.length; i++) {
        if (links[i].getAttribute('rc') != '0') {
            availableSeats.push(links[i]);
        }
    }
    return availableSeats;
    """
    available_seats = driver.execute_script(available_seats_script)

    # available_seats 배열에는 rc 속성이 0이 아닌 <a> 요소들이 포함되어 있음
    # 예를 들어, 첫 번째 요소에 대한 정보를 출력
    if len(available_seats) > 0:
        # 현재 날짜와 시간을 가져오기
        current_datetime = datetime.now()
        # 문자열 형식으로 출력하기
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")        
        print(f"좌석 발견!! {formatted_datetime}")
        for available_seat in available_seats:
            rc = available_seats[0].get_attribute('rc')
            seat_text = available_seats[0].find_element(By.CSS_SELECTOR, 'span.red').text
            print(f"  rc={rc}, {seat_text}")

            # 숫자만 추출하는 정규 표현식 패턴
            pattern = r'\d+'
            if re.search(pattern, seat_text):
                num_seats = int(re.search(pattern, seat_text).group())
            else:
                num_seats = 0

            # '2'를 포함하는 텍스트를 발견한 경우 해당 좌석 클릭
            if num_seats >= wanted_seats_count:
                print("\n자동 배정 진행!")
                available_seat.click()
                find_seat = True
                break
    # else:
    #     print("좌석 없음. 새로고침.")
    
    if not find_seat:
        # driver.switch_to.default_content()
        driver.refresh()
        # time.sleep(1)
        random_sleep_time = random.uniform(0.111, 0.222)
        time.sleep(random_sleep_time)        
        continue
    
    # 자리 찾음.
    # 자동 배정 버튼 클릭
    auto_assign_button = driver.find_element(By.XPATH, "//a[img[@src='//ticketimage.interpark.com/TicketImage/onestop/kbo_twoBtn_1.gif']]")
    auto_assign_button.click()    


    ## 좌석 수 고르는 창

    # 먼저 메인 컨텐츠로 전환
    driver.switch_to.default_content()
    # iframe으로 전환
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
    iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
    driver.switch_to.frame(iframe_bookstep)

    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # <select> 요소 찾기
    select_element = driver.find_element(By.NAME, "SeatCount")

    # Select 객체 생성
    select_object = Select(select_element)

    # "2매" 선택 (옵션 값 "2" 사용)
    select_object.select_by_value(f"{wanted_seats_count}")

    # iframe_bookstep 작업 완료 후, 메인 페이지로 다시 전환
    driver.switch_to.default_content()

    # 다음 버튼 클릭
    # 'SmallNextBtnLink' ID를 가진 <a> 요소 찾기 (다음 버튼)
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
    # next_button = driver.find_element(By.XPATH, "//img[@src='//ticketimage.interpark.com/TicketImage/onestop/btn_next_02_on.gif']")
    next_button = driver.find_element(By.ID, "SmallNextBtnImage")
    next_button.click()

    # 약관 동의
    # iframe으로 전환
    iframe_cert = driver.find_element(By.ID, "ifrmBookCertify")
    driver.switch_to.frame(iframe_cert)

    # 체크박스 요소 찾기
    checkbox = driver.find_element(By.ID, "Agree")

    # 체크박스가 체크되어 있지 않다면 클릭
    if not checkbox.is_selected():
        checkbox.click()

    # 저장 버튼 찾기 (src 속성을 기반으로)
    save_button = driver.find_element(By.XPATH, "//img[@src='http://ticketimage.interpark.com/TicketImage/event/110321/btn_pop_01.gif']")

    # 저장 버튼 클릭
    save_button.click()

    # iframe 나오기.
    driver.switch_to.default_content()

    # 다음 버튼 클릭 (src 속성을 기반으로)
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
    # next_button = driver.find_element(By.XPATH, "//img[@src='//ticketimage.interpark.com/TicketImage/onestop/btn_next_02_on.gif']")
    next_button = driver.find_element(By.ID, "SmallNextBtnImage")    
    next_button.click()

    # 경고창 처리
    while True:
        # 경고창 없으면 반복
        if alert_check():
            find_seat = False
            break
        if book_Delivery_check():
            find_seat = True
            break
        print('로딩 중...')
        time.sleep(0.2)
    
    if not find_seat:
        continue
    else:
        print("자리 차지 완료!")

    # try:
    #     WebDriverWait(driver, wait_sec).until(EC.alert_is_present())
    #     alert = driver.switch_to.alert
    #     alert_text = alert.text  # 경고창의 내용을 가져옴
    #     print("경고창 내용:", alert_text)
    #     alert.accept()  # "확인" 버튼 클릭
    #     find_seat = False
    #     continue
    # except TimeoutException:
    #     print("경고창이 없습니다.")

    ## 생년월일 입력.
    print("생년월일 입력")
    # iframe으로 전환
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
    iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
    driver.switch_to.frame(iframe_bookstep)

    # 'YYMMDD' ID를 가진 <input> 요소 찾기
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "YYMMDD")))
    input_element = driver.find_element(By.ID, "YYMMDD")

    # 숫자 입력
    input_element.send_keys(birth_date)    

    # iframe 나오기
    driver.switch_to.default_content()

    # 다음 버튼 누르기
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
    next_button = driver.find_element(By.ID, "SmallNextBtnImage")
    next_button.click()


    ## 결제 선택
    print("카카오페이 선택")
    # iframe으로 전환
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
    iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
    driver.switch_to.frame(iframe_bookstep)

    # "카카오" 라벨을 가진 라디오 버튼 찾기
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(), '카카오')]/preceding-sibling::input[@type='radio']")))
    bank_transfer_radio = driver.find_element(By.XPATH, "//label[contains(text(), '카카오')]/preceding-sibling::input[@type='radio']")

    # 라디오 버튼 클릭
    bank_transfer_radio.click()  

    # # 은행 선택
    # print("은행 선택")
    # # 'BankCode' ID를 가진 <select> 요소 찾기
    # select_element = driver.find_element(By.ID, "BankCode")

    # # Select 객체 생성
    # select_object = Select(select_element)

    # # "국민은행" 선택 (옵션 값 "38051" 사용)
    # select_object.select_by_value("38051")

    # iframe 나오기
    driver.switch_to.default_content()
    
    # 다음 버튼 누르기
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "SmallNextBtnImage")))
    next_button = driver.find_element(By.ID, "SmallNextBtnImage")
    next_button.click()    


    ## 결제하기
    print("결제하기")
    # iframe으로 전환
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "ifrmBookStep")))
    iframe_bookstep = driver.find_element(By.ID, "ifrmBookStep")
    driver.switch_to.frame(iframe_bookstep)    

    # 동의 체크
    print("동의 체크")
    # checkbox = driver.find_element(By.CSS_SELECTOR, "#checkAll input[type='checkbox']")
    checkbox = driver.find_element(By.CSS_SELECTOR, "#checkAll[type='checkbox']")
    checkbox.click()

    # iframe 나오기
    driver.switch_to.default_content()    

    # 결제하기 버튼 누르기
    print("결제하기 버튼 누름.")
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "LargeNextBtnImage")))
    pay_button = driver.find_element(By.ID, "LargeNextBtnImage")
    pay_button.click()    

    # 카카오 페이 창 전환
    # 새 창이나 탭이 열릴 때까지 기다림
    WebDriverWait(driver, wait_sec).until(lambda d: len(d.window_handles) > 2)
    window_handles = driver.window_handles
    driver.switch_to.window(window_handles[2])

    # 카톡결제 누르기
    # iframe으로 전환
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "kakaoiframe")))
    iframe_bookstep = driver.find_element(By.ID, "kakaoiframe")
    driver.switch_to.frame(iframe_bookstep)    
    
    # 카톡결제 클릭
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'kakaotalk')]")))
    kakaotalk_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'kakaotalk')]")
    # kakaotalk_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'button-menu') and contains(@class, 'kakaotalk')]")
    kakaotalk_btn.click()

    # 휴대폰 번호 입력.
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "userPhone")))
    input_element = driver.find_element(By.ID, 'userPhone')
    input_element.send_keys(kakao_phone_number)

    # 생년월일 입력.
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.ID, "userBirth")))
    input_element = driver.find_element(By.ID, 'userBirth')
    input_element.send_keys(kakao_birth_date)

    # <button class="button-request btn_payask on">결제요청</button>
    # 결제요청 클릭
    WebDriverWait(driver, wait_sec).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'btn_payask') and contains(@class, 'on')]")))
    pay_request_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'btn_payask') and contains(@class, 'on')]")
    pay_request_btn.click()

    break

print('end')