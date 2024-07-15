import requests
import time
import uuid
import json
import base64
from io import BytesIO
from openai import OpenAI
from PIL import Image
from django.conf import settings


"""
from approval.ocr import ReceiptParser
from PIL import Image
image = Image.open("/Users/siyoungbyun/Downloads/30004_craw1.jpg")
parser = ReceiptParser(image)
response = parser.parse()
"""


class NaverOCRClient:

    def __init__(
        self,
        api_url: str = "https://g9gkfwgi5u.apigw.ntruss.com/custom/v1/32152/246b6aeab072b47e22d1c8148b95f123ec2f759e655caee63fe4bf5f7f26da31/document/receipt",
    ):
        self.headers = {
            "X-OCR-SECRET": "",  # settings.NAVER_OCR_SECRET_KEY
            "Content-Type": "application/json",
        }
        self.api_url = api_url

    def post(self, request_id, image_name, image_format, image_data):
        # payload = {
        #     "images": [
        #         {
        #             "name": image_name,
        #             "format": image_format,
        #             "data": image_data,
        #         }
        #     ],
        #     "requestId": request_id,
        #     "version": "V2",
        #     "timestamp": int(round(time.time() * 1000)),
        # }
        # response = requests.request(
        #     "POST",
        #     self.api_url,
        #     headers=self.headers,
        #     data=json.dumps(payload).encode("UTF-8"),
        # )
        # return response
        # TODO: API 허가 나올 때까지 더미 데이터 사용
        response = {
            "result": {
                "storeInfo": {
                    "name": {
                        "text": "emart everyday",
                        "formatted": {"value": "emart everyday"},
                        "boundingBoxes": [
                            [[513, 190], [762, 195], [760, 275], [511, 270]],
                            [[516, 264], [756, 269], [755, 329], [515, 324]],
                        ],
                    },
                    "subName": {
                        "text": "분당정자2점",
                        "formatted": {"value": "분당정자2점"},
                        "boundingBoxes": [
                            [[1035, 202], [1191, 199], [1192, 238], [1036, 241]]
                        ],
                    },
                    "bizNum": {
                        "text": "212-81-25544",
                        "formatted": {"value": "212-81-25544"},
                        "boundingBoxes": [
                            [[784, 244], [1005, 241], [1006, 276], [784, 279]]
                        ],
                    },
                    "address": [
                        {
                            "text": "경기 성남시 분당구 정자일로 120",
                            "formatted": {"value": "경기 성남시 분당구 정자일로 120"},
                            "boundingBoxes": [
                                [[786, 284], [845, 284], [845, 321], [786, 321]],
                                [[845, 282], [932, 282], [932, 320], [845, 320]],
                                [[929, 279], [1016, 279], [1016, 320], [929, 320]],
                                [[1016, 279], [1129, 279], [1129, 320], [1016, 320]],
                                [[1129, 280], [1193, 280], [1193, 316], [1129, 316]],
                            ],
                        }
                    ],
                    "tel": [
                        {
                            "text": "(031)786-1171",
                            "formatted": {"value": "0317861171"},
                            "boundingBoxes": [
                                [[1114, 238], [1398, 233], [1399, 277], [1115, 281]]
                            ],
                        }
                    ],
                },
                "paymentInfo": {
                    "date": {
                        "text": "2020-04-16",
                        "formatted": {"year": "2020", "month": "04", "day": "16"},
                        "boundingBoxes": [
                            [[511, 504], [843, 504], [843, 546], [511, 546]]
                        ],
                    },
                    "time": {
                        "text": "20: 11",
                        "formatted": {"hour": "20", "minute": "11", "second": "00"},
                        "boundingBoxes": [
                            [[854, 511], [912, 511], [912, 545], [854, 545]],
                            [[912, 511], [952, 511], [952, 545], [912, 545]],
                        ],
                    },
                    "cardInfo": {
                        "company": {
                            "text": "신 한",
                            "formatted": {"value": "신한"},
                            "boundingBoxes": [
                                [[604, 1145], [650, 1145], [650, 1191], [604, 1191]],
                                [[684, 1146], [727, 1146], [727, 1191], [684, 1191]],
                            ],
                        },
                        "number": {
                            "text": "4221**8686",
                            "formatted": {"value": "4221**8686"},
                            "boundingBoxes": [
                                [[1022, 1147], [1399, 1157], [1398, 1197], [1021, 1187]]
                            ],
                        },
                    },
                    "confirmNum": {
                        "text": "28672931",
                        "boundingBoxes": [
                            [[1022, 1147], [1399, 1157], [1398, 1197], [1021, 1187]]
                        ],
                    },
                },
                "subResults": [
                    {
                        "items": [
                            {
                                "name": {
                                    "text": "씨그램 레몬350ml",
                                    "formatted": {"value": "씨그램 레몬350ml"},
                                    "boundingBoxes": [
                                        [
                                            [607, 675],
                                            [727, 675],
                                            [727, 721],
                                            [607, 721],
                                        ],
                                        [
                                            [743, 674],
                                            [919, 678],
                                            [918, 722],
                                            [742, 719],
                                        ],
                                    ],
                                },
                                "count": {
                                    "text": "2",
                                    "formatted": {"value": "2"},
                                    "boundingBoxes": [
                                        [
                                            [1173, 680],
                                            [1204, 680],
                                            [1204, 718],
                                            [1173, 718],
                                        ]
                                    ],
                                },
                                "priceInfo": {
                                    "price": {
                                        "text": "1,600",
                                        "formatted": {"value": "1600"},
                                        "boundingBoxes": [
                                            [
                                                [1293, 679],
                                                [1398, 679],
                                                [1398, 718],
                                                [1293, 718],
                                            ]
                                        ],
                                    },
                                    "unitPrice": {
                                        "text": "800",
                                        "formatted": {"value": "800"},
                                        "boundingBoxes": [
                                            [
                                                [1059, 680],
                                                [1127, 680],
                                                [1127, 718],
                                                [1059, 718],
                                            ]
                                        ],
                                    },
                                },
                            },
                            {
                                "name": {
                                    "text": "씨그램 라임350ml",
                                    "formatted": {"value": "씨그램 라임350ml"},
                                    "boundingBoxes": [
                                        [
                                            [607, 759],
                                            [727, 759],
                                            [727, 807],
                                            [607, 807],
                                        ],
                                        [
                                            [743, 761],
                                            [918, 761],
                                            [918, 805],
                                            [743, 805],
                                        ],
                                    ],
                                },
                                "count": {
                                    "text": "1",
                                    "formatted": {"value": "1"},
                                    "boundingBoxes": [
                                        [
                                            [1177, 770],
                                            [1200, 770],
                                            [1200, 796],
                                            [1177, 796],
                                        ]
                                    ],
                                },
                                "priceInfo": {
                                    "price": {
                                        "text": "800",
                                        "formatted": {"value": "800"},
                                        "boundingBoxes": [
                                            [
                                                [1329, 764],
                                                [1398, 764],
                                                [1398, 804],
                                                [1329, 804],
                                            ]
                                        ],
                                    },
                                    "unitPrice": {
                                        "text": "800",
                                        "formatted": {"value": "800"},
                                        "boundingBoxes": [
                                            [
                                                [1059, 766],
                                                [1125, 766],
                                                [1125, 802],
                                                [1059, 802],
                                            ]
                                        ],
                                    },
                                },
                            },
                            {
                                "name": {
                                    "text": "삼다수2L",
                                    "formatted": {"value": "삼다수2L"},
                                    "boundingBoxes": [
                                        [[607, 845], [766, 845], [766, 895], [607, 895]]
                                    ],
                                },
                                "count": {
                                    "text": "6",
                                    "formatted": {"value": "6"},
                                    "boundingBoxes": [
                                        [
                                            [1175, 855],
                                            [1200, 855],
                                            [1200, 886],
                                            [1175, 886],
                                        ]
                                    ],
                                },
                                "priceInfo": {
                                    "price": {
                                        "text": "6,240",
                                        "formatted": {"value": "6240"},
                                        "boundingBoxes": [
                                            [
                                                [1289, 852],
                                                [1396, 852],
                                                [1396, 891],
                                                [1289, 891],
                                            ]
                                        ],
                                    },
                                    "unitPrice": {
                                        "text": "1,040",
                                        "formatted": {"value": "1040"},
                                        "boundingBoxes": [
                                            [
                                                [1025, 852],
                                                [1127, 852],
                                                [1127, 891],
                                                [1025, 891],
                                            ]
                                        ],
                                    },
                                },
                            },
                            {
                                "name": {
                                    "text": "크리넥스 K/T 150*8",
                                    "formatted": {"value": "크리넥스 K/T 150*8"},
                                    "boundingBoxes": [
                                        [
                                            [609, 889],
                                            [766, 889],
                                            [766, 939],
                                            [609, 939],
                                        ],
                                        [
                                            [777, 895],
                                            [841, 895],
                                            [841, 930],
                                            [777, 930],
                                        ],
                                        [
                                            [855, 893],
                                            [954, 893],
                                            [954, 929],
                                            [855, 929],
                                        ],
                                    ],
                                },
                                "count": {
                                    "text": "1",
                                    "formatted": {"value": "1"},
                                    "boundingBoxes": [
                                        [
                                            [1177, 900],
                                            [1200, 900],
                                            [1200, 929],
                                            [1177, 929],
                                        ]
                                    ],
                                },
                                "priceInfo": {
                                    "price": {
                                        "text": "8,800",
                                        "formatted": {"value": "8800"},
                                        "boundingBoxes": [
                                            [
                                                [1289, 896],
                                                [1402, 896],
                                                [1402, 936],
                                                [1289, 936],
                                            ]
                                        ],
                                    },
                                    "unitPrice": {
                                        "text": "8,800",
                                        "formatted": {"value": "8800"},
                                        "boundingBoxes": [
                                            [
                                                [1023, 895],
                                                [1125, 895],
                                                [1125, 934],
                                                [1023, 934],
                                            ]
                                        ],
                                    },
                                },
                            },
                        ]
                    }
                ],
                "totalPrice": {
                    "price": {
                        "text": "17,080",
                        "formatted": {"value": "17080"},
                        "boundingBoxes": [
                            [[1271, 1068], [1400, 1068], [1400, 1111], [1271, 1111]]
                        ],
                    }
                },
            },
            "meta": {},
        }
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
        # self.openai_chat_client = OpenAIChatClient()
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

    def _clean_text(self, response):

        string_result = ""
        for i in response["images"][0]["fields"]:
            if i.get("lineBreak", False):
                linebreak = "\n"
            else:
                linebreak = " "
            string_result += i["inferText"] + linebreak
        return string_result

    def _extract_text(self):
        request_id = str(uuid.uuid4())
        image_format = self.image.format.lower()
        response = self.ocr_client.post(
            request_id, f"preview_{request_id}", image_format, self._image_to_base64()
        )
        return response

    def _process_receipt(self, response):
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
        result = response["result"]
        store_info = result["storeInfo"]
        payment_info = result["paymentInfo"]
        total_price = result["totalPrice"]
        output["store_name"] = (
            store_info["name"]["text"] + " " + store_info["subName"]["text"]
        )
        output["store_business_number"] = store_info["bizNum"]["text"]
        output["transaction_time"] = (
            payment_info["date"]["text"] + " " + payment_info["time"]["text"]
        )
        output["card_info"]["company"] = payment_info["cardInfo"]["company"]["text"]
        output["card_info"]["number"] = payment_info["cardInfo"]["number"]["text"]
        output["total_price"] = total_price["price"]["text"]

        return output

    # def _extract_receipt_metadata(self, text):
    #     system_role = "You are a helpful assistant that extracts store information from receipts and output it in JSON format."
    #     prompt = f"""
    #     Please analyze the following receipt and extract the store name, address, phone number, and total amount. The receipt text is as follows:
    #     {text}
    #     Please return the result in JSON format with the keys "store_name", "address", "phone", and "total_amount".
    #     If the information is not available, set the value to an empty string.
    #     """
    #     metadata = self.openai_chat_client.ask(system_role, prompt)
    #     return metadata
    #
    # def _extract_receipt_listing(self, text):
    #     system_role = "You are a helpful assistant to analyze the purchase date, items, quantity, and amount from the receipt and output it in JSON format."
    #     prompt = f"""
    #      f'please analyze {text}. only items and date. If an item is free, set its cost to 0'
    #     """
    #     listing = self.openai_chat_client.ask(system_role, prompt)
    #     return listing

    def parse(self):
        response = self._extract_text()
        return self._process_receipt(response)
        # print(text)
        response = {}
        # for _ in range(3):
        #     metadata = self._extract_receipt_metadata(text)
        #     if metadata:
        #         break
        # listing = self._extract_receipt_listing(text)
        # for _ in range(3):
        #     listing = self._extract_receipt_listing(text)
        #     if listing:
        #         break
        # return {"metadata": metadata, "listing": listing}
