"""Module for Legrand Cable Outlet with pilot wire functionality."""

from zigpy.quirks import CustomCluster
from zigpy.quirks.v2 import EntityType, QuirkBuilder
import zigpy.types as t
from zigpy.zcl.foundation import (
    BaseAttributeDefs,
    BaseCommandDefs,
    ZCLAttributeDef,
    ZCLCommandDef,
)

from zhaquirks.legrand import LEGRAND, MANUFACTURER_SPECIFIC_CLUSTER_ID

DEVICE_MODE_WIRE_PILOT_ON = [0x02, 0x00]
DEVICE_MODE_WIRE_PILOT_OFF = [0x01, 0x00]


class DeviceMode(t.enum8):
    """Device mode."""

    Switch = 0x00
    Wire_pilot = 0x01


class LegrandCluster(CustomCluster):
    """LegrandCluster."""

    cluster_id = MANUFACTURER_SPECIFIC_CLUSTER_ID
    name = "Legrand"
    ep_attribute = "legrand_cluster"

    class AttributeDefs(BaseAttributeDefs):
        """Attribute definitions for LegrandCluster."""

        device_mode = ZCLAttributeDef(
            id=0x0000,
            type=t.data16,
            is_manufacturer_specific=True,
        )
        led_dark = ZCLAttributeDef(
            id=0x0001,
            type=t.Bool,
            is_manufacturer_specific=True,
        )
        led_on = ZCLAttributeDef(
            id=0x0002,
            type=t.Bool,
            is_manufacturer_specific=True,
        )
        device_mode_enum = ZCLAttributeDef(
            id=0x4000,
            type=t.enum8,
            is_manufacturer_specific=True,
        )

    async def write_attributes(self, attributes, manufacturer=None):
        """Write attributes to the cluster."""

        attrs = {}
        for attr, value in attributes.items():
            attr_def = self.find_attribute(attr)
            if attr_def == LegrandCluster.AttributeDefs.device_mode_enum:
                mode = (
                    DEVICE_MODE_WIRE_PILOT_ON
                    if value == DeviceMode.Wire_pilot
                    else DEVICE_MODE_WIRE_PILOT_OFF
                )
                attrs[LegrandCluster.AttributeDefs.device_mode.id] = mode
            else:
                attrs[attr] = value
        return await super().write_attributes(attrs, manufacturer)

    def _update_attribute(self, attrid, value) -> None:
        super()._update_attribute(attrid, value)
        if attrid == LegrandCluster.AttributeDefs.device_mode.id:
            mode = (
                DeviceMode.Wire_pilot
                if value == DEVICE_MODE_WIRE_PILOT_ON
                else DeviceMode.Switch
            )
            super()._update_attribute(
                LegrandCluster.AttributeDefs.device_mode_enum.id, mode
            )


class WirePilotMode(t.enum8):
    """Wire pilot mode."""

    Comfort = 0x00
    Comfort_minus_1 = 0x01
    Comfort_minus_2 = 0x02
    Eco = 0x03
    Frost_protection = 0x04
    Off = 0x05


class LegrandWirePilotCluster(CustomCluster):
    """Legrand wire pilot manufacturer-specific cluster."""

    cluster_id = 0xFC40
    name = "Legrand Wire Pilot"
    ep_attribute = "legrand_wire_pilot"

    class AttributeDefs(BaseAttributeDefs):
        """Attribute definitions for LegrandWirePilotCluster."""

        wire_pilot_mode = ZCLAttributeDef(
            id=0x00,
            type=WirePilotMode,
            is_manufacturer_specific=True,
        )

    class ServerCommandDefs(BaseCommandDefs):
        """Server command definitions."""

        set_wire_pilot_mode = ZCLCommandDef(
            id=0x00,
            schema={"mode": WirePilotMode},
            is_manufacturer_specific=True,
        )

    async def write_attributes(self, attributes, manufacturer=None):
        """Write attributes to the cluster."""

        attrs = {}
        for attr, value in attributes.items():
            attr_def = self.find_attribute(attr)
            if attr_def == LegrandWirePilotCluster.AttributeDefs.wire_pilot_mode:
                await self.set_wire_pilot_mode(value, manufacturer=manufacturer)
                await super().read_attributes([attr], manufacturer=manufacturer)
            else:
                attrs[attr] = value
        return await super().write_attributes(attrs, manufacturer)


class LegrandPowerCluster(CustomCluster):
    """Legrand wire pilot manufacturer-specific cluster."""

    cluster_id = 0xFC40
    name = "Legrand Wire Pilot"
    ep_attribute = "legrand_wire_pilot"

    class AttributeDefs(BaseAttributeDefs):
        """Attribute definitions for LegrandWirePilotCluster."""

        wire_pilot_mode = ZCLAttributeDef(
            id=0x00,
            type=WirePilotMode,
            is_manufacturer_specific=True,
        )

    class ServerCommandDefs(BaseCommandDefs):
        """Server command definitions."""

        set_wire_pilot_mode = ZCLCommandDef(
            id=0x00,
            schema={"mode": WirePilotMode},
            is_manufacturer_specific=True,
        )

    async def write_attributes(self, attributes, manufacturer=None):
        """Write attributes to the cluster."""

        attrs = {}
        for attr, value in attributes.items():
            attr_def = self.find_attribute(attr)
            if attr_def == LegrandWirePilotCluster.AttributeDefs.wire_pilot_mode:
                await self.set_wire_pilot_mode(value, manufacturer=manufacturer)
                await super().read_attributes([attr], manufacturer=manufacturer)
            else:
                attrs[attr] = value
        return await super().write_attributes(attrs, manufacturer)


(
    QuirkBuilder(f" {LEGRAND}", " Cable outlet")
    .replaces(LegrandCluster)
    .replaces(LegrandWirePilotCluster)
    .enum(
        attribute_name=LegrandCluster.AttributeDefs.device_mode_enum.name,
        cluster_id=LegrandCluster.cluster_id,
        enum_class=DeviceMode,
        translation_key="device_mode",
        fallback_name="Device mode",
    )
    .enum(
        attribute_name=LegrandWirePilotCluster.AttributeDefs.wire_pilot_mode.name,
        cluster_id=LegrandWirePilotCluster.cluster_id,
        enum_class=WirePilotMode,
        translation_key="wire_pilot_mode",
        fallback_name="Wire pilot mode",
        entity_type=EntityType.STANDARD,
    )
    .add_to_registry()
)
