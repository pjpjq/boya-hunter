# -*- coding: utf-8 -*-
from time import sleep
from datetime import datetime
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import confidentials_buaa


def email_image(img_name):
    # Send an HTML email with an embedded image and a plain text message for
    # email clients that don't want to display the HTML.
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage
    from email.header import Header

    import confidentials_email
    sender = confidentials_email.email_user
    receiver = confidentials_email.receiver

    # Create the root message and fill in the from, to, and subject headers
    msg_root = MIMEMultipart('related')
    msg_root['Subject'] = Header('有新博雅了!', 'utf-8').encode()
    msg_root['From'] = sender
    msg_root['To'] = receiver

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msg_alternative = MIMEMultipart('alternative')
    msg_root.attach(msg_alternative)

    msg_text = MIMEText('This is the alternative plain text message.')
    msg_alternative.attach(msg_text)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msg_text = MIMEText('<img src="cid:image1">', 'html')
    # msg_text = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!', 'html')
    msg_alternative.attach(msg_text)

    with open(img_name, 'rb') as img:
        msg_img = MIMEImage(img.read())

    # Define the image's ID as referenced above
    msg_img.add_header('Content-ID', '<image1>')
    msg_root.attach(msg_img)

    import smtplib
    smtp = smtplib.SMTP(confidentials_email.smtp_host)
    smtp.login(sender, confidentials_email.email_password)
    smtp.sendmail(sender, receiver, msg_root.as_string())
    smtp.quit()


def auto_enroll_boya(specific_course_xpath=None, page_loading_delay=2, cool_down=1,
                     driver_executable_path='/usr/local/bin/chromedriver',
                     silent_mode=True, max_n_trials=100000, email_notify=True, show_not_found_elements=False):
    # BUG: 调用的时候同时自己用同样浏览器(eg 这里的 chrome) 手动登录, 会显示页面过期重新登录!??
    # 当前解决方法: 可以换一个浏览器登录...
    # silent_mode = False  # DEBUG
    options = webdriver.ChromeOptions()
    if silent_mode:
        options.add_argument("headless")
    driver = webdriver.Chrome(executable_path=driver_executable_path, chrome_options=options)

    vpn_login_url = "https://e.buaa.edu.cn/users/sign_in"
    driver.get(vpn_login_url)
    elem = driver.find_element_by_name("user[login]")
    elem.clear()
    elem.send_keys(confidentials_buaa.username)
    elem = driver.find_element_by_name("user[password]")
    elem.clear()
    elem.send_keys(confidentials_buaa.password)
    elem.send_keys(Keys.RETURN)
    sleep(page_loading_delay)

    boyaketang_xpath = "/html/body/div[4]/div/ul/li[12]/a"
    driver.find_element_by_xpath(boyaketang_xpath).click()
    driver.switch_to.window(driver.window_handles[-1])
    sleep(page_loading_delay * 2)

    # 不等5s!
    driver.find_element_by_xpath("/html/body/main/div[1]/div/div/div[2]/div[2]/button").click()
    sleep(page_loading_delay)

    wodekecheng_xpath = "/html/body/main/div[1]/aside/div/ul/li[3]/div/div/div/i[1]"
    driver.find_element_by_xpath(wodekecheng_xpath).click()
    kechengxuanze_xpath = "/html/body/main/div[1]/aside/div/ul/li[3]/div/ul/li[2]"
    driver.find_element_by_xpath(kechengxuanze_xpath).click()
    sleep(page_loading_delay)

    # TODO: 直接搜课名会小心选上退不了的课
    n_successes = 0
    for n_trials in range(max_n_trials):
        try:
            refresh_xpath = "/html/body/main/div[1]/div/div/div[2]/div[1]/div/div/div/div/div[1]/div[2]/a"
            driver.find_element_by_xpath(refresh_xpath).click()
            sleep(page_loading_delay)

            if not specific_course_xpath:
                success_link_text = "报名课程"
                driver.find_element_by_link_text(success_link_text).click()
            else:
                driver.find_element_by_xpath(specific_course_xpath)
            sleep(page_loading_delay)

            yes_i_am_sure_xpath = "/html/body/div[1]/div/div/div[3]/button[2]"
            driver.find_element_by_xpath(yes_i_am_sure_xpath).click()
            print("{} 选到了一个博雅!".format(datetime.now().time()))
            n_successes += 1
            sleep(page_loading_delay)

            screenshot_name = "screenshot-" + str(datetime.now().time()) + ".png"
            driver.save_screenshot(screenshot_name)
            if email_notify:
                email_image(screenshot_name)

            if specific_course_xpath and n_successes > 0:
                break
        except NoSuchElementException as e:
            if show_not_found_elements:
                print("{} {}".format(datetime.now().time(), e))
        except Exception as e:
            print("{} {}".format(datetime.now().time(), e))

        if (n_trials + 1) % 1000 == 0:
            print("{} tried for {} times with {} successes".format(datetime.now().time(), n_trials + 1, n_successes))
        sleep(cool_down)

    # Done, 续几秒就关了她
    sleep(5 * cool_down)
    driver.close()


def main():
    idx = 1
    specific_course_xpath = "/html/body/main/div[1]/div/div/div[2]/div[1]/div/div/div/div/div[2]/table/tbody/tr[{}]/td[9]/a[2]".format(
        idx)
    auto_enroll_boya(specific_course_xpath)
    # email_image("niunai.jpg")


if __name__ == '__main__':
    main()
