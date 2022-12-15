class Main {

	input: Int <- in_int();
	output: Int - input*input*input;

	main() : Object {
		out_int(output)
	};
};
	
(* cubes an integer *)
(* NEEDS TO INHERIT IO FOR "in_int" AND "out_int" METHODS. *)
(* ABOVE ERROR MAY NOT RAISE AN ERROR FOR A3. ALSO MISSING A '<' IN LINE 4. *)