"""Constants for the Home Connect integration."""

import os

DOMAIN = "home_connect"

API_ENDPOINT = "https://api.home-connect.com"

if os.getenv("HOME_CONNECT_DEV"):
    API_ENDPOINT = "https://simulator.home-connect.com"

OAUTH2_AUTHORIZE = f"{API_ENDPOINT}/security/oauth/authorize"
OAUTH2_TOKEN = f"{API_ENDPOINT}/security/oauth/token"

BSH_POWER_STATE = "BSH.Common.Setting.PowerState"
BSH_POWER_ON = "BSH.Common.EnumType.PowerState.On"
BSH_POWER_OFF = "BSH.Common.EnumType.PowerState.Off"
BSH_POWER_STANDBY = "BSH.Common.EnumType.PowerState.Standby"
BSH_ACTIVE_PROGRAM = "BSH.Common.Root.ActiveProgram"
BSH_REMOTE_CONTROL_ACTIVATION_STATE = "BSH.Common.Status.RemoteControlActive"
BSH_REMOTE_START_ALLOWANCE_STATE = "BSH.Common.Status.RemoteControlStartAllowed"
BSH_CHILD_LOCK_STATE = "BSH.Common.Setting.ChildLock"
BSH_TEMPERATURE_UNIT = "BSH.Common.Setting.TemperatureUnit"

BSH_TEMPERATURE_UNIT_CELSIUS = "BSH.Common.EnumType.TemperatureUnit.Celsius"
BSH_TEMPERATURE_UNIT_FAHRENHEIT = "BSH.Common.EnumType.TemperatureUnit.Fahrenheit"

BSH_OPERATION_STATE = "BSH.Common.Status.OperationState"
BSH_OPERATION_STATE_RUN = "BSH.Common.EnumType.OperationState.Run"
BSH_OPERATION_STATE_PAUSE = "BSH.Common.EnumType.OperationState.Pause"
BSH_OPERATION_STATE_FINISHED = "BSH.Common.EnumType.OperationState.Finished"
BSH_OPERATION_STATE_DELAYED_START = "BSH.Common.EnumType.OperationState.DelayedStart"
BSH_OPERATION_STATE_READY = "BSH.Common.EnumType.OperationState.Ready"

BSH_REMAINING_PROGRAM_TIME = "BSH.Common.Option.RemainingProgramTime"
BSH_PROGRAM_PROGRESS = "BSH.Common.Option.ProgramProgress"

BSH_OPERATION_STATE_ENUM = [
    "BSH.Common.EnumType.OperationState.Inactive",
    BSH_OPERATION_STATE_READY,
    BSH_OPERATION_STATE_DELAYED_START,
    BSH_OPERATION_STATE_RUN,
    BSH_OPERATION_STATE_PAUSE,
    "BSH.Common.EnumType.OperationState.ActionRequired",
    BSH_OPERATION_STATE_FINISHED,
    "BSH.Common.EnumType.OperationState.Error",
    "BSH.Common.EnumType.OperationState.Aborting",
]

COFFEE_EVENT_BEAN_CONTAINER_EMPTY = (
    "ConsumerProducts.CoffeeMaker.Event.BeanContainerEmpty"
)
COFFEE_EVENT_WATER_TANK_EMPTY = "ConsumerProducts.CoffeeMaker.Event.WaterTankEmpty"
COFFEE_EVENT_DRIP_TRAY_FULL = "ConsumerProducts.CoffeeMaker.Event.DripTrayFull"

COOKING_LIGHTING = "Cooking.Common.Setting.Lighting"
COOKING_LIGHTING_BRIGHTNESS = "Cooking.Common.Setting.LightingBrightness"

COOKING_CURRENT_CAVITY_TEMP = "Cooking.Oven.Status.CurrentCavityTemperature"

REFRIGERATION_INTERNAL_LIGHT_POWER = "Refrigeration.Common.Setting.Light.Internal.Power"
REFRIGERATION_INTERNAL_LIGHT_BRIGHTNESS = (
    "Refrigeration.Common.Setting.Light.Internal.Brightness"
)
REFRIGERATION_EXTERNAL_LIGHT_POWER = "Refrigeration.Common.Setting.Light.External.Power"
REFRIGERATION_EXTERNAL_LIGHT_BRIGHTNESS = (
    "Refrigeration.Common.Setting.Light.External.Brightness"
)

REFRIGERATION_SUPERMODEFREEZER = "Refrigeration.FridgeFreezer.Setting.SuperModeFreezer"
REFRIGERATION_SUPERMODEREFRIGERATOR = (
    "Refrigeration.FridgeFreezer.Setting.SuperModeRefrigerator"
)
REFRIGERATION_DISPENSER = "Refrigeration.Common.Setting.Dispenser.Enabled"
REFRIGERATION_STATUS_DOOR_CHILLER = "Refrigeration.Common.Status.Door.ChillerCommon"
REFRIGERATION_STATUS_DOOR_FREEZER = "Refrigeration.Common.Status.Door.Freezer"
REFRIGERATION_STATUS_DOOR_REFRIGERATOR = "Refrigeration.Common.Status.Door.Refrigerator"

