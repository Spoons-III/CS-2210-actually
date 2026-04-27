; Input:  R3 (upper limit N)
; Output: R2 (sum of 1 + 2 + ... + N)
; Uses:   R0 (constant 1), R1 (counter), R4 (throwaway for flag-setting)

START:
    LOADI   R0, #1        ; constant 1
    ; three more LOADI here
LOOP:
    ; complete loop here
DONE:
    HALT
popcount.asm
Count the number of set bits in a 16-bit word. Example: If we have 0010 0011 1111 0100 there are eight bits set. If we have 0000 0000 0000 0000 there are zero bits set.

Here’s some scaffolding / starter code:

; Input:  R1 (16-bit value)
; Output: R2 (number of set bits, 0-16)
; Uses:   R3 (loop counter), R4 (limit = 16), R5 (LSB mask),
;         R6 (shift control), R7 (throwaway for AND / flag-setting)
;
; Strategy: test LSB, shift right by 1, repeat 16 times.

    LOADI R1, #0x0F       ; test value (4 set bits)
    LOADI R2, #0          ; count = 0
    ; complete the problem setup here
LOOP:
    ; complete loop
    BLT   LOOP            ; if counter < 16, continue
DONE:
    HALT