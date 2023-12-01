from app.schemas.milk_service import MilkConfigSchema
from app.settings import checked_invalid_requests, settings
from app.vetis.schemas.base import EnterpriseMainPageSchema
from app.vetis.schemas.milk import MilkRequestSchema, ValueWithIsValid


def get_config_answer(config: MilkConfigSchema) -> str:
    answer = (
        f"<b>Сервис обработки входящих заявок на сырое молоко</b>\n"
        f"<b>Текущая конфигурация:</b>\n"
        f"Периодичность проверки: <b>{config.schedule_every_minute} минут(-а)</b>\n"
        f"Проверяемые площадки: <b>{', '.join(config.enterprise_patterns)}</b>\n"
        f"Допустимые названия продуктов: <b>{', '.join(config.verified_products)}</b>\n"
        f"Допустимые типы транзакций: <b>{', '.join(config.verified_transaction_types)}</b>\n"
        f"Допустимые статусы ВСЭ: <b>{', '.join(config.verified_vet_examinations)}</b>\n"
        f"Проверять формат номера транспорта: <b>{'Да' if config.check_transport_number_format else 'Нет'}</b>\n"
        f"Интервал проверки: <b>{str(config.start_hour).rjust(2, '0')}:{str(config.start_minute).rjust(2, '0')}"
        f" - {str(config.end_hour).rjust(2, '0')}:{str(config.end_minute).rjust(2, '0')}</b>\n"
    )
    return answer


def get_observer_answer(enterprise: EnterpriseMainPageSchema, requests: list[MilkRequestSchema]) -> list[str]:
    def is_valid_symbol(field: ValueWithIsValid) -> str:
        return '🍚' if field.is_valid else '❌'

    counter = 0
    answer = [[f"{enterprise.name} \n<b>- количество активных заявок: {len(requests)}</b>;\n"]]
    for request in requests:
        if request.number in checked_invalid_requests:
            continue
        text = [
            f"\n<b>Заявка {requests.index(request) + 1}:</b>\n",
            f"Принято: <b>{request.accepted}</b> -> Оформлено: <b>{request.confirmed}</b>\n"
            f"{is_valid_symbol(request.transaction_type)} <b>Способ хранения при перевозке:</b> {request.transaction_type.value.value};\n",
            f"{is_valid_symbol(request.auto_number)} <b>Номер авто:</b> {request.auto_number.value};\n",
        ]
        if sum(map(lambda x: len(x), answer[counter])) + sum(map(lambda x: len(x), text)) >= settings.MESSAGE_MAX_LENGTH:
            counter += 1
            answer.append([])
        answer[counter].extend(text)
        for recipient in request.recipients:
            text = [
                f"\n<b>Получатель:</b> {request.recipients.index(recipient) + 1}/{len(request.recipients)} {recipient.recipient_company}\n",
                f"<b>Площадка:</b> {recipient.recipient_enterprise}\n",
                f"{is_valid_symbol(recipient.bill_of_lading_date)} <b>ТТН:</b> {recipient.bill_of_lading} от {recipient.bill_of_lading_date.value.strftime('%d.%m.%Y')}\n",
            ]
            if sum(map(lambda x: len(x), answer[counter])) + sum(map(lambda x: len(x), text)) >= settings.MESSAGE_MAX_LENGTH:
                counter += 1
                answer.append([])
            answer[counter].extend(text)
            for product in recipient.products:
                text = [
                    f"\n{is_valid_symbol(product.product_name)} <b>Продукт:</b> {product.product_name.value} - {product.volume} {product.unit}\n",
                    f"{is_valid_symbol(product.expiration)} <b>Срок годности:</b> {product.expiration.value} ({None if product.date_from is None else product.date_from.value.strftime('%d.%m.%Y:%H')} - {None if product.date_to is None else product.date_to.strftime('%d.%m.%Y:%H')})\n",
                    f"{is_valid_symbol(product.purpose)} <b>Цель:</b> {product.purpose.value}\n",
                    f"{is_valid_symbol(product.vet_examination)} <b>ВСЭ:</b> {product.vet_examination.value.value}\n",
                ]
                if sum(map(lambda x: len(x), answer[counter])) + sum(map(lambda x: len(x), text)) >= settings.MESSAGE_MAX_LENGTH:
                    counter += 1
                    answer.append([])
                answer[counter].extend(text)
        if not request.is_valid():
            checked_invalid_requests.add(request.number)
    for msg_index in range(len(answer)):
        answer[msg_index] = ''.join(answer[msg_index])
    return answer
