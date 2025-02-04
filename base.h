#include <stdio.h>
#include <stdbool.h>
static void print(const char* str) {
    printf("%s\n", str);
}
static void print_num(double num) {
    printf("%g\n", num);
}
union var {
    const char* str;
    double num;
    bool boolean;
};