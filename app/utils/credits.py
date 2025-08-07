# from datetime import datetime, timezone
# from functools import wraps

# from fastapi import HTTPException
# from sqlalchemy.orm import Session

# # from app.features.auth.service import get_superadmin_user
# from app.models import UsageHistory, User, Wallet


# def check_credits(minimum_credits: int):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             db: Session
#             current_user: User

#             db, current_user = args
#             if not current_user:
#                 raise HTTPException(status_code=401, detail="Unauthorized")

#             superadmin_user = get_superadmin_user(current_user)

#             wallet = (
#                 db.query(Wallet).filter(Wallet.user_id == superadmin_user.id).first()
#             )
#             if not wallet:
#                 raise HTTPException(status_code=403, detail="No wallet found for user.")
#             total_credits = sum(credit.amount for credit in wallet.credits)
#             if total_credits < minimum_credits:
#                 raise HTTPException(
#                     status_code=403,
#                     detail=f"Insufficient credits. Minimum required: {minimum_credits}, Available: {total_credits}",
#                 )

#             return func(*args, **kwargs)

#         return wrapper

#     return decorator


# def consume_credits(db: Session, user: User, amount: int, feature: str):
#     """
#     To Use this function ensure that the parent function is decorated with @check_credits(minimum_credits=amount)
#     """
#     superadmin_user = get_superadmin_user(user)
#     wallet = db.query(Wallet).filter(Wallet.user_id == superadmin_user.id).first()
#     if not wallet:
#         raise HTTPException(status_code=403, detail="No wallet found for user.")

#     now = datetime.now(timezone.utc)
#     wallet = db.query(Wallet).filter(Wallet.user_id == superadmin_user.id).first()
#     if not wallet:
#         raise HTTPException(status_code=403, detail="No wallet found for user.")
#     credits = wallet.credits
#     valid_subscription_credits = [
#         credit
#         for credit in credits
#         if credit.credit_type == "subscription"
#         and (not credit.expiry_date or credit.expiry_date >= now)
#         and credit.amount > 0
#     ]

#     valid_purchased_credits = [
#         credit
#         for credit in credits
#         if credit.credit_type == "purchased"
#         and (not credit.expiry_date or credit.expiry_date >= now)
#         and credit.amount > 0
#     ]

#     remaining = amount
#     credit_type = None

#     # Deduct from subscription credits first
#     for credit in valid_subscription_credits:
#         if remaining <= 0:
#             break
#         deduct = min(credit.amount, remaining)
#         credit.amount -= deduct
#         remaining -= deduct
#         credit_type = "subscription"

#     # Then deduct from purchased credits
#     for credit in valid_purchased_credits:
#         if remaining <= 0:
#             break
#         deduct = min(credit.amount, remaining)
#         credit.amount -= deduct
#         remaining -= deduct
#         credit_type = "purchased"

#     if remaining > 0:
#         raise HTTPException(
#             status_code=403,
#             detail=f"Insufficient valid credits. Required: {amount}, Available: {amount - remaining}",
#         )

#     # Log the usage
#     usage_history = UsageHistory(
#         user_id=user.id,
#         feature=feature,
#         credit_type=credit_type,
#         credits_consumed=amount,
#         description=f"Consumed {amount} credits",
#     )
#     db.add(usage_history)

#     db.commit()
#     return True
