"""Interface."""

import attr
from typing import Callable, TypeVar, Union
from purplship.domain.proxy import Proxy
from purplship.domain.mapper import Mapper
from purplship.domain.Types.models import (
    RateRequest,
    ShipmentRequest,
    TrackingRequest,
    PickupRequest,
    PickupCancellationRequest
)

T = TypeVar('T')
S = TypeVar('S')


@attr.s(auto_attribs=True)
class IDeserialize:
    deserialize: Callable[[], S]

    def parse(self):
        return self.deserialize()


@attr.s(auto_attribs=True)
class IRequestFrom:
    action: Callable[[Proxy], IDeserialize]

    def from_(self, proxy: Proxy) -> IDeserialize:
        return self.action(proxy)


@attr.s(auto_attribs=True)
class IRequestWith:
    action: Callable[[Proxy], IDeserialize]

    def with_(self, proxy: Proxy) -> IDeserialize:
        return self.action(proxy)


class pickup:

    @staticmethod
    def book(args: Union[PickupRequest, dict]):

        def action(proxy: Proxy):
            payload = (
                args if isinstance(args, PickupRequest)
                else PickupRequest(**args)
            )
            mapper: Mapper = proxy.mapper
            request = mapper.create_pickup_request(payload)
            response = proxy.request_pickup(request)

            def deserialize():
                return mapper.parse_pickup_response(response)

            return IDeserialize(deserialize)

        return IRequestWith(action)

    @staticmethod
    def cancel(args: Union[PickupCancellationRequest, dict]):

        def action(proxy: Proxy):
            payload = (
                args if isinstance(args, PickupCancellationRequest)
                else PickupCancellationRequest(**args)
            )
            mapper: Mapper = proxy.mapper
            request = mapper.create_pickup_cancellation_request(payload)
            response = proxy.cancel_pickup(request)

            def deserialize():
                return response

            return IDeserialize(deserialize)

        return IRequestFrom(action)

    @staticmethod
    def update(args: Union[PickupRequest, dict]):

        def action(proxy: Proxy):
            payload = (
                args if isinstance(args, PickupRequest)
                else PickupRequest(**args)
            )
            mapper: Mapper = proxy.mapper
            request = mapper.create_pickup_request(payload)
            response = proxy.modify_pickup(request)

            def deserialize():
                return mapper.parse_pickup_response(response)

            return IDeserialize(deserialize)

        return IRequestFrom(action)


class rating:

    @staticmethod
    def fetch(args: Union[RateRequest, dict]):

        def action(proxy: Proxy):
            payload = (
                args if isinstance(args, RateRequest)
                else RateRequest(**args)
            )
            mapper: Mapper = proxy.mapper
            request = mapper.create_quote_request(payload)
            response = proxy.get_quotes(request)

            def deserialize():
                return mapper.parse_quote_response(response)

            return IDeserialize(deserialize)

        return IRequestFrom(action)


class shipment:

    @staticmethod
    def create(args: Union[ShipmentRequest, dict]):

        def action(proxy: Proxy):
            payload = (
                args if isinstance(args, ShipmentRequest)
                else ShipmentRequest(**args)
            )
            mapper: Mapper = proxy.mapper
            request = mapper.create_shipment_request(payload)
            response = proxy.create_shipment(request)

            def deserialize():
                return mapper.parse_shipment_response(response)

            return IDeserialize(deserialize)

        return IRequestWith(action)


class tracking:

    @staticmethod
    def fetch(args: Union[TrackingRequest, dict]) -> IRequestFrom:

        def action(proxy: Proxy) -> IDeserialize:
            payload = (
                args if isinstance(args, TrackingRequest)
                else TrackingRequest(**args)
            )
            mapper: Mapper = proxy.mapper
            request = mapper.create_tracking_request(payload)
            response = proxy.get_tracking(request)

            def deserialize():
                return mapper.parse_tracking_response(response)

            return IDeserialize(deserialize)

        return IRequestFrom(action)
