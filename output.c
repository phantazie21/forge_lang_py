#include "base.h"
Var string;
Var num;
Var boolean;
Var twoplusfour;
Var minusone;
Var asd;
Var _string;
Var nothing;
Var kuki(Var param1, Var param2) {
	Var _return;
	_return.kind = NONE;
	print_var(param1);
	_return.varion = _string.varion;
	return _return;
}
int main(int argc, const char** argv) {
	string.varion.str = "prefix""kuki""kuki";
	string.kind = STR;
	num.varion.num = 0.0;
	num.kind = NUM;
	boolean.varion.boolean = false;
	boolean.kind = BOOLEAN;
	twoplusfour.varion.num = 6.0;
	twoplusfour.kind = NUM;
	minusone.varion.num = -1.0;
	minusone.kind = NUM;
	asd.varion.num = 12.0;
	asd.kind = NUM;
	_string.varion.str = "prefix""kuki""kuki""prefix""kuki""kuki";
	_string.kind = STR;
	nothing.kind = NONE;
	print_var(_string);
	_string.varion.str = "_string";
	_string.kind = STR;
	print_var(_string);
	print_var(asd);
	print_var(minusone);
	print_var(string);
	print_var(num);
	print_var(boolean);
	print_var(nothing);
	print_var(twoplusfour);
	print("0.1");
	print("HALLO");
	print("fasz""kuki""6");
	if (boolean.varion.boolean || (boolean.varion.boolean || twoplusfour.varion.num)) {
		print("if igaz");
	}
	else {
		print("if hamis");
	}
	kuki(_string, twoplusfour);
	Var arg1;
	arg1.varion.str = "asd";
	arg1.kind = STR;
	Var arg2;
	arg2.varion.num = 0.0;
	arg2.kind = NUM;
	kuki(arg1, arg2);
	Var arg3;
	arg3.varion.str = "penisz";
	arg3.kind = STR;
	Var arg4;
	arg4.varion.str = "fasz";
	arg4.kind = STR;
	kuki(arg3, arg4);
	return 0;
}