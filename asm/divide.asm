; Computes the quotient and remainder of a / b
; by repeatedly subtracting b from a.
; Assumes a >= 0, b > 0.
;
; Input:  R1 (a, dividend), R2 (b, divisor, positive)
; Output: R3 (quotient a / b), R4 (remainder a % b)
; Uses:   R5 (throwaway for flag-setting)

    LOADI R1, #17         ; a (test value)
    LOADI R2, #5          ; b (test value)
    LOADI R3, #0          ; quotient = 0
    MOV   R4, R1          ; remainder = a
LOOP:
    ; complete the loop here
    SUB R1, R2
    INC R3
    LOADI R4, R1
    B     LOOP
DONE:
    HALT