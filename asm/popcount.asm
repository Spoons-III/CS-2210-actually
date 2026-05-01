; Input:  R1 (16-bit value)
; Output: R2 (number of set bits, 0-16)
; Uses:   R3 (loop counter), R4 (limit = 16), R5 (LSB mask),
;         R6 (shift control), R7 (throwaway for AND / flag-setting)
;
; Strategy: test LSB, shift right by 1, repeat 16 times.

    LOADI R1, #0x0F       ; test value (4 set bits)
    LOADI R2, #0          ; count = 0
    ; complete the problem setup here
    LOADI R3, #0           ; counter = 0
    LOADI R4, #16          ; limit = 16
    LOADI R5, #0x1         ; LSB mask 
    LOADI R6, #1           ; shift control (right)
LOOP:
    ; complete loop
    AND R7, R1, R5
    ADD R3, R3, R7
    SHFT R1, R4, R6
    SUB R7, R4, R3
    BLT   LOOP             ; if counter < 16, continue
DONE:
    HALT