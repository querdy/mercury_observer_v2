from aiogram import Router

from app.tg.milk_service.handlers import main
from app.tg.milk_service.handlers import config
from app.tg.milk_service.handlers import mercury

milk_service_router = Router()
milk_service_router.include_router(main.router)

milk_service_router.include_router(config.main.router)
milk_service_router.include_router(config.schedule_every_minute.router)
milk_service_router.include_router(config.enterprise_patterns.router)
milk_service_router.include_router(config.interval.router)
milk_service_router.include_router(config.verified_products.router)
milk_service_router.include_router(config.verified_transaction_type.router)
milk_service_router.include_router(config.check_transport_number_format.router)
milk_service_router.include_router(config.verified_vet_examinations.router)
milk_service_router.include_router(config.days_of_week.router)

milk_service_router.include_router(mercury.router)