REFRIGERATION_EVENT_DOOR_ALARM_REFRIGERATOR = (
    "Refrigeration.FridgeFreezer.Event.DoorAlarmRefrigerator"
)
REFRIGERATION_EVENT_DOOR_ALARM_FREEZER = (
    "Refrigeration.FridgeFreezer.Event.DoorAlarmFreezer"
)
REFRIGERATION_EVENT_TEMP_ALARM_FREEZER = (
    "Refrigeration.FridgeFreezer.Event.TemperatureAlarmFreezer"
)

REFRIGERATION_CHILLERLEFT_SETPOINTTEMPERATURE = (
    "Refrigeration.Common.Setting.ChillerLeft.SetpointTemperature"
)
REFRIGERATION_CHILLERCOMMON_SETPOINTTEMPERATURE = (
    "Refrigeration.Common.Setting.ChillerCommon.SetpointTemperature"
)
REFRIGERATION_CHILLERRIGHT_SETPOINTTEMPERATURE = (
    "Refrigeration.Common.Setting.ChillerRight.SetpointTemperature"
)
REFRIGERATION_FRIDGEFREEZER_SETPOINTTEMPERATUREREFRIGERATOR = (
    "Refrigeration.FridgeFreezer.Setting.SetpointTemperatureRefrigerator"
)
REFRIGERATION_FRIDGEFREEZER_SETPOINTTEMPERATUREFREEZER = (
    "Refrigeration.FridgeFreezer.Setting.SetpointTemperatureFreezer"
)
REFRIGERATION_BOTTLECOOLER_SETPOINTTEMPERATURE = (
    "Refrigeration.Common.Setting.BottleCooler.SetpointTemperature"
)

REFRIGERATION_WINECOMPARTMENT_SETPOINTTEMPERATURE = (
    "Refrigeration.Common.Setting.WineCompartment.SetpointTemperature"
)

REFRIGERATION_ECO_MODE = "Refrigeration.Common.Setting.EcoMode"
REFRIGERATION_SABBATH_MODE = "Refrigeration.Common.Setting.SabbathMode "
REFRIGERATION_VACATION_MODE = "Refrigeration.Common.Setting.VacationMode"
REFRIGERATION_FRESH_MODE = "Refrigeration.Common.Setting.FreshMode"

BSH_EVENT_PRESENT_STATE_PRESENT = "BSH.Common.EnumType.EventPresentState.Present"
BSH_EVENT_PRESENT_STATE_CONFIRMED = "BSH.Common.EnumType.EventPresentState.Confirmed"
BSH_EVENT_PRESENT_STATE_OFF = "BSH.Common.EnumType.EventPresentState.Off"

BSH_EVENT_PRESENT_STATE_ENUM = (
    BSH_EVENT_PRESENT_STATE_PRESENT,
    BSH_EVENT_PRESENT_STATE_CONFIRMED,
    BSH_EVENT_PRESENT_STATE_OFF,
)

BSH_AMBIENT_LIGHT_ENABLED = "BSH.Common.Setting.AmbientLightEnabled"
BSH_AMBIENT_LIGHT_BRIGHTNESS = "BSH.Common.Setting.AmbientLightBrightness"
BSH_AMBIENT_LIGHT_COLOR = "BSH.Common.Setting.AmbientLightColor"
BSH_AMBIENT_LIGHT_COLOR_CUSTOM_COLOR = (
    "BSH.Common.EnumType.AmbientLightColor.CustomColor"
)
BSH_AMBIENT_LIGHT_CUSTOM_COLOR = "BSH.Common.Setting.AmbientLightCustomColor"

BSH_DOOR_STATE = "BSH.Common.Status.DoorState"
BSH_DOOR_STATE_CLOSED = "BSH.Common.EnumType.DoorState.Closed"
BSH_DOOR_STATE_LOCKED = "BSH.Common.EnumType.DoorState.Locked"
BSH_DOOR_STATE_OPEN = "BSH.Common.EnumType.DoorState.Open"

BSH_DOOR_STATE_ENUM = {
    BSH_DOOR_STATE_CLOSED,
    "BSH.Common.EnumType.DoorState.Locked",
    "BSH.Common.EnumType.DoorState.Open",
    "BSH.Common.EnumType.DoorState.Ajar",
}


BSH_PAUSE = "BSH.Common.Command.PauseProgram"
BSH_RESUME = "BSH.Common.Command.ResumeProgram"

SIGNAL_UPDATE_ENTITIES = "home_connect.update_entities"

SERVICE_OPTION_ACTIVE = "set_option_active"
SERVICE_OPTION_SELECTED = "set_option_selected"
SERVICE_PAUSE_PROGRAM = "pause_program"
SERVICE_RESUME_PROGRAM = "resume_program"
SERVICE_SELECT_PROGRAM = "select_program"
SERVICE_SETTING = "change_setting"
SERVICE_GET_DATA = "get_data"
SERVICE_START_PROGRAM = "start_program"

SERVICE_EXCEPTION_RESPONSE = {"error": "Service call failed."}

ATTR_AMBIENT = "ambient"
ATTR_DESC = "desc"
ATTR_DEVICE = "device"
ATTR_ENDPOINT = "endpoint"
ATTR_KEY = "key"
ATTR_PROGRAM = "program"
ATTR_SENSOR_TYPE = "sensor_type"
ATTR_SIGN = "sign"
ATTR_UNIT = "unit"
ATTR_VALUE = "value"
