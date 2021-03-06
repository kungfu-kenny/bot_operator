import os
import requests
from telegram_manager import TelegramManager
from config import (folder_config,
                    # chat_id_default,
                    entrance_bot_img_name,
                    entrance_bot_img_link)

class UserProfiler:
    """
    class which is dedicated to work with the style of this bot;
    It adds musical layer and returns music to send
    """
    def __init__(self) -> None:
        self.folder_current = os.getcwd()
        self.folder_config = os.path.join(self.folder_current, folder_config)
        self.folder_create = lambda x: os.path.exists(x) or os.mkdir(x)

    @staticmethod
    def produce_request(value_link:str) -> object:
        """
        Method for making 
        Input:  value_link = link which is dedicated to make the request
        Output: object valus
        """
        return requests.get(value_link, stream=True)

    def work_on_the_picture(self) -> None:
        """
        Method which is dedicated to download the picture and store it to the folder
        Input:  None
        Output: We stored the folder to the 
        """
        self.folder_create(self.folder_config)
        value_image_used = os.path.join(self.folder_config, entrance_bot_img_name)
        if os.path.exists(value_image_used) and os.path.isfile(value_image_used):
            return value_image_used
        a = TelegramManager()
        try:
            value_img = self.produce_request(entrance_bot_img_link)
            if value_img.status_code == 200:
                with open(value_image_used, 'wb') as new_picture:
                    for chunk in value_img:
                        new_picture.write(chunk)
                return value_image_used
            a.proceed_message_values('Unfortunatelly, your link to the image is not working.')
        except Exception as e:
            a.proceed_message_values(f'We faced problem with the getting requests. Mistake: {e}')
        return ''


if __name__ == '__main__':
    a = UserProfiler()
    a.work_on_the_picture()