from typing import Any, Dict

from app.services.email.base import BaseEmail


class PaymentSuccessEmail(BaseEmail):
    @property
    def template_name(self) -> str:
        return "emails/payment_success.html"

    @property
    def subject(self) -> str:
        return "Payment Successful"

    def get_context(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context(**kwargs)
        required_fields = [
            "first_name",
            "credits",
            "amount",
            "currency",
            "transaction_id",
            "payment_date",
        ]
        for field in required_fields:
            if field not in kwargs:
                raise ValueError(
                    f"Missing required field for PaymentSuccessEmail: {field}"
                )
        return context
