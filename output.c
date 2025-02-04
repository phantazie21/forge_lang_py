#include "base.h"
int main(int argc, const char** argv) {
	union var string;
	string.str = "kuki";
	union var num;
	num.num = 0.0;
	union var boolean;
	boolean.boolean = true;
	union var nothing;
	print("kuki");
	print_num(0.0);
	print("true");
	print_num(0.0);
	print("HALLO");
	return 0;
}