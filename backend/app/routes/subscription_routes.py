from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.services import SubscriptionService
from app.schemas import (
    subscription_schema,
    subscriptions_schema,
    subscription_request_schema,
)
import logging

subscription_bp = Blueprint("subscription", __name__)


@subscription_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    subscriptions = SubscriptionService.get_all_subscriptions()
    return jsonify(subscriptions_schema.dump(subscriptions)), 200


@subscription_bp.route("/subscribe", methods=["POST"])
def create_subscription():
    try:
        data = subscription_request_schema.load(request.json)

        if data.get("product_id"):
            subscription, error = SubscriptionService.create_subscription(
                data["email"], data["product_id"]
            )
        else:
            subscription, error = (
                SubscriptionService.create_subsciption_by_product_name(
                    data["email"], data["product_name"]
                )
            )

        if error:
            return jsonify({"message": error}), 400

        # Return only necessary information to the user
        result = {
            "message": "Subscription created successfully",
            "invite_link": subscription.invite_link_url,
            "invite_expires_at": subscription.invite_link_expires_at,
            "subscription_expires_at": subscription.subscription_expires_at,
        }

        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"message": "Validation error", "errors": e.messages}), 400
    except Exception as e:
        logging.exception("Error creating subscription")
        return jsonify({"message": str(e)}), 500
