"""PurplShip Australia post rate mapper module."""

from functools import reduce
from typing import List, Tuple
from .interface import AustraliaPostMapperBase
from purplship.domain.Types import (
    Error,
    ChargeDetails,
    ShipmentRequest,
    QuoteDetails
)
from purplship.domain.Types.errors import OriginNotServicedError
from pyaups.shipping_price_response import (
    ShippingPriceResponse,
    Shipment as ResponseShipment,
    ShipmentSummary
)
from pyaups.shipping_price_request import (
    ShippingPriceRequest,
    Shipment,
    From,
    To,
    Item
)


class AustraliaPostMapperPartial(AustraliaPostMapperBase):
    def parse_shipping_price_response(
        self, response: dict
    ) -> Tuple[List[QuoteDetails], List[Error]]:
        price_response: ShippingPriceResponse = ShippingPriceResponse(**response)
        return (
            reduce(self._extract_quote, price_response.shipments, []),
            self.parse_error_response({
                "errors": response.get('errors', [])
            })
        )

    def _extract_quote(
        self, quotes: List[QuoteDetails], shipping_price: ResponseShipment
    ) -> List[QuoteDetails]:
        summary = shipping_price.shipment_summary or ShipmentSummary()
        return quotes + [
            QuoteDetails(
                carrier=self.client.carrier_name,
                service_name=None,
                service_type=None,
                base_charge=summary.total_cost_ex_gst,
                duties_and_taxes=summary.total_gst,
                total_charge=summary.total_cost,
                currency="AUD",
                delivery_date=None,
                discount=summary.discount,
                extra_charges=[
                    ChargeDetails(**details)
                    for details in (
                        [] if not summary.fuel_surcharge else [{"name": 'Fuel', "amount": summary.fuel_surcharge}] +
                        [] if not summary.security_surcharge else [{"name": 'Fuel', "amount": summary.security_surcharge}] +
                        [] if not summary.transit_cover else [{"name": 'Fuel', "amount": summary.transit_cover}] +
                        [] if not summary.freight_charge else [{"name": 'Fuel', "amount": summary.freight_charge}]
                    )
                ]
            )
        ]

    def create_shipping_price_request(self, payload: ShipmentRequest) -> ShippingPriceRequest:
        """Create the appropriate Australia post rate request depending on the destination

        :param payload: PurplShip unified API rate request data
        :return: a domestic or international Australia post compatible request
        :raises: an OriginNotServicedError when origin country is not serviced by the carrier
        """
        if payload.shipper.country_code and payload.shipper.country_code != 'AU':
            raise OriginNotServicedError(payload.shipper.country_code, "Australia post")

        return ShippingPriceRequest(
            shipments=[
                Shipment(
                    shipment_reference=" ".join(payload.shipment.references),
                    sender_references=None,
                    goods_descriptions=None,
                    despatch_date=payload.shipment.date,
                    consolidate=None,
                    email_tracking_enabled=payload.shipment.extra.get('email_tracking_enabled'),
                    from_=From(
                        name=payload.shipper.person_name,
                        type=None,
                        lines=payload.shipper.address_lines,
                        suburb=payload.shipper.suburb,
                        state=payload.shipper.state_code,
                        postcode=payload.shipper.postal_code,
                        country=payload.shipper.country_code,
                        phone=payload.shipper.phone_number,
                        email=payload.shipper.email_address
                    ),
                    to=To(
                        name=payload.recipient.person_name,
                        business_name=payload.recipient.company_name,
                        type=None,
                        lines=payload.recipient.address_lines,
                        suburb=payload.recipient.suburb,
                        state=payload.recipient.state_code,
                        postcode=payload.recipient.postal_code,
                        country=payload.recipient.country_code,
                        phone=payload.recipient.phone_number,
                        email=payload.recipient.email_address,
                        delivery_instructions=None
                    ),
                    dangerous_goods=None,
                    movement_type=None,
                    features=None,
                    authorisation_number=None,
                    items=[
                        Item(
                            item_reference=item.sku,
                            product_id=item.id,
                            item_description=item.description,
                            length=item.length,
                            width=item.width,
                            height=item.height,
                            cubic_volume=None,
                            weight=item.weight,
                            contains_dangerous_goods=None,
                            transportable_by_air=None,
                            dangerous_goods_declaration=None,
                            authority_to_leave=item.extra.get('authority_to_leave'),
                            reason_for_return=None,
                            allow_partial_delivery=item.extra.get('allow_partial_delivery'),
                            packaging_type=item.packaging_type,
                            atl_number=None,
                            features=None,
                            tracking_details=None,
                            commercial_value=None,
                            export_declaration_number=None,
                            import_reference_number=None,
                            classification_type=None,
                            description_of_other=None,
                            international_parcel_sender_name=None,
                            non_delivery_action=None,
                            certificate_number=None,
                            licence_number=None,
                            invoice_number=None,
                            comments=None,
                            tariff_concession=None,
                            free_trade_applicable=None
                        ) for item in payload.shipment.items
                    ]
                )
            ]
        )
