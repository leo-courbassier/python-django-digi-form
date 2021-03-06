from django.db import IntegrityError
from django.db import models
from django.utils import timezone


class CouponManager(models.Manager):
    def create_coupon(self, type, value, user=None, valid_until=None, prefix="", campaign=None):
        from billing.models import Coupon
        coupon = self.create(
            value=value,
            code=Coupon.generate_code(prefix),
            type=type,
            user=user,
            valid_until=valid_until,
            campaign=campaign,
        )
        try:
            coupon.save()
        except IntegrityError:
            # Try again with other code
            return Coupon.objects.create_coupon(type, value, user, valid_until, prefix, campaign)
        else:
            return coupon

    def expired(self):
        return self.filter(valid_until__lt=timezone.now())


class PlanPricingManager(models.Manager):
    def get_query_set(self):
        return super(PlanPricingManager, self).get_query_set().select_related('plan', 'pricing')


class PlanSubscriptionQueryset(models.QuerySet):

    def is_active(self):
        """
        Return the active Plan subscription
        """
        return self.filter(active=True)

    def has_active_subscription(self):
        return any(self.is_active().values_list('active', flat=True))
