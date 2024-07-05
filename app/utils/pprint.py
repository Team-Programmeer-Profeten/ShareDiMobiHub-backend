import datetime
from colorama import Fore
from colorama import Style
from colorama import init
from threading import Semaphore
init()

class Pprint():

    """
    This class is responsible for the pretty printing of the logs

    Attributes:
    task: int
    screenlock: Semaphore
    specification: str
    siteName: str

    Methods:
    printt: prints the message with the correct color
    """

    def __init__(self, task_id, specification, siteName):
        self.task = task_id
        self.screenlock = Semaphore(1)
        self.specification = specification
        self.siteName = siteName


    def printt(self, message, colorType='normal'):
        message = str(message)
        now = datetime.datetime.now()
        time = Fore.WHITE + Style.BRIGHT + f'[{now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]}]' + Fore.RESET
        if (self.task < 10):
            currentTask = f'Task 0{str(self.task)} |'
        else:
            currentTask = f'Task {str(self.task)} |'
        specification = f'[{self.specification}]'
        site = f'[{self.siteName}]'

        self.screenlock.acquire()
        if colorType == 'good':
            print(time + Fore.GREEN + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        elif colorType == 'bad':
            print(time + Fore.RED + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        elif colorType == 'normal':
            print(time + Fore.YELLOW + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        elif colorType == 'carted':
            print(time + Fore.MAGENTA + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        elif colorType == 'misc':
            print(time + Fore.CYAN + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        elif colorType == 'blue':
            print(time + Fore.BLUE + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        elif colorType == 'grey':
            print(time + Fore.BLACK + Style.BRIGHT, site, specification, currentTask, message + Fore.RESET)
        self.screenlock.release()