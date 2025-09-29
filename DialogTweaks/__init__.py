from mods_base import build_mod, hook, Game, Mod, BoolOption, NestedOption, SliderOption
from typing import Any, Dict
from unrealsdk import find_all, find_object
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction


WHITELIST = {
    Game.BL3:[
    ],
    Game.WL:[
        # Tutorial Prophecy to quest complete
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M00.DialogScript_Main_M00:DialogTimeSlotData_187.DialogLineData_0.DialogPerformanceData_0'",
        # Ballad of Bones First Mate
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_136.DialogLineData_0.DialogPerformanceData_0'",
        # Ballad of Bones Marley Maiden Tunnel
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_73.DialogLineData_0.DialogPerformanceData_0'",
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_187.DialogLineData_0.DialogPerformanceData_0'",
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_157.DialogLineData_0.DialogPerformanceData_0'",
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_225.DialogLineData_0.DialogPerformanceData_0'",
        # Ossu-gol First Barrier
        "DialogPerformanceData'/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M09.DialogScript_Main_M09:DialogTimeSlotData_101.DialogLineData_0.DialogPerformanceData_0'",
    ]
}[Game.get_current()]
"""DialogPerformanceDatas that break sequences if they are skipped, so we exclude them."""


# Commented items aren't loaded at the main menu at least - but might be in specific maps
_stylesDict = {
    "Enemy Callouts" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_BattleDialog_Patient.DialogStyle_BattleDialog_Patient"),
    #"Enemy Taunts" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_BattleDialog_Taunt.DialogStyle_BattleDialog_Taunt")
    "Enemy Death" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_BattleDialog_Death.DialogStyle_BattleDialog_Death"),
    "Enemy Critical" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_BattleDialog_Critical.DialogStyle_BattleDialog_Critical"),
    "Player Callouts" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_BattleDialog_Player_Patient.DialogStyle_BattleDialog_Player_Patient"),
    "Player Interrupts" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_BattleDialog_Player_Interrupt.DialogStyle_BattleDialog_Player_Interrupt"),
    #"Echo Logs" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_EchoLogs.DialogStyle_EchoLogs"),
}
if Game.get_current() is Game.WL:
    _stylesDict = _stylesDict | {
        "NPC Ambient" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_VOCT.DialogStyle_VOCT"),
        "NPC Interact" : find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_VOCT_Interact.DialogStyle_VOCT_Interact"),
    }

_storyStyles = [
    find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_High.DialogStyle_Scripted_High"),
    #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_High_Simultaneous.DialogStyle_Scripted_High_Simultaneous"),
]
if Game.get_current() is Game.BL3:
    _storyStyles += [
        #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_High_Interrupt.DialogStyle_Scripted_High_Interrupt"),
        #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_High_NoSubs.DialogStyle_Scripted_High_NoSubs"),
        find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_High_NoWait.DialogStyle_Scripted_High_NoWait"),
        #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_High_Simultaneous_NoSubs.DialogStyle_Scripted_High_Simultaneous_NoSubs"),
        find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_Low.DialogStyle_Scripted_Low"),
        find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_Low_NoSubs.DialogStyle_Scripted_Low_NoSubs"),
        #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_MultiLine_Playback.DialogStyle_Scripted_MultiLine_Playback"),
        #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_MultiLine_Playback_NoSubs.DialogStyle_Scripted_MultiLine_Playback_NoSubs"),
        #find_object("DialogStyle","/Game/Dialog/Styles/DialogStyle_Scripted_VOG.DialogStyle_Scripted_VOG")
    ]

_pathDict = {
    Game.BL3: {
        "New-U" : "/Game/Dialog/Scripts/VOCT/DialogScript_VOCT_NEW-U",
        "Hunt Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Hunt",
        "Kill Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Kill",
        "Sabotage Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Sabotage",
        "Salvage Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Salvage",
        "Typhon Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Typhon",
        "Vehicle Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Vehicle",
        "Writings Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Crew_Challenges_Writings"
    },
    Game.WL : {
        "New-U" : "/Game/Dialog/Scripts/VOCT/DialogScript_VOCT_NEW-U",
        "Quick Change" : "/Game/Dialog/Scripts/Misc/DialogScript_CharSamples",
        "Overworld Shortcuts" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Tina_ShortCuts",
        "Overworld Shrines" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Shrines_Challenge",
        "Amnesiac Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Amnesiac_Challenge",
        "Poetry Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Poetry_Challenge",
        "RuneSwitch Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_RuneSwitch_Challenge",
        "Obelisk Challenge" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_Obelisk_Challenge",
        "Golden Dice" : "/Game/Dialog/Scripts/CrewChallenges/DialogScript_GoldenDice_Challenge"
    }
}[Game.get_current()]

_originalChances: Dict[int, float] = {}


anyEnabled: BoolOption = BoolOption("All Dialog", True, "On", "Off")
storyEnabled: BoolOption = BoolOption("Story Dialog", True, "On", "Off")
calloutsEnabled: BoolOption = BoolOption("Combat Callouts", True, "On", "Off", description="Includes companion callouts.")
dotEnabled: BoolOption = BoolOption("DOT Screams", True, "On", "Off", description="Requires a map change to re-enable.")
painEnabled: BoolOption = BoolOption("Pain/Stagger/Flinch", True, "On", "Off")
deathEnabled: BoolOption = BoolOption("Creature Deaths", True, "On", "Off")
echoesEnabled: BoolOption = BoolOption("ECHO Logs/Lore Scrolls", True, "On", "Off")
styleOptions = NestedOption("Frequency Options", [
        SliderOption(key, 100, 0, 100, description="The percentage chance for this type of dialog to play, scaled by the default chance to play.")
        for key in _stylesDict.keys()
    ], description="Options for adjusting each style of dialog's chance to play."
)
classOptions = NestedOption("World Options", [BoolOption(key, True, "On", "Off") for key in _pathDict.keys()])

