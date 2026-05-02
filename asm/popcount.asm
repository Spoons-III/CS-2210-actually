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
    LOADI R6, #0x01           ; shift control (right)
    LUI R6, #0x80
LOOP:
    ; complete loop
    AND R7, R1, R5
    ADD R2, R2, R7
    ADDI R3, R3, #1
    SHFT R1, R1, R6
    SUB R7, R3, R4
    BLT   LOOP             ; if counter < 16, continue
DONE:
    HALT