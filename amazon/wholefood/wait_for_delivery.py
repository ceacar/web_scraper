"""
this file is for those poorlings who cannot get a delivery slot from whole food
"""
import sys
import time
import os
import random
import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver


class Spinner:
    """
    a simple spinner
    """
    @classmethod
    def spinning_cursor(cls):
        """
        yields spinner character
        """
        while True:
            for cursor in ['|/-\\']:
                yield cursor * 10

    def __init__(self):
        pass

    def spin(self):
        """
        spins
        """
        spinner = self.spinning_cursor()
        for _ in range(50):
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            time.sleep(0.1)
            sys.stdout.write('\b')


class WholeFoodCrazyBuyer:
    '''
    #-- FireFox
    caps = webdriver.DesiredCapabilities().FIREFOX
    caps["marionette"] = True
    browser = webdriver.Firefox(capabilities=caps)
    '''
    UBUNTU_CHROME_CACHE_LOCATION = os.path.expanduser("~/.config/google-chrome/Default")

    def __init__(self):
        self.state = "login"
        self.start_url = 'https://amazon.com/'
        self.get_browser()
        self.action_sequence = ["click_cart", "click_checkout", "skip_upsell"]

        self.action_list = {
            "click_cart": {
                "func": self.browser.find_element_by_xpath,
                "search_pattern": "//span[contains(@class, 'nav-cart-icon nav-sprite')]",
                # initial_state is the page where you want to perform the action like clicking
                "initial_state": "login",
                # every action needs to verify what state it has reached, so we can keep track of action
                "expected_state": "view_cart",
                "partial_url_match_string": 'https://www.amazon.com/gp/cart/view.html?ref_=nav_cart',
                "button_action_type": "click",
                # any error, we will try to roll back to login
                "state_recover_to": "login",
            },
            "click_checkout": {
                "func": self.browser.find_element_by_xpath,
                "search_pattern": "//span[contains(@id, 'sc-alm-buy-box-ptc-button-')]",
                # initial_state is the page where you want to perform the action like clicking
                "initial_state": "view_cart",
                # every action needs to verify what state it has reached, so we can keep track of action
                "expected_state": "checkout",
                "partial_url_match_string": "https://www.amazon.com/gp/buy/shipoptionselect/handlers/display.html",
                "button_action_type": "click",
                "state_recover_to": "login",
            },
            "skip_upsell": {
                "func": self.browser.find_element_by_name,
                "search_pattern": "proceedToCheckout",
                # initial_state is the page where you want to perform the action like clicking
                "initial_state": "checkout",
                # every action needs to verify what state it has reached, so we can keep track of action
                "expected_state": "skipped_upsell",
                "partial_url_match_string": "https://www.amazon.com/gp/buy/shipoptionselect/handlers/display.html",
                "button_action_type": "click",
                "state_recover_to": "login",
            },

        }

    def get_browser(self, profile_location="~/.config/google-chrome/Default"):
        """
        returns a brwoser(chrome_webdrive)
        """
        profile_location = os.path.expanduser("~/.config/google-chrome/Default")
        options = Options()
        user_data_config_for_options = f"user-data-dir={profile_location}"
        options.add_argument(user_data_config_for_options)
        self.browser = webdriver.Chrome(chrome_options=options)

    def assess_state(self, partial_correct_url, state_string):
        """
        verifies the current state with state_string(desired state)
        returns the current state
        """
        if partial_correct_url not in self.browser.current_url:
            # state error, we need to go back to initial state which is login
            current_state = "login"
        else:
            current_state = state_string

        return current_state

    @classmethod
    def button_do(cls, button, action="click"):
        """
        this functions will do a button action, this function is expandable
        """
        if action == "click":
            button.click()

    def do_action(self, desired_action):
        """
        this function basically does below code, but in a reuseable way
        cart_icon = self.browser.find_element_by_xpath("//span[contains(@class, 'nav-cart-icon nav-sprite')]")
        cart_icon.click()
        self.state = self.assess_state('https://www.amazon.com/gp/cart/view.html?ref_=nav_cart', "view_cart")
        """
        initial_state = desired_action["initial_state"]
        # check if we are in the correct starting state for sanity
        if self.state != initial_state:
            raise Exception(f"Oops, wrong starting state {self.state} is not in desired {initial_state}")

        func = desired_action["func"]
        search_pattern = desired_action["search_pattern"]
        expected_state = desired_action["expected_state"]
        rollback_state = desired_action["state_recover_to"]
        partial_url_match_string = desired_action["partial_url_match_string"]

        button = func(search_pattern)
        self.button_do(button, "click")

        # assess state with every step
        self.state = self.assess_state(partial_url_match_string, expected_state)
        if self.state != expected_state:
            print(f"Oof, we deviated from {initial_state} to {expected_state}, but we are at {self.state}")
            # we rollback to state where we can start over
            self.state = rollback_state

    @classmethod
    def today_date(cls, date_format="%b %d"):
        """
        return date string like 'Mar 10'
        """
        return datetime.datetime.now().strftime(date_format)

    @classmethod
    def found_slot(cls):
        Spinner().spin()

    def buy(self):
        """
        main run function to run the script, it will loop through the action_sequence
        and take corresponding action
        """
        self.browser.get(self.start_url)
        import ipdb
        ipdb.set_trace()

        for action_type in self.action_sequence:
            action_dict = self.action_list[action_type]
            self.do_action(action_dict)
            time.sleep(1.5)

        while self.state == "skipped_upsell":
            # searching for timeslot here
            self.browser.refresh()
            sleep_time = random.randint(45, 75)
            print(f"sleeping {sleep_time}")
            time.sleep(sleep_time)
            # a-size-base-plus
            today = self.today_date(date_format="%Y-%m-%d")
            today_with_letter = self.today_date()
            element_id = f'slot-container-{today}'
            expected_alert_message = f'Select a time\nDoorstep delivery times for Today, {today_with_letter} are no longer available.'
            div_container = self.browser.find_element_by_id(element_id)
            span_element = div_container.find_element_by_class_name("a-size-base-plus")
            if expected_alert_message not in span_element.text:
                # we might see a page which has an available timeslot
                break
            else:
                self.found_slot()

        self.browser.close()


def main():
    """
    main method to run entire method
    """
    crazydude = WholeFoodCrazyBuyer()
    crazydude.buy()


# inputElement = browser.find_elements_by_class_name("password-input")[0]
# inputElement.send_keys("123hello")
# inputElement.send_keys(Keys.RETURN)
# time.sleep(5)  #seconds

# Give source code to BeautifulSoup
# soup = BeautifulSoup(browser.page_source, 'html.parser')
#
# # Get JavaScript info from site
# top_text = soup.select_one('.result__text.result__before')
# crack_time = soup.select_one('.result__text.result__time')
# bottom_text = soup.select_one('.result__text.result__after')
# print(top_text.text)
# print(crack_time.text)
# print(bottom_text.text)
# time.sleep(5)  #seconds
# browser.close()


if __name__ == '__main__':
    main()
