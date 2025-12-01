from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=40, unique=True, blank=True)
    code = models.CharField(max_length=2, blank=True)  # not unique as there are duplicates (IT)

    class Meta:
        verbose_name_plural = "Countries"
        ordering = ("name",)

    def __str__(self):
        return "%s" % (self.name or self.code)


class State(models.Model):
    name = models.CharField(max_length=165, blank=True)
    code = models.CharField(max_length=8, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states")

    class Meta:
        unique_together = ("name", "country")
        ordering = ("country", "name")

    def __str__(self):
        return f"{self.name or self.code}"


class Address(models.Model):
    address_one = models.CharField(max_length=100)
    address_two = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="addresses")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="addresses")

    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ("state", "country", "postal_code", "address_one")

    def __str__(self):
        return (
            f"{self.address_one}, {self.address_two + ', ' if self.address_two else ''} "
            + f"{self.postal_code}, {self.state.__str__()}, {self.country.__str__()}"
        )


class AddressField(models.ForeignKey):
    description = "An address"

    def __init__(self, *args, **kwargs):
        kwargs["to"] = "address.Address"
        # The address should be set to null when deleted if the relationship could be null
        default_on_delete = models.SET_NULL if kwargs.get("null", False) else models.CASCADE
        kwargs["on_delete"] = kwargs.get("on_delete", default_on_delete)
        super(AddressField, self).__init__(*args, **kwargs)
