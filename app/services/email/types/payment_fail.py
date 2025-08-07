from typing import Any, Dict

from app.services.email.base import BaseEmail


class PaymentFailEmail(BaseEmail):
    @property
    def template_name(self) -> str:
        return "emails/payment_fail.html"

    @property
    def subject(self) -> str:
        return "Payment Failed"

    def get_context(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context(**kwargs)
        required_fields = [
            "first_name",
            "amount",
            "currency",
            "update_payment_url",
            "payment_date",
        ]
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(
                    f"Missing required field for PaymentFailEmail: {field}"
                )
        return context
