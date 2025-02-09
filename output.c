#include "base.h"
int main(int argc, const char** argv) {
	Var string;
	string.varion.str = "kuki";
	string.kind = STR;
	Var num;
	num.varion.num = 0.0;
	num.kind = NUM;
	Var boolean;
	boolean.varion.boolean = true;
	boolean.kind = BOOLEAN;
	Var twoplusfour;
	twoplusfour.varion.num = 6.0;
	twoplusfour.kind = NUM;
	Var nothing;
	nothing.kind = NONE;
	print_var(string);
	print_var(num);
	print_var(boolean);
	print_var(nothing);
	print_var(twoplusfour);
	print("0.1");
	print("HALLO");
	print("fasz""kuki""6");
	return 0;
}