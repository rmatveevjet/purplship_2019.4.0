"""PurplShip Gateway modules."""

import attr
from enum import Enum
from typing import Callable, Union
from purplship.domain import Proxy, Client
from purplship.mappers.aups import AustraliaPostProxy, AustraliaPostClient
from purplship.mappers.caps import CanadaPostProxy, CanadaPostClient
from purplship.mappers.dhl import DHLProxy, DHLClient
from purplship.mappers.fedex import FedexProxy, FedexClient
from purplship.mappers.ups import UPSProxy, UPSClient
from purplship.mappers.usps import USPSProxy, USPSClient
from purplship.mappers.sendle import SendleProxy, SendleClient


class Providers(Enum):
    aups = (AustraliaPostProxy, AustraliaPostClient)
    caps = (CanadaPostProxy, CanadaPostClient)
    dhl = (DHLProxy, DHLClient)
    fedex = (FedexProxy, FedexClient)
    sendle = (SendleProxy, SendleClient)
    ups = (UPSProxy, UPSClient)
    usps = (USPSProxy, USPSClient)


@attr.s(auto_attribs=True)
class Builder:
    initializer: Callable[[dict], Proxy]

    def create(self, settings: dict) -> Proxy:
        return self.initializer(settings)


class Gateway:
    def __getitem__(self, key):
        def initializer(settings: Union[Client, dict]) -> Proxy:
            try:
                _Proxy, _Client = Providers[key].value
                return _Proxy(
                    client=_Client(**settings) if isinstance(settings, dict) else settings
                )
            except KeyError as e:
                raise Exception(f"Unknown provider id '{key}'") from e

        return Builder(initializer)


gateway = Gateway()
