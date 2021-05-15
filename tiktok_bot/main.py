import os
import pickle
import random
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

from config import vk_phone, vk_password

# Переменная для хранения ссылки на видео, которое мы будем лайкать
post_url = 'https://www.tiktok.com/@bill7yt/video/6960998810348768518'


class TikTokBot:
    """Класс, содержащий весь функционал для работы с ботом"""

    def __init__(self, vk_phone, vk_password):
        self.class_name = ''
        self.vk_phone = vk_phone
        self.vk_password = vk_password
        options = webdriver.FirefoxOptions()
        options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0"
        )
        options.set_preference('dom.webdriver.enabled', False)
        self.driver = webdriver.Firefox(
            executable_path='firefoxdriver/geckodriver',
            options=options
        )

    def xpath_exists(self, xpath):
        """Метод для проверки наличия элемента по Xpath"""
        try:
            self.driver.find_element_by_xpath(xpath)
            exist = True
            print(xpath)
        except NoSuchElementException:
            exist = False
        return exist

    def class_exists(self, class_name):
        """Метод для проверки наличия элемента по его классу"""
        try:
            self.driver.find_element_by_class_name(class_name)
            print(class_name)
            self.class_name = class_name
            exist = True
        except NoSuchElementException:
            print('Class does not exist')
            exist = False
        return exist

    def close_driver(self):
        """Метод для закрытия драйвера бота"""
        self.driver.close()
        self.driver.quit()

    def get_cookies(self):
        """Метод для первичной авторизации и получения куков"""
        print('No cookies! Trying to log in...')
        self.driver.implicitly_wait(10)
        self.driver.get('https://www.tiktok.com/')

        # Небольшой костыль
        # Дело в том, что тикток с вероятностью 50 на 50 выдает нам разные верстки, внешне они ничем не отличаются
        # но названия классов элементов разнятся. В связи с этим приходится обрабатывать оба возможных сценария
        if self.class_exists("login-button") or self.class_exists('tiktok-1n6furx-Button-StyledLoginButton'):
            try:
                # нажимаем на кнопку входа
                self.driver.find_element_by_class_name(self.class_name).click()
                self.driver.implicitly_wait(10)
                # ищем айфрэйм
                if self.xpath_exists('/html/body/div[2]/div[1]/iframe'):
                    iframe = self.driver.find_element_by_xpath('/html/body/div[2]/div[1]/iframe')
                elif self.xpath_exists('/html/body/div[4]/div[2]/div/iframe'):
                    iframe = self.driver.find_element_by_xpath('/html/body/div[4]/div[2]/div/iframe')

                # переходим на айфрэйм
                self.driver.switch_to.frame(iframe)
                self.driver.implicitly_wait(7)

                # нажимаем на вход через ВК. Тут тикток тоже подкидывает разные сюрпризы
                if self.xpath_exists("//div[contains(text(), 'VK')]"):
                    self.driver.find_element_by_xpath("//div[contains(text(), 'VK')]").click()
                elif self.xpath_exists("//div[contains(text(), 'Log in with VK']"):
                    self.driver.find_element_by_xpath("//div[contains(text(), 'Log in with VK')]").click()
                elif self.xpath_exists("//div[contains(text(), 'Войти через VK']"):
                    self.driver.find_element_by_xpath("//div[contains(text(), 'Войти через VK')]").click()
                self.driver.implicitly_wait(5)

                # переходим на новую открывшуюся вкладку
                self.driver.switch_to.window(self.driver.window_handles[1])
                time.sleep(3)

                # вводим логин
                email_input = self.driver.find_element_by_name('email')
                email_input.clear()
                email_input.send_keys(vk_phone)
                time.sleep(5)

                # вводим пароль
                password_input = self.driver.find_element_by_name('pass')
                password_input.clear()
                password_input.send_keys(vk_password, Keys.ENTER)
                time.sleep(15)

                # возвращаемся на главную вкладку после входа
                self.driver.switch_to.window(self.driver.window_handles[0])

                # coockies
                cookie = open(f"cookies/{vk_phone}_cookies", 'wb')
                pickle.dump(self.driver.get_cookies(), cookie)  # сохраняем куки
                cookie.close()
                print('You are in! Good job! Cookies saved!')
                self.close_driver()
            except Exception as ex:
                print('Exception: ', ex)
                self.close_driver()
        else:
            print('Oops... Something was wrong...')
            self.close_driver()

    def set_like(self, post_url):
        """Метод для повторной авторизации через куки и выставления лайка"""

        try:
            self.driver.get('https://www.tiktok.com/')
            time.sleep(4)
            # Загружаем куки
            for cookie in pickle.load(open(f"cookies/{vk_phone}_cookies", 'rb')):
                self.driver.add_cookie(cookie)
            time.sleep(2)
            self.driver.refresh()
            time.sleep(3)

            # Ищем кнопку логина. Если ее нет, значит мы вошли и можно лайкать, в противном случае, что-то не так
            if not self.class_exists(self.class_name):
                print('Log in successfully!')

                self.driver.get(url=post_url)
                time.sleep(random.randrange(3, 7))
                item_video_container = self.driver.find_element_by_class_name('item-video-container').click()
                time.sleep(random.randrange(3, 7))
                like_span = self.driver.find_element_by_class_name(
                    'action-wrapper-v2'
                ).find_element_by_class_name('icons')

                if 'liked' in like_span.get_attribute('class').split():
                    print('Sorry, You already liked this post!')
                else:
                    like_button = self.driver.find_element_by_class_name('like').click()
                    time.sleep(random.randrange(3, 8))
                    close_button = self.driver.find_element_by_class_name('close').click()
                    time.sleep(random.randrange(3, 8))
                    print('Yeah! You liked the post!')
                self.close_driver()
            else:
                print('Bad log in, try again!')
                self.close_driver()
        except Exception as ex:
            print(ex)
            print('Check the URL please!')
            self.close_driver()


def main():
    tiktok_bot = TikTokBot(vk_phone=vk_phone, vk_password=vk_password)  # Создаем экземпляр бота
    # Если куков еще нет, то создаем их, в противном случае авторизуемся и лайкаем
    if not os.path.exists(f"cookies/{vk_phone}_cookies"):
        tiktok_bot.get_cookies()
    else:
        tiktok_bot.set_like(post_url=post_url)


if __name__ == '__main__':
    main()
