import requests
import time
import uuid
import json
import base64
from io import BytesIO
from openai import OpenAI
from PIL import Image
from django.conf import settings


class NaverOCRClient:

    def __init__(
        self,
        api_url: str = "https://1wo815wdbd.apigw.ntruss.com/custom/v1/32668/2181f7c75ba2a6cd46c6b4732b2c36292cccfd17522ddb4d913914e505a75615/document/receipt",
    ):
        self.headers = {
            "X-OCR-SECRET": "UnZSVFBGemVaWkhCeVZSR3JEV1RwelphSFdISW9tRUI=",  # settings.NAVER_OCR_SECRET_KEY
            "Content-Type": "application/json",
        }
        self.api_url = api_url

    def post(self, request_id, image_name, image_format, image_data):
        payload = {
            "images": [
                {
                    "name": image_name,
                    "format": image_format,
                    "data": image_data,
                }
            ],
            "requestId": request_id,
            "version": "V2",
            "timestamp": int(round(time.time() * 1000)),
        }
        response = requests.request(
            "POST",
            self.api_url,
            headers=self.headers,
            data=json.dumps(payload).encode("UTF-8"),
        )
        return response


class OpenAIChatClient:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def ask(self, system_role, prompt):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_role},
                {"role": "user", "content": prompt},
            ],
        )
        try:
            data = json.loads(response.choices[0].message.content)
            return data
        except (json.JSONDecodeError, KeyError):
            return {}


class ReceiptParser:

    def __init__(self, image: Image):
        self.image = image
        self.ocr_client = NaverOCRClient()
        self.ocr_result = None
        self._validate()

    def _validate(self):
        image_format = self.image.format.lower()
        if image_format not in ["jpeg", "jpg", "png", "bmp", "tiff"]:
            raise ValueError("지원하지 않는 이미지 포맷입니다.")

    def _image_to_base64(self):
        buffered = BytesIO()
        self.image.save(buffered, format=self.image.format)
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_str

    def _run_ocr(self):
        request_id = str(uuid.uuid4())
        image_format = self.image.format.lower()
        response = self.ocr_client.post(
            request_id, f"preview_{request_id}", image_format, self._image_to_base64()
        )
        if response.status_code == 200:
            self.ocr_result = response.json()["images"][0]["receipt"]["result"]

    def _get_store_info(self):
        store_info = {
            "store_name": "",
            "store_business_number": "",
        }
        if "storeInfo" not in self.ocr_result:
            return store_info
        store_info_result = self.ocr_result["storeInfo"]
        store_name_strings = []
        if store_info_result.get("name") and store_info_result["name"].get("text"):
            store_name_strings.append(store_info_result["name"]["text"])
        if store_info_result.get("subName") and store_info_result["subName"].get(
            "text"
        ):
            store_name_strings.append(store_info_result["subName"]["text"])
        store_info["store_name"] = " ".join(store_name_strings)
        if store_info_result.get("bizNum") and store_info_result["bizNum"].get("text"):
            store_info["store_business_number"] = store_info_result["bizNum"]["text"]
        return store_info

    def _get_payment_info(self):
        payment_info = {
            "transaction_time": "",
            "card_info": {
                "company": "",
                "number": "",
            },
        }
        if "paymentInfo" not in self.ocr_result:
            return payment_info
        payment_info_result = self.ocr_result["paymentInfo"]
        transaction_time_strings = []
        if payment_info_result.get("date") and payment_info_result["date"].get("text"):
            transaction_time_strings.append(payment_info_result["date"]["text"])
        if payment_info_result.get("time") and payment_info_result["time"].get("text"):
            transaction_time_strings.append(payment_info_result["time"]["text"])
        payment_info["transaction_time"] = " ".join(transaction_time_strings)
        if (
            payment_info_result.get("cardInfo")
            and payment_info_result["cardInfo"].get("company")
            and payment_info_result["cardInfo"]["company"].get("text")
        ):
            payment_info["card_info"]["company"] = payment_info_result["cardInfo"][
                "company"
            ]["text"]
        if (
            payment_info_result.get("cardInfo")
            and payment_info_result["cardInfo"].get("number")
            and payment_info_result["cardInfo"]["number"].get("text")
        ):
            payment_info["card_info"]["number"] = payment_info_result["cardInfo"][
                "number"
            ]["text"]
        return payment_info

    def _get_total_price(self):
        total_price = {"total_price": ""}
        if "totalPrice" not in self.ocr_result:
            return total_price
        total_price_result = self.ocr_result["totalPrice"]
        if total_price_result.get("price") and total_price_result["price"].get("text"):
            total_price["total_price"] = total_price_result["price"]["text"]
        return total_price

    def _process_receipt(self):
        if self.ocr_result:
            return {
                **self._get_store_info(),
                **self._get_payment_info(),
                **self._get_total_price(),
            }
        output = {
            "store_name": "",
            "store_business_number": "",
            "transaction_time": "",
            "card_info": {
                "company": "",
                "number": "",
            },
            "total_price": "",
        }
        return output

    def parse(self):
        self._run_ocr()
        return self._process_receipt()
