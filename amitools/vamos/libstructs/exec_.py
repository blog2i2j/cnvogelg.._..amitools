from amitools.vamos.astructs import (
    AmigaStructDef,
    AmigaStruct,
    APTR_SELF,
    APTR_VOID,
    APTR,
    UBYTE,
    BYTE,
    UWORD,
    WORD,
    ULONG,
    LONG,
    CSTR,
    ARRAY,
)

# Node
@AmigaStructDef
class NodeStruct(AmigaStruct):
    _format = [
        (APTR_SELF, "ln_Succ"),
        (APTR_SELF, "ln_Pred"),
        (UBYTE, "ln_Type"),
        (BYTE, "ln_Pri"),
        (CSTR, "ln_Name"),
    ]


# MinNode
@AmigaStructDef
class MinNodeStruct(AmigaStruct):
    _format = [(APTR_SELF, "mln_Succ"), (APTR_SELF, "mln_Pred")]


# Library
@AmigaStructDef
class LibraryStruct(AmigaStruct):
    _format = [
        (NodeStruct, "lib_Node"),
        (UBYTE, "lib_Flags"),
        (UBYTE, "lib_pad"),
        (UWORD, "lib_NegSize"),
        (UWORD, "lib_PosSize"),
        (UWORD, "lib_Version"),
        (UWORD, "lib_Revision"),
        (CSTR, "lib_IdString"),
        (ULONG, "lib_Sum"),
        (UWORD, "lib_OpenCnt"),
    ]


# List
@AmigaStructDef
class ListStruct(AmigaStruct):
    _format = [
        (APTR(NodeStruct), "lh_Head"),
        (APTR(NodeStruct), "lh_Tail"),
        (APTR(NodeStruct), "lh_TailPred"),
        (UBYTE, "lh_Type"),
        (UBYTE, "l_pad"),
    ]


# MinList
@AmigaStructDef
class MinListStruct(AmigaStruct):
    _format = [
        (APTR(MinNodeStruct), "mlh_Head"),
        (APTR(MinNodeStruct), "mlh_Tail"),
        (APTR(MinNodeStruct), "mlh_TailPred"),
    ]


# MsgPort
@AmigaStructDef
class MsgPortStruct(AmigaStruct):
    _format = [
        (NodeStruct, "mp_Node"),
        (UBYTE, "mp_Flags"),
        (UBYTE, "mp_SigBit"),
        (APTR_VOID, "mp_SigTask"),
        (ListStruct, "mp_MsgList"),
    ]


# Message
@AmigaStructDef
class MessageStruct(AmigaStruct):
    _format = [
        (NodeStruct, "mn_Node"),
        (APTR(MsgPortStruct), "mn_ReplyPort"),
        (UWORD, "mn_Length"),
    ]


# IntVector
@AmigaStructDef
class IntVectorStruct(AmigaStruct):
    _format = [
        (APTR_VOID, "iv_Data"),
        (APTR_VOID, "iv_Code"),
        (APTR(NodeStruct), "iv_Node"),
    ]


# SoftIntList
@AmigaStructDef
class SoftIntListStruct(AmigaStruct):
    _format = [(ListStruct, "sh_List"), (UWORD, "sh_Pad")]


# Task
@AmigaStructDef
class TaskStruct(AmigaStruct):
    _format = [
        (NodeStruct, "tc_Node"),
        (UBYTE, "tc_Flags"),
        (UBYTE, "tc_State"),
        (BYTE, "tc_IDNestCnt"),
        (BYTE, "tc_TDNestCnt"),
        (ULONG, "tc_SigAlloc"),
        (ULONG, "tc_SigWait"),
        (ULONG, "tc_SigRecvd"),
        (ULONG, "tc_SigExcept"),
        (UWORD, "tc_TrapAlloc"),
        (UWORD, "tc_TrapAble"),
        (APTR_VOID, "tc_ExceptData"),
        (APTR_VOID, "tc_ExceptCode"),
        (APTR_VOID, "tc_TrapData"),
        (APTR_VOID, "tc_TrapCode"),
        (APTR_VOID, "tc_SPReg"),
        (APTR_VOID, "tc_SPLower"),
        (APTR_VOID, "tc_SPUpper"),
        (APTR_VOID, "tc_Switch"),
        (APTR_VOID, "tc_Launch"),
        (ListStruct, "tc_MemEntry"),
        (APTR_VOID, "tc_UserData"),
    ]


