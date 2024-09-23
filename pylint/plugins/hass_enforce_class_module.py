"""Plugin for checking if class is in correct module."""

from __future__ import annotations

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter

from homeassistant.const import Platform

_BASE_MODULES: dict[str, set[str]] = {
    "entity": {
        "BaseCoordinatorEntity",
        "CoordinatorEntity",
        "Entity",
        "EntityDescription",
        "ManualTriggerEntity",
        "RestoreEntity",
        "ToggleEntity",
        "ToggleEntityDescription",
        "TriggerBaseEntity",
    },
}
_MODULES: dict[str, set[str]] = {
    "air_quality": {"AirQualityEntity"},
    "alarm_control_panel": {
        "AlarmControlPanelEntity",
        "AlarmControlPanelEntityDescription",
    },
    "assist_satellite": {"AssistSatelliteEntity", "AssistSatelliteEntityDescription"},
    "binary_sensor": {"BinarySensorEntity", "BinarySensorEntityDescription"},
    "button": {"ButtonEntity", "ButtonEntityDescription"},
    "calendar": {"CalendarEntity"},
    "camera": {"CameraEntity", "CameraEntityDescription"},
    "climate": {"ClimateEntity", "ClimateEntityDescription"},
    "coordinator": {"DataUpdateCoordinator"},
    "conversation": {"ConversationEntity"},
    "cover": {"CoverEntity", "CoverEntityDescription"},
    "date": {"DateEntity", "DateEntityDescription"},
    "datetime": {"DateTimeEntity", "DateTimeEntityDescription"},
    "device_tracker": {"DeviceTrackerEntity"},
    "event": {"EventEntity", "EventEntityDescription"},
    "fan": {"FanEntity", "FanEntityDescription"},
    "geo_location": {"GeolocationEvent"},
    "humidifier": {"HumidifierEntity", "HumidifierEntityDescription"},
    "image": {"ImageEntity", "ImageEntityDescription"},
    "image_processing": {
        "ImageProcessingEntity",
        "ImageProcessingFaceEntity",
        "ImageProcessingEntityDescription",
    },
    "lawn_mower": {"LawnMowerEntity", "LawnMowerEntityDescription"},
    "light": {"LightEntity", "LightEntityDescription"},
    "lock": {"LockEntity", "LockEntityDescription"},
    "media_player": {"MediaPlayerEntity", "MediaPlayerEntityDescription"},
    "notify": {"NotifyEntity", "NotifyEntityDescription"},
    "number": {"NumberEntity", "NumberEntityDescription", "RestoreNumber"},
    "remote": {"RemoteEntity", "RemoteEntityDescription"},
    "select": {"SelectEntity", "SelectEntityDescription"},
    "sensor": {"RestoreSensor", "SensorEntity", "SensorEntityDescription"},
    "siren": {"SirenEntity", "SirenEntityDescription"},
    "stt": {"SpeechToTextEntity"},
    "switch": {"SwitchEntity", "SwitchEntityDescription"},
    "text": {"TextEntity", "TextEntityDescription"},
    "time": {"TimeEntity", "TimeEntityDescription"},
    "todo": {"TodoListEntity"},
    "tts": {"TextToSpeechEntity"},
    "update": {"UpdateEntityDescription"},
    "vacuum": {"VacuumEntity", "VacuumEntityDescription"},
    "wake_word": {"WakeWordDetectionEntity"},
    "water_heater": {"WaterHeaterEntity"},
    "weather": {
        "CoordinatorWeatherEntity",
        "SingleCoordinatorWeatherEntity",
        "WeatherEntity",
        "WeatherEntityDescription",
    },
}
_ENTITY_COMPONENTS: set[str] = {platform.value for platform in Platform}
_ENTITY_COMPONENTS.add("tag")


_MODULE_CLASSES = {
    class_name for classes in _MODULES.values() for class_name in classes
}


class HassEnforceClassModule(BaseChecker):
    """Checker for class in correct module."""

    name = "hass_enforce_class_module"
    priority = -1
    msgs = {
        "C7461": (
            "Derived %s is recommended to be placed in the '%s' module",
            "hass-enforce-class-module",
            "Used when derived class should be placed in its own module.",
        ),
    }

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        """Check if derived class is placed in its own module."""
        root_name = node.root().name

        # we only want to check components
        if not root_name.startswith("homeassistant.components."):
            return
        parts = root_name.split(".")
        current_integration = parts[2]
        current_module = parts[3] if len(parts) > 3 else ""

        ancestors = list(node.ancestors())

        for expected_module, classes in _MODULES.items():
            if expected_module in (current_module, current_integration):
                continue

            for ancestor in ancestors:
                if ancestor.name in classes:
                    self.add_message(
                        "hass-enforce-class-module",
                        node=node,
                        args=(ancestor.name, expected_module),
                    )
                    return

        for expected_module, classes in _BASE_MODULES.items():
            if (
                expected_module == current_module
                or expected_module == "entity"
                and current_integration in _ENTITY_COMPONENTS
            ):
                continue

            top_level_ancestors = list(node.ancestors(recurs=False))

            for ancestor in top_level_ancestors:
                if ancestor.name in classes and not any(
                    anc.name in _MODULE_CLASSES for anc in ancestors
                ):
                    self.add_message(
                        "hass-enforce-class-module",
                        node=node,
                        args=(ancestor.name, "entity"),
                    )
                    return


def register(linter: PyLinter) -> None:
    """Register the checker."""
    linter.register_checker(HassEnforceClassModule(linter))