def GetStyleOptionValueFromKey(key: str) -> int:
    for opt in styleOptions.children:
        if opt.identifier is key:
            return opt.value # type: ignore
    return 1

def GetClassOptionValueFromKey(key: str) -> bool:
    for opt in classOptions.children:
        if opt.identifier is key:
            return opt.value # type: ignore
    return True


# Some CharacterSoundDatas mustn't be loaded for /Script/Engine.PlayerController:ServerNotifyLoadedWorld
# We can't access these through the Pawn classes when they spawn because they are in TMaps.
# So we need a hook that occurs just after the level loads, and handles Chaos Chamber / Overworld loading.
# /Script/OakGame.GFxExperienceBar:extFinishedDim doesn't exist in Wonderlands
@hook("/Script/Engine.PlayerController:ServerNotifyLoadedWorld", Type.POST)
def LoadedWorld(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    """ Called when a new level is loaded. """
    global _originalChances
    _originalChances = {}
    UpdateDialogObjects()
    UpdateSoundObjects()

@hook("/Script/OakGame.endlessdungeon:Multicast_OnRoomBeginPlay", Type.POST)    # Chaos Chamber / Overworld room
def ExecuteTeleport(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    UpdateSoundObjects()


def ApplyChanceToPlayScale(obj: UObject, percentage: int):
    global _originalChances
    if obj.InternalIndex not in _originalChances:
        _originalChances[obj.InternalIndex] = obj.ChanceToPlay
    
    if percentage == 100:
        obj.ChanceToPlay = _originalChances[obj.InternalIndex]
        return
    if percentage == 0:
        obj.ChanceToPlay = 0
        return
    obj.ChanceToPlay = _originalChances[obj.InternalIndex] * (percentage / 100)
    
                
def UpdateDialogObjects():
    """
    Find all the loaded DialogPerformanceDatas, and adjust the ChanceToPlays.
    """
    for perf in find_all("DialogPerformanceData"):
        if str(perf) in WHITELIST:
            continue
        
        ApplyChanceToPlayScale(perf, 100)
        
        if not anyEnabled.value:
            ApplyChanceToPlayScale(perf, 0)
            continue

        if perf.EchoData:
            if not echoesEnabled.value:
                ApplyChanceToPlayScale(perf, 0)
            continue
        
        if perf.style is not None:
            if not calloutsEnabled.value and perf.style.bCallout:
                ApplyChanceToPlayScale(perf, 0)
                continue
            if not storyEnabled.value and perf.style in _storyStyles:
                ApplyChanceToPlayScale(perf, 0)
                continue
            for k,v in _stylesDict.items():
                if perf.style is v:
                    percentage = GetStyleOptionValueFromKey(k)
                    ApplyChanceToPlayScale(perf, percentage)
                    break
        
        for k,v in _pathDict.items():
            if not GetClassOptionValueFromKey(k):
                if str(perf).startswith("DialogPerformanceData'" + v):
                    ApplyChanceToPlayScale(perf, 0)
                    break


def UpdateSoundObjects():
    """
    Find all the loaded CharacterSoundTags and CharacterSoundDatas,
    and adjust the ChanceToPlays, or block DOT effects.
    """
    for tag in find_all("CharacterSoundTag"):
        if tag.bPainVox:
            if not painEnabled.value:
                ApplyChanceToPlayScale(tag, 0)
            else:
                ApplyChanceToPlayScale(tag, 100)
        elif tag.bDeathVox:
            if not deathEnabled.value:
                ApplyChanceToPlayScale(tag, 0)
            else:
                ApplyChanceToPlayScale(tag, 100)
    
    for data in find_all("OakCharacterSoundData"):
        data.bOverrideCorrosivePainLoop = dotEnabled.value
        data.bOverrideCryoPainLoop = dotEnabled.value
        data.bOverrideFirePainLoop = dotEnabled.value
        data.bOverrideRadiationPainLoop = dotEnabled.value
        data.bOverrideShockPainLoop = dotEnabled.value
        if Game.get_current() is Game.BL3:
            data.bOverrideSlagPainLoop = dotEnabled.value
        if Game.get_current() is Game.WL:
            data.bOverrideDarkMagicPainLoop = dotEnabled.value
            data.bOverridePoisonPainLoop = dotEnabled.value
        
        if not dotEnabled.value:
            data.CorrosivePainLoop = None
            data.CryoPainLoop = None
            data.FirePainLoop = None
            data.RadiationPainLoop = None
            data.ShockPainLoop = None
            if Game.get_current() is Game.BL3:
                data.SlagPainLoop = None
            if Game.get_current() is Game.WL:
                data.DarkMagicPainLoop = None
                data.PoisonPainLoop = None



class OnSaveSettingsMod(Mod):
    """Subclass mod to update objects on mod save instead of option change, to make adjusting sliders smoother."""
    def save_settings(self) -> None:
        super().save_settings()
        UpdateSoundObjects()
        UpdateDialogObjects()


mod: Mod = build_mod(cls=OnSaveSettingsMod, options=[anyEnabled,storyEnabled,styleOptions,calloutsEnabled,dotEnabled,painEnabled,deathEnabled,classOptions,echoesEnabled])
