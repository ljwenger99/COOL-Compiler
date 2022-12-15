class Main inherits IO {

	input: Int <- in_int();
	output: Int <- input*input*input;

	main() : Object {
		out_int(output)
	};
};
	
(* cubes an integer *)