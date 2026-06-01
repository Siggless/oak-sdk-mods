from mods_base import build_mod, hook, Game
from typing import Any
from unrealsdk import find_enum, find_object, construct_object
from unrealsdk.hooks import Block, Type, prevent_hooking_direct_calls
from unrealsdk.unreal import BoundFunction, UObject, WeakPointer, WrappedStruct, notify_changes


EPlayerDroppability = find_enum("EPlayerDroppability")
EUsabilityType = find_enum("EUsabilityType")
baseUsableDefinition = find_object("UsableTypeDefinition", "/Game/UI/InteractionPrompt/UIData_Take.UIData_Take")
with notify_changes():
    newUseDef = construct_object(
        baseUsableDefinition.Class,
        baseUsableDefinition.Outer,
        "UIData_PickupAsTrash",
        baseUsableDefinition.ObjectFlags | 0x0080,    # KeepAlive
        None    # Crashes on ActionText set, if we use a template
    )
    newUseDef.ActionText = 'Pickup As Trash'
pickupAsTrashUseDef = WeakPointer(newUseDef)


#@hook("/Script/GbxInventory.DroppedInventoryItemPickup:OnPhysicsWake")
@hook("/Script/GbxInventory.InventoryItemPickup:OnLookedAtByPlayer")
def OnPhysicsWake(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if obj.PickupCategory and obj.PickupCategory.NotAddedToInventory:
        return
    if not obj.AssociatedInventoryData or obj.AssociatedInventoryData.PlayerDroppability != EPlayerDroppability.EPD_CanDropAndSell:
        return
    if not obj.BP_PickupUsableComponent:
        return

    global pickupAsTrashUseDef
    if pickupAsTrashUseDef() is None:
        return

    useComponent: UObject = obj.BP_PickupUsableComponent    #CachedUsableComponent better?
    
    # By default I am only replacing the overriden SecondaryUseDef, in case some items have crucial default ones.
    # Sellable items with null overrides get their default SecondaryUseDef replaced, to cover cosmetics.
    if not useComponent.UsabilityData:
        useComponent.SecondaryUseDefSelection.DefaultUseDefinition = pickupAsTrashUseDef()
    else:
        # NOTE In BL3 the HUD only shows max 2 use prompts, so this still doesn't show if the Hold Equip is there.
        useComponent.UsabilityData.SecondaryUseDefSelection.DefaultUseDefinition = pickupAsTrashUseDef()        
        # I can't tell if the overriden SecondaryUseDef or the base one has been used.
        # So I'm always overriding with PickupAsTrash. From what I've seen this just replaces
        # the "Equip Right" prompts on Rings and Spells (with Ambihextrous).
        useComponent.UsabilityData.SecondaryUseDefSelection.ConditionalUseDefs = []


@hook("/Script/GbxInventory.InventoryItemPickup:OnUsedBy", Type.PRE)
def OnUsedBy(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
    if args.UseEvent.UseType != EUsabilityType.Secondary or args.UseEvent.bWasHeld:
        return
    
    if not (useComponent := obj.BP_PickupUsableComponent):
        return
    if pickupAsTrashUseDef() is None:
        return

    if useComponent.SecondaryUseDefSelection.DefaultUseDefinition is not pickupAsTrashUseDef():
        if not useComponent.UsabilityData or useComponent.UsabilityData.SecondaryUseDefSelection.DefaultUseDefinition is not pickupAsTrashUseDef():
            return
    char = args.UseEvent.UserController.Character
    if not (inv := char.InventoryList):
        return
    # I don't think I need to check the length for whether picked up or not, since I'm checking CanBePickedUp,
    # but best be safe with people's inventories.
    prePickupLength = len(inv.InventoryList.Items)

    if not obj.CanBePickedUp(char, True, False, False):
        # Inventory full or summin
        return
    
    # GBX must've coded the weapon auto-equip check as "not primary", so we need the hooked function to
    # run with the proper Primary type, to make sure this doesn't happen for guns
    with prevent_hooking_direct_calls():
        args.UseEvent.UseType = EUsabilityType.Primary
        obj.OnUsedBy(args.UseEvent)
    
    if prePickupLength < len(inv.InventoryList.Items):
        invItem = inv.InventoryList.Items[-1]
        inv.ServerSetItemUIFlags(invItem.Handle, 0b101, 0b111)  # 0 is seen (not new), 1 is favourite, 2 is trash
    
    return Block


# Add Sell All Trash vendor interaction to BL3
if Game.get_current() is Game.BL3:
    with notify_changes():
        vendorDef = construct_object(
            baseUsableDefinition.Class,
            baseUsableDefinition.Outer,
            "UIData_PickupAsTrash_SellAllTrash",
            baseUsableDefinition.ObjectFlags | 0x0080,    # KeepAlive
        )
        vendorDef.ActionText = 'Sell All Trash'
    vendorUseDef = WeakPointer(vendorDef)


    @hook("/Script/OakGame.AdvancedInteractiveObject:OnAnyPlayersNowInInteractRange")
    def OnAnyPlayersNowInInteractRange(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
        if obj.Name.startswith('BP_VendingMachine_Weapons'):
            if not obj.UsableComponent:
                return
            if not (useData := obj.UsableComponent.UsabilityData):
                return
            if vendorUseDef():
                useData.SecondaryUseDefSelection.DefaultUseDefinition = vendorUseDef()
                useData.SecondaryUseDefSelection.ConditionalUseDefs = []
    
    
    @hook("/Script/OakGame.AdvancedInteractiveObject:NotifyUsed")
    def NotifyUsed(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> type[Block] | None:
        if args.UseEvent.UseType != EUsabilityType.Secondary or args.UseEvent.bWasHeld:
            return
        if not obj.UsableComponent:
            return
        if not (useData := obj.UsableComponent.UsabilityData):
            return
        if vendorUseDef() is not None and useData.SecondaryUseDefSelection.DefaultUseDefinition is vendorUseDef():
            pc = args.UseEvent.UserController
            if component := pc.ShopManagerComponent:
                char = pc.Character
                echo = char.GetEchoDevice()
                inv = char.InventoryList
                if inv:
                    # Track inventory size to determine if we actually sold any junk
                    preSellLength = len(inv.InventoryList.Items)
                    
                    component.ServerSellAllJunk()
                    
                    if len(inv.InventoryList.Items) < preSellLength:
                        obj.K2_OnSoldAllJunk()  # Play vendor VO
                        if echo:
                            pc.ClientPlayWwiseEvent(echo.ConfirmSound)
                    elif echo:
                        pc.ClientPlayWwiseEvent(echo.ErrorSound)


build_mod()
