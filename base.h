#include <stdio.h>
#include <stdbool.h>
static void print(const char* str) {
    printf("%s\n", str);
}

/*static void print_num(double num) {
    printf("%g\n", num);
}*/

union VarUnion {
    const char* str;
    double num;
    bool boolean;
};

enum Kind {
    STR,
    NUM,
    BOOLEAN,
    NONE
};

typedef struct {
    union VarUnion varion;
    enum Kind kind;
} Var;

static void print_var(Var var) {
    if (var.kind == STR) {
        printf("%s\n", var.varion.str);
    } 
    else if (var.kind == NUM) {
        printf("%g\n", var.varion.num);
    }
    else if (var.kind == BOOLEAN) {
        const char* text = var.varion.boolean == true ? "true" : "false";
        printf("%s\n", text);
    }
}