class Main inherits IO {
	x: Bool <- false;
	main(): Object
	{10};
};
class Main1 {
	y: Int <- 2; -- let a: Int <- 4 in a + 2;
	extra(a:Int, b:Int): Object
	{a+b};
};

class Main2 inherits
Main1{
	extra(a:Int, b:Int): Object
	{a-b};
	c : String;
	z : Int; -- illegal
	--x : Bool <- true;
	-- legal
};