@AmigaStructDef
class ExecLibraryStruct(AmigaStruct):
    _format = [
        (LibraryStruct, "LibNode"),
        # Static System Variables
        (UWORD, "SoftVer"),
        (WORD, "LowMemChkSum"),
        (ULONG, "ChkBase"),
        (APTR_VOID, "ColdCapture"),
        (APTR_VOID, "CoolCapture"),
        (APTR_VOID, "WarmCapture"),
        (APTR_VOID, "SysStkUpper"),
        (APTR_VOID, "SysStkLower"),
        (ULONG, "MaxLocMem"),
        (APTR_VOID, "DebugEntry"),
        (APTR_VOID, "DebugData"),
        (APTR_VOID, "AlertData"),
        (APTR_VOID, "MaxExtMem"),
        (UWORD, "ChkSum"),
        # Interrupt Related
        (ARRAY(IntVectorStruct, 16), "IntVects"),
        # Dynamic System Variables
        (APTR(TaskStruct), "ThisTask"),
        (ULONG, "IdleCount"),
        (ULONG, "DispCount"),
        (UWORD, "Quantum"),
        (UWORD, "Elapsed"),
        (UWORD, "SysFlags"),
        (BYTE, "IDNestCnt"),
        (BYTE, "TDNestCnt"),
        (UWORD, "AttnFlags"),
        (UWORD, "AttnResched"),
        (APTR_VOID, "ResModules"),
        (APTR_VOID, "TaskTrapCode"),
        (APTR_VOID, "TaskExceptCode"),
        (APTR_VOID, "TaskExitCode"),
        (ULONG, "TaskSigAlloc"),
        (UWORD, "TaskTrapAlloc"),
        # System Lists (private!)
        (ListStruct, "MemList"),
        (ListStruct, "ResourceList"),
        (ListStruct, "DeviceList"),
        (ListStruct, "IntrList"),
        (ListStruct, "LibList"),
        (ListStruct, "PortList"),
        (ListStruct, "TaskReady"),
        (ListStruct, "TaskWait"),
        (ARRAY(SoftIntListStruct, 5), "SoftIntList"),
        # Other Globals
        (ARRAY(ULONG, 4), "LastAlert"),
        (UBYTE, "VBlankFrequency"),
        (UBYTE, "PowerSupplyFrequency"),
        (ListStruct, "SemaphoreList"),
        (APTR_VOID, "KickMemPtr"),
        (APTR_VOID, "KickTagPtr"),
        (APTR_VOID, "KickCheckSum"),
        # V36 Additions
        (ULONG, "ex_Pad0"),
        (ULONG, "ex_LaunchPoint"),
        (APTR_VOID, "ex_RamLibPrivate"),
        (ULONG, "ex_EClockFrequency"),
        (ULONG, "ex_CacheControl"),
        (ULONG, "ex_TaskID"),
        (ARRAY(ULONG, 5), "ex_Reserved1"),
        (APTR_VOID, "ex_MMULock"),
        (ARRAY(ULONG, 3), "ex_Reserved2"),
        # V39 Additions
        (MinListStruct, "ex_MemHandlers"),
        (APTR_VOID, "ex_MemHandler"),
    ]


# StackSwap
@AmigaStructDef
class StackSwapStruct(AmigaStruct):
    _format = [
        (APTR_VOID, "stk_Lower"),
        (ULONG, "stk_Upper"),
        (APTR_VOID, "stk_Pointer"),
    ]


# Semaphores
@AmigaStructDef
class SemaphoreRequestStruct(AmigaStruct):
    _format = [(MinNodeStruct, "sr_Link"), (APTR(TaskStruct), "sr_Waiter")]


@AmigaStructDef
class SignalSemaphoreStruct(AmigaStruct):
    _format = [
        (NodeStruct, "ss_Link"),
        (WORD, "ss_NestCount"),
        (MinListStruct, "ss_WaitQueue"),
        (SemaphoreRequestStruct, "ss_MultipleLink"),
        (APTR(TaskStruct), "ss_Owner"),
        (WORD, "ss_QueueCount"),
    ]


# Device
@AmigaStructDef
class DeviceStruct(AmigaStruct):
    _format = [(LibraryStruct, "dd_Library")]


# Unit
@AmigaStructDef
class UnitStruct(AmigaStruct):
    _format = [
        (MsgPortStruct, "unit_MsgPort"),
        (UBYTE, "unit_flags"),
        (UBYTE, "unit_pad"),
        (UWORD, "unit_OpenCnt"),
    ]


# IORequests
@AmigaStructDef
class IORequestStruct(AmigaStruct):
    _format = [
        (MessageStruct, "io_Message"),
        (APTR(DeviceStruct), "io_Device"),
        (UnitStruct, "io_Unit"),
        (UWORD, "io_Command"),
        (UBYTE, "io_Flags"),
        (BYTE, "io_Error"),
        (ULONG, "io_Actual"),
        (ULONG, "io_Length"),
        (ULONG, "io_Data"),
        (ULONG, "io_Offset"),
    ]


# MemChunk
@AmigaStructDef
class MemChunkStruct(AmigaStruct):
    _format = [(APTR_SELF, "mc_Next"), (ULONG, "mc_Bytes")]


# MemHeader
@AmigaStructDef
class MemHeaderStruct(AmigaStruct):
    _format = [
        (NodeStruct, "mh_Node"),
        (UWORD, "mh_Attributes"),
        (APTR(MemChunkStruct), "mh_First"),
        (APTR_VOID, "mh_Lower"),
        (APTR_VOID, "mh_Upper"),
        (ULONG, "mh_Free"),
    ]


# Resident
@AmigaStructDef
class ResidentStruct(AmigaStruct):
    _format = [
        (UWORD, "rt_MatchWord"),
        (APTR_VOID, "rt_MatchTag"),
        (APTR_VOID, "rt_EndSkip"),
        (UBYTE, "rt_Flags"),
        (UBYTE, "rt_Version"),
        (UBYTE, "rt_Type"),
        (BYTE, "rt_Pri"),
        (CSTR, "rt_Name"),
        (CSTR, "rt_IdString"),
        (APTR_VOID, "rt_Init"),
    ]


# AutoInit used in Residents
@AmigaStructDef
class AutoInitStruct(AmigaStruct):
    _format = [
        (ULONG, "ai_PosSize"),
        (APTR_VOID, "ai_Functions"),
        (APTR_VOID, "ai_InitStruct"),
        (APTR_VOID, "ai_InitFunc"),
    ]
