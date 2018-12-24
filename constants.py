from telnetlib import IAC, WILL, WONT, DO, DONT, TTYPE, SB, SE

IS = chr(0)

MSDP = chr(69)

MSDP_VAR = chr(1)
MSDP_VAL = chr(2)

MSDP_TABLE_OPEN = chr(3)
MSDP_TABLE_CLOSE = chr(4)

MSDP_ARRAY_OPEN = chr(5)
MSDP_ARRAY_CLOSE = chr(6)

TELNET_CODES = {
    DO: "DO",
    DONT: "DONT",
    WILL: "WILL",
    WONT: "WONT",
    IS: "IS",
    MSDP: "MSDP",
    MSDP_VAR: "MSDP_VAR",
    MSDP_VAL: "MSDP_VAL",
}
