    MOV R5, 63
    MOV R0, 0
    SYSCALL R0, 3
    SHR R1, R0, 6
    AND R2, R0, R5
    SYSCALL R0, 0
    SHR R3, R0, 6
    AND R4, R0, R5
    CMP R1, R3
    B.EQ 16
    CMP R1, R3
    B.LT 14
    MOV R5, 1
    B 21
    MOV R5, 0
    B 21
    CMP R2, R4
    B.LT 20
    MOV R5, 3
    B 21
    MOV R5, 2
    SYSCALL R5, 5
    B 0
