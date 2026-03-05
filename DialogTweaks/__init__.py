from mods_base import build_mod, hook, Game, Mod, BoolOption, NestedOption, SliderOption
from typing import Any, Dict, List
from unrealsdk import find_all, find_object
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction


WHITELIST = {
    Game.BL3:[
        # Sanctuary decompression crash
        "/Game/Dialog/Scripts/Scripted/DialogScript_Sanctuary.DialogScript_Sanctuary:DialogTimeSlotData_24.DialogLineData_24.DialogPerformanceData_24",
        # Lorelei door objective advance
        "/Game/Dialog/Scripts/Scripted/DialogScript_Hostile_Takeover.DialogScript_Hostile_Takeover:DialogTimeSlotData_73.DialogLineData_0.DialogPerformanceData_0",
        #"/Game/Dialog/Scripts/Scripted/DialogScript_Hostile_Takeover.DialogScript_Hostile_Takeover:DialogTimeSlotData_126.DialogLineData_0.DialogPerformanceData_0",
        # Follow Maya bell 3
        "/Game/Dialog/Scripts/Scripted/DialogScript_Monastery.DialogScript_Monastery:DialogTimeSlotData_104.DialogLineData_0.DialogPerformanceData_0",
        # Sanctuary 3 Lilith Maya convo block
        '/Game/Dialog/Scripts/Scripted/DialogScript_Monastery.DialogScript_Monastery:DialogTimeSlotData_145.DialogLineData_0.DialogPerformanceData_0',
        # Rhys-ball wake
        '/Game/Dialog/Scripts/Scripted/DialogScript_Orbital_Platform.DialogScript_Orbital_Platform:DialogTimeSlot_Orbital_Platform_105.DialogLine_Orbital_Platform_105_01.DialogPerformance_Orbital_Platform_105_01_01',
        # Beneath the Meridian Zer0 appearance
        '/Game/Dialog/Scripts/Scripted/DialogScript_City_Vault.DialogScript_City_Vault:DialogTimeSlotData_30.DialogLineData_0.DialogPerformanceData_0',
        # Beneath the Meridian funeral end
        '/Game/Dialog/Scripts/Scripted/DialogScript_City_Vault.DialogScript_City_Vault:DialogTimeSlotData_174.DialogLineData_0.DialogPerformanceData_0',
        # Hammerlocked start
        '/Game/Dialog/Scripts/Scripted/DialogScript_Prison.DialogScript_Prison:DialogTimeSlotData_27.DialogLineData_1.DialogPerformanceData_1',
        #'/Game/Dialog/Scripts/Scripted/DialogScript_Prison.DialogScript_Prison:DialogTimeSlotData_28.DialogLineData_2.DialogPerformanceData_2',
        # Family Jewel BALEX mech activation
        '/Game/Dialog/Scripts/Scripted/DialogScript_Watership.DialogScript_Watership:DialogTimeSlotData_229.DialogLineData_93.DialogPerformanceData_97',
        # The First VH Lilith
        '/Game/Dialog/Scripts/Scripted/DialogScript_Desolate.DialogScript_Desolate:DialogTimeSlotData_9.DialogLineData_0.DialogPerformanceData_0',
        # Footsteps of Giants grave key
        '/Game/Dialog/Scripts/Scripted/DialogScript_Beach.DialogScript_Beach:DialogTimeSlotData_72.DialogLineData_0.DialogPerformanceData_0',
    ],
    Game.WL:[
        # Tutorial Prophecy to quest complete
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M00.DialogScript_Main_M00:DialogTimeSlotData_187.DialogLineData_0.DialogPerformanceData_0",
        # Ballad of Bones First Mate
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_136.DialogLineData_0.DialogPerformanceData_0",
        # Ballad of Bones Marley Maiden Tunnel
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_73.DialogLineData_0.DialogPerformanceData_0",
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_187.DialogLineData_0.DialogPerformanceData_0",
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_157.DialogLineData_0.DialogPerformanceData_0",
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M06.DialogScript_Main_M06:DialogTimeSlotData_225.DialogLineData_0.DialogPerformanceData_0",
        # Ossu-gol First Barrier
        "/Game/Dialog/Scripts/MainMissions/DialogScript_Main_M09.DialogScript_Main_M09:DialogTimeSlotData_101.DialogLineData_0.DialogPerformanceData_0",
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
    "/Game/Dialog/Styles/DialogStyle_Scripted_High.DialogStyle_Scripted_High",
    "/Game/Dialog/Styles/DialogStyle_Scripted_High_Simultaneous.DialogStyle_Scripted_High_Simultaneous",
]
if Game.get_current() is Game.BL3:
    _storyStyles += [
        "/Game/Dialog/Styles/DialogStyle_Scripted_High_Interrupt.DialogStyle_Scripted_High_Interrupt",
        "/Game/Dialog/Styles/DialogStyle_Scripted_High_NoSubs.DialogStyle_Scripted_High_NoSubs",
        "/Game/Dialog/Styles/DialogStyle_Scripted_High_NoWait.DialogStyle_Scripted_High_NoWait",
        "/Game/Dialog/Styles/DialogStyle_Scripted_High_Simultaneous_NoSubs.DialogStyle_Scripted_High_Simultaneous_NoSubs",
        "/Game/Dialog/Styles/DialogStyle_Scripted_Low.DialogStyle_Scripted_Low",
        "/Game/Dialog/Styles/DialogStyle_Scripted_Low_NoSubs.DialogStyle_Scripted_Low_NoSubs",
        "/Game/Dialog/Styles/DialogStyle_Scripted_MultiLine_Playback.DialogStyle_Scripted_MultiLine_Playback",
        "/Game/Dialog/Styles/DialogStyle_Scripted_MultiLine_Playback_NoSubs.DialogStyle_Scripted_MultiLine_Playback_NoSubs",
        "/Game/Dialog/Styles/DialogStyle_Scripted_VOG.DialogStyle_Scripted_VOG"
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

try:
    reloading   # type: ignore
except NameError:
    reloading = False # means the module is being imported
    _originalDialogChances: Dict[int, float] = {}
    _originalSoundChances: Dict[str, float] = {}
    _loadedStoryStyles: List[UObject] = []
    #print("import")
else:
    reloading = True # means the module is being reloaded
    #print("reload")


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
    global _originalDialogChances, _originalSoundChances, _loadedStoryStyles, _storyStyles
    _loadedStoryStyles = []
    for s in _storyStyles:
        try:
            _loadedStoryStyles.append(find_object("DialogStyle", s))
        except:
            pass
    UpdateDialogObjects()
    UpdateSoundObjects()

@hook("/Script/OakGame.endlessdungeon:Multicast_OnRoomBeginPlay", Type.POST)    # Chaos Chamber / Overworld room
def ExecuteTeleport(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    UpdateSoundObjects()

@hook("/Script/OakGame.OakDialogBlackboard:BindEchoLogInitialPlayFinished", Type.POST)
def BindEchoLogInitialPlayFinished(obj, args, ret, func: BoundFunction):
    if echoesEnabled.value and storyEnabled.value:
        return
    finishedEvent: BoundFunction = args.Event
    if finishedEvent:
        finishedEvent()


def ApplyChanceToPlayScale(obj: UObject, percentage: int):
    """
    Some objects remain loaded across levels so we can't just reset our dicts if we want to store the original chances.
    We need a unique ID for an object to store and retrieve these chances (or keep a pointer and check if unloaded).
    We can't use InternalIndex because these get allocated on load and reallocated if unloaded.
    We use WwiseEventShortID for DialogPerformanceDatas because these seem to be fixed.
    For others we just use the Name.
    """
    global _originalDialogChances, _originalSoundChances
    objID: int | str = obj.Name
    originals: Dict[Any, float] = _originalSoundChances
    if hasattr(obj, "WwiseEventShortID"):
        objID = obj.WwiseEventShortID
        originals = _originalDialogChances

    if objID not in originals:
        originals[objID] = obj.ChanceToPlay
    
    if percentage == 100:
        obj.ChanceToPlay = originals[objID]
        return
    if percentage == 0:
        obj.ChanceToPlay = 0
        return
    obj.ChanceToPlay = originals[objID] * (percentage / 100)

                
def UpdateDialogObjects():
    """
    Find all the loaded DialogPerformanceDatas, and adjust the ChanceToPlays.
    """
    for perf in find_all("DialogPerformanceData"):
        
        ApplyChanceToPlayScale(perf, 100)
        
        if not anyEnabled.value:
            ApplyChanceToPlayScale(perf, 0)
            continue

        if perf.EchoData:
            if not echoesEnabled.value:
                ApplyChanceToPlayScale(perf, 0)
            continue
        
        if perf.Style is not None:
            if not calloutsEnabled.value and perf.Style.bCallout:
                ApplyChanceToPlayScale(perf, 0)
                continue
            if not storyEnabled.value and perf.Style in _loadedStoryStyles:
                ApplyChanceToPlayScale(perf, 0)
                continue
            for k,v in _stylesDict.items():
                if perf.Style is v:
                    percentage = GetStyleOptionValueFromKey(k)
                    ApplyChanceToPlayScale(perf, percentage)
                    break
        
        for k,v in _pathDict.items():
            if not GetClassOptionValueFromKey(k):
                if perf._path_name().startswith(v):
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
