import re
from re import Pattern

from aiohttp import InvalidURL
from bs4 import BeautifulSoup as BSoup
from loguru import logger
from yarl import URL

from app.databases.mongo import Database
from app.settings import settings
from app.vetis.base_session import BaseSession
from app.vetis.schemas.base import EnterpriseMainPageSchema
from app.vetis.schemas.milk import MilkRequestSchema, MilkTransactionAfterRequestSchema


class Mercury(BaseSession):
    def __init__(self, user_id: int, db: Database, service_url: URL = settings.BASE_MERCURY_URL):
        super().__init__(service_url=service_url, user_id=user_id, db=db)

    async def login(self, login: str, password: str) -> bool:
        if not await self._check_cookie():
            return await self._auth(login=login, password=password)
        return False

    async def _check_cookie(self) -> bool:
        try:
            await self.load_cookies()
        except FileNotFoundError:
            logger.warning(f"Нет сохраненных куки")
            return False
        response = await self.fetch(self.service_url)
        soup = BSoup(await response.text(), 'html5lib')
        if soup.find('div', {'id': 'loggedas'}):
            self.user = ' '.join((soup.find('div', {'id': 'loggedas'}).find('b')).text.split()[:-1])
            logger.info(f"Куки действительны для пользователя: {self.user}")
            return True
        else:
            self.clear_cookies()
            logger.warning(f"Куки не действительны. Сброс.")
            return False

    async def _auth(self, login: str, password: str):
        response = await self.fetch(self.service_url)
        soup = BSoup(await response.text(), 'html5lib')
        form = soup.find('form')
        fields = form.findAll('input')
        form_data = dict(
            (field.get('name'), field.get('value')) for field in fields if field.get('name') is not None
        )
        response = await self.fetch(form['action'], data=form_data)
        form_data['j_username'] = login
        form_data['j_password'] = password
        form_data['_eventId_proceed'] = ''
        form_data['ksid'] = 'kekw'
        response = await self.fetch(response.history[0].headers['Location'], data=form_data)
        soup = BSoup(await response.text(), 'html5lib')
        form = soup.find('form')
        fields = form.findAll('input')
        form_data = dict(
            (field.get('name'), field.get('value')) for field in fields if field.get('name') is not None
        )
        try:
            response = await self.fetch(form['action'], data=form_data)
            soup = BSoup(await response.text(), 'html5lib')
            self.user = ' '.join((soup.find('div', {'id': 'loggedas'}).find('b')).text.split()[:-1])
            logger.info(f"Выполнен вход: {self.user}")
        except InvalidURL:
            logger.warning(f'Неудачная авторизация.')
            return False
        await self.save_cookies()
        return True

    async def get_enterprises_from_main_page(self) -> list[EnterpriseMainPageSchema]:
        collection = []
        response = await self.fetch(url=f"{self.service_url}/operatorui?_action=changeServicedEnterprise")
        soup = BSoup(await response.text(), 'html5lib').find_all("label", {"class": "active"})
        for label in soup:
            enterprise = {}
            for notification in label.find_all("a", {"class": "notification"}):
                if "входящие всд" in notification.get("title").lower():
                    enterprise["input_documents_href"] = notification.get("href")
                    enterprise["input_documents_count"] = notification.get_text(strip=True)
                elif "входящие заявки от хс" in notification.get("title").lower():
                    enterprise["request_href"] = notification.get("href")
                    enterprise["request_count"] = notification.get_text(strip=True)
                notification.decompose()
            enterprise["number"] = label.find("input").get("value")
            enterprise["name"] = label.get_text(strip=True)
            collection.append(
                EnterpriseMainPageSchema(**enterprise)
            )
        return collection

    @staticmethod
    def filter_enterprises_with_request(enterprises: list[EnterpriseMainPageSchema]) -> list[EnterpriseMainPageSchema]:
        return list(filter(lambda x: x.request_count is not None, enterprises))

    @staticmethod
    def filter_enterprises_by_patterns(
            enterprises: list[EnterpriseMainPageSchema],
            patterns: list
    ) -> list[EnterpriseMainPageSchema]:
        return [enterprise for enterprise in enterprises if any(pattern in enterprise.name for pattern in patterns)]

    async def select_enterprise(self, enterprise_pk: str) -> None:
        await self.fetch(
            url=self.request_url,
            data={
                "_action": "chooseServicedEnterprise",
                "enterprisePk": enterprise_pk
            }
        )

    async def get_request_transactions_numbers(self) -> list[int]:
        response = await self.fetch(
            url=self.request_url,
            data={
                "_action": "listTransactionAjax",
                "formed": "false",
                "status": "4",
                "pageList": "1",
                "all": "true",
                "request": "true",
                "template": "false",
            }
        )
        soup = BSoup(await response.text(), "lxml").find("listcontent")
        return [
            transaction.find("td").find("b").get_text()
            for transaction in soup.find_all("tr", {"class": ["first", "second"]})
        ]

    async def get_transaction_data(self, transaction_number: int):
        response = await self.fetch(
            url=self.request_url,
            data={
                "_action": "showTransactionForm",
                "transactionPk": transaction_number,
            }
        )
        request_page = BSoup(await response.text(), "html5lib")
        edited_data_table = request_page.find_all(
            name="table",
            attrs={"class": "innerForm"}
        )[2]
        recipients_table = request_page.find_all(
            name="table",
            attrs={"class": "innerFormWide"}
        )[1]
        return {
            **(self._parse_edited_data_table(edited_data_table)),
            "recipients": await self._parse_recipients_table(recipients_table),
            "version": self._parse_request_version(request_page),
            "tuid": self._parse_request_tuid(request_page),
        }

    @staticmethod
    def _parse_request_tuid(request_page: BSoup) -> str:
        return request_page.find("input", {"name": "tuid"}).get("value")

    @staticmethod
    def _parse_request_version(request_page: BSoup) -> str:
        return request_page.find("input", {"id": "transaction-version"}).get("value")

    @staticmethod
    def _parse_edited_data_table(table: BSoup) -> dict:
        return {
            "transaction_type": table.find_all("tr")[-1].find("td", {"class": "value"}).get_text(strip=True),
            "auto_number": table.find_all("tr")[-2].find("td", {"class": "value"}).get_text(strip=True).replace(" ", "")
        }

    async def _parse_recipients_table(self, table: BSoup) -> list:
        return [
            {
                "recipient_enterprise": recipient.find_all("td")[0].find("a").get_text(strip=True),
                "recipient_company": recipient.find_all("td")[1].find("a").get_text(strip=True),
                "bill_of_lading": recipient.find_all("td")[2].get_text(strip=True),
                "bill_of_lading_date": recipient.find_all("td")[3].get_text(strip=True),
                "products": [
                    await self._parse_request_document(product.get('href').split('&')[1].split('=')[-1])
                    for product in recipient.find_next("tr").find_all("a", {"title": "просмотр сведений"})
                ]
            } for recipient in table.find_all("tr", {"style": True})
        ]

    async def _parse_request_document(self, request_document_number: int):
        def get_text_by_title(bs_doc: BSoup, title: str | Pattern) -> str:
            if title_tag := bs_doc.find('td', string=title):
                return title_tag.find_next().get_text(strip=True)
            return ''

        response = await self.fetch(
            url=self.request_url,
            data={
                '_action': 'showVetDocumentAjaxForm',
                'vetDocument': request_document_number
            }
        )
        doc_params = BSoup(await response.text(), "html5lib").find_all("table", {"class": "innerFormWide"})[1]
        parsed_doc = {}
        parsed_doc.update({"product_name": get_text_by_title(bs_doc=doc_params, title='Название продукции:')})
        parsed_doc.update({"volume": get_text_by_title(bs_doc=doc_params, title='Объём:').split(" ")[0]})
        parsed_doc.update({"unit": get_text_by_title(bs_doc=doc_params, title='Объём:').split(" ")[1]})
        parsed_doc.update({
            "date_from": get_text_by_title(bs_doc=doc_params, title=re.compile(r"Дата выработки продукции:"))
        })
        parsed_doc.update({"date_to": get_text_by_title(bs_doc=doc_params, title='Годен до:')})
        parsed_doc.update({"purpose": get_text_by_title(bs_doc=doc_params, title='Цель:')})
        parsed_doc.update({
            "vet_examination": get_text_by_title(bs_doc=doc_params, title='Ветеринарно-санитарная экспертиза:')})
        parsed_doc.update({"text": get_text_by_title(bs_doc=doc_params, title='Особые отметки:')})
        return parsed_doc

    async def accept_request(self, request: MilkRequestSchema) -> MilkTransactionAfterRequestSchema:
        response = await self.fetch(
            url=self.request_url,
            data={'_action': 'transactionAcceptForm',
                  'transactionPk': request.number,
                  'version': request.version,
                  'skipCheck': 'true',
                  }
        )
        request.accepted = True
        accepted_request_page = BSoup(await response.text(), "html5lib")
        return MilkTransactionAfterRequestSchema(
            number=accepted_request_page.find("input", {"name": "transactionPk"}).get("value"),
            version=accepted_request_page.find("input", {"id": "transaction-version"}).get("value"),
            tuid=accepted_request_page.find("input", {"name": "tuid"}).get("value"),
            waybill_id=accepted_request_page.find("input", {"name": "waybillId"}).get("value"),
        )

    async def confirm_transaction(self, transaction: MilkTransactionAfterRequestSchema) -> bool:
        response = await self.fetch(
            url=self.request_url,
            data={
                # 'waybillId': transaction.waybill_id,
                '_action': 'formTransaction',
                'transactionPk': transaction.number,
                'request': 'false',
                'version': transaction.version,
                'skipCheck': 'true',
                # 'tuid': transaction.tuid
            }
        )
        return BSoup(await response.text(), "html5lib").find("div", {"class": "successMessage"}).get_text(
            strip=True) == "Транзакция успешно оформлена"
