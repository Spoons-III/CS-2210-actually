; Input:  R3 (upper limit N)
; Output: R2 (sum of 1 + 2 + ... + N)
; Uses:   R0 (constant 1), R1 (counter), R4 (throwaway for flag-setting)

START:
    LOADI   R0, #1        ; constant 1
    ; three more LOADI here
    LOADI R1, #0          ; counter = 0
    LOADI R2, #0          ; sum = 0
    LOADI R3, #100         ; a (test value)
LOOP:
    ; complete loop here
    ADD R2, R2, R1
    ADD R1, R1, R0
    SUB R4, R1, R3
    BLT LOOP
    ADD R2, R2, R1
DONE:
    HALT