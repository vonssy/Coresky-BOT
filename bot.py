from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from datetime import datetime
from colorama import *
import asyncio, base64, json, cv2, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Coresky:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://www.coresky.com",
            "Referer": "https://www.coresky.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://www.coresky.com"
        self.ref_code = "s9ztsx" # U can change it with yours.
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}
        self.project_id = "21748"

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Coresky - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_project_id(self):
        try:
            with open("project_id.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
        
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address

            return address
        except Exception as e:
            return None
    
    def generate_payload(self, account: str, address: str):
        try:
            message = f"Welcome to CoreSky!\n\nClick to sign in and accept the CoreSky Terms of Service.\n\nThis request will not trigger a blockchain transaction or cost any gas fees.\n\nYour authentication status will reset after 24 hours.\n\nWallet address:\n\n{address}"
            encoded_message = encode_defunct(text=message)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "address":address,
                "signature":signature,
                "refCode":self.ref_code,
                "projectId":"0"
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
    
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account
        except Exception as e:
            return None

    def decode_base64_to_image(self, base64_str, filename):
        folder_path = "images"
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            full_path = os.path.join(folder_path, filename)
            with open(full_path, "wb") as f:
                f.write(base64.b64decode(base64_str))

            return full_path
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

    def find_slider_position(self, bg_path, piece_path):
        try:
            bg = cv2.imread(bg_path, 0)
            piece = cv2.imread(piece_path, 0)
            result = cv2.matchTemplate(bg, piece, cv2.TM_CCOEFF_NORMED)
            _, _, _, max_loc = cv2.minMaxLoc(result)
            x, y = max_loc
            return x
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

    def calculate_final_x(self, slider_left_px, captcha_image_width_px=310):
        try:
            final_x = round(310 * (slider_left_px / captcha_image_width_px), 2)
            
            return final_x
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

    def aes_encrypt(self, data_str, secret_key):
        try:
            key = secret_key.encode('utf-8')
            cipher = AES.new(key, AES.MODE_ECB)
            ct_bytes = cipher.encrypt(pad(data_str.encode('utf-8'), AES.block_size))

            return base64.b64encode(ct_bytes).decode('utf-8')
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

    def generate_point_json(self, x, y, secret_key):
        try:
            point = {"x": x, "y": y}
            point_str = json.dumps(point, separators=(',', ':'))

            return self.aes_encrypt(point_str, secret_key)
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

    def generate_response_token(self, token, secret_key, x, y):
        try:
            point = {"x": x, "y": y}
            point_str = json.dumps(point, separators=(',', ':'))
            message = f"{token}---{point_str}"

            return self.aes_encrypt(message, secret_key)
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
    
    def generate_encrypted_data(self, captcha_token, secret_key, original_base64, jigsaw_base64):
        try:
            bg_path = self.decode_base64_to_image(original_base64, "background.png")
            piece_path = self.decode_base64_to_image(jigsaw_base64, "piece.png")

            x_pos = self.find_slider_position(bg_path, piece_path)
            bg_img = cv2.imread(bg_path, 0)
            captcha_width = bg_img.shape[1]
            final_x = self.calculate_final_x(x_pos, captcha_width)

            point_json = self.generate_point_json(final_x, 5, secret_key)
            response_token = self.generate_response_token(captcha_token, secret_key, final_x, 5)

            return point_json, response_token
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxyscrape Free Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Proxyscrape Free" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def user_login(self, account: str, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/login"
        data = json.dumps(self.generate_payload(account, address))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Token": ""
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def user_token(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/token"
        headers = {
            **self.headers,
            "Content-Length": "2",
            "Content-Type": "application/json",
            "Token": self.access_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json={}, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def get_captcha(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/captcha/get"
        data = json.dumps({"captchaType":"blockPuzzle"})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Token": self.access_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def check_captcha(self, address: str, point_json: str, captcha_token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/captcha/check"
        data = json.dumps({"captchaType":"blockPuzzle", "pointJson":point_json, "token":captcha_token})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Token": self.access_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def claim_checkin(self, address: str, response_token: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/taskwall/meme/sign"
        data = json.dumps({"responseToken":response_token})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Token": self.access_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def perform_vote(self, address: str, unvoted_points: int, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/taskwall/meme/vote"
        data = json.dumps({"projectId":int(self.project_id), "voteNum":unvoted_points})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
            "Token": self.access_tokens[address]
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, ssl=False) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
            
    async def process_user_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy    :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            login = await self.user_login(account, address, proxy)
            if isinstance(login, dict) and login.get("message") == "success":
                self.access_tokens[address] = login["debug"]["token"]

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}Status   :{Style.RESET_ALL}"
                    f"{Fore.GREEN + Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )
                return True
            
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status   :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Login Failed {Style.RESET_ALL}"
            )

            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
                await asyncio.sleep(5)
                continue

            return False
        
    async def process_solving_captcha(self, address: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            captcha = await self.get_captcha(address, proxy)
            if isinstance(captcha, dict) and captcha.get("message") == "success":
                captcha_token = captcha.get("debug", {}).get("token")
                secret_key = captcha.get("debug", {}).get("secretKey")
                original_base64 = captcha.get("debug", {}).get("originalImageBase64")
                jigsaw_base64 = captcha.get("debug", {}).get("jigsawImageBase64")

                point_json, response_token = self.generate_encrypted_data(captcha_token, secret_key, original_base64, jigsaw_base64)

                check = await self.check_captcha(address, point_json, captcha_token, proxy)
                if isinstance(check, dict) and check.get("message") == "success":
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}Captcha:{Style.RESET_ALL}"
                        f"{Fore.GREEN+Style.BRIGHT} Solved Successfully {Style.RESET_ALL}"
                    )
                    return response_token

                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT}Captcha:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Solved, {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}Retrying...{Style.RESET_ALL}"
                )
                await asyncio.sleep(5)
                continue

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Captcha:{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Captcha Image Failed {Style.RESET_ALL}"
            )
            return False

    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(account, address, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            balance = "NaN"
            token = await self.user_token(address, proxy)
            if isinstance(token, dict) and token.get("message") == "success":
                balance = token.get("debug", {}).get("score", 0)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Balance  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} Unvoted PTS {Style.RESET_ALL}"
            )

            self.log(f"{Fore.CYAN+Style.BRIGHT}Check-In :{Style.RESET_ALL}")

            response_token = await self.process_solving_captcha(address, use_proxy)
            if response_token:
                checkin = await self.claim_checkin(address, response_token, proxy)
                if isinstance(checkin, dict) and checkin.get("message") == "success":
                    checkin_day = checkin.get("debug", {}).get("signDay", "N/A")
                    reward = checkin.get("debug", {}).get("task", {}).get("rewardPoint", None)

                    if not reward:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Status :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} Day {checkin_day} {Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT}Already Claimed{Style.RESET_ALL}"
                        )
                    else:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Status :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} Day {checkin_day} {Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT}Claimed Successfully{Style.RESET_ALL}"
                        )
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Reward :{Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT} {reward} PTS {Style.RESET_ALL}"
                        )

                else:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   > {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}Status :{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not Claimed {Style.RESET_ALL}"
                    )

            token = await self.user_token(address, proxy)
            if isinstance(token, dict) and token.get("message") == "success":
                unvoted_points = token.get("debug", {}).get("score", 0)

                if unvoted_points > 0:
                    vote = await self.perform_vote(address, unvoted_points, proxy)
                    if isinstance(vote, dict) and vote.get("message") == "success":
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Meme Vote:{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                        )
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT} Project Id : {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{self.project_id}{Style.RESET_ALL}"
                        )
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT} Vote Amount: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{unvoted_points} PTS{Style.RESET_ALL}"
                        )

                    else:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Meme Vote:{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                        )
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Meme Vote:{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Avaialble Unvoted PTS {Style.RESET_ALL}"
                    )
            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Meme Vote:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} NaN Unvoted PTS {Style.RESET_ALL}"
                )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            project_id = self.load_project_id()
            if project_id:
                self.project_id = project_id

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)

                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue
                        
                        await self.process_accounts(account, address, use_proxy, rotate_proxy)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                
                delay = 12 * 60 * 60
                while delay > 0:
                    formatted_time = self.format_seconds(delay)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}All Accounts Have Been Processed...{Style.RESET_ALL}",
                        end="\r",
                        flush=True
                    )
                    await asyncio.sleep(1)
                    delay -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Coresky()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Coresky - BOT{Style.RESET_ALL}                                       "                              
        )