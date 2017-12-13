/*********************************************
 * OPL 12.7.1.0 Model
 * Author: pique
 * Creation Date: 24/10/2017 at 11.39.24
 *********************************************/
int hours=...;
int nHoras=hours;
int numNurses=...;
int nNurses=numNurses;
int minHours=...;
int maxHours=...;
int maxConsec=...;
int maxPresence=...;

range N=1..nNurses;
range H=1..nHoras;
int demand[d in H]=...;

range StartM=1..(nHoras-maxConsec);
range rangeMaxC=0..maxConsec;

//Variables
dvar boolean Wn[n in N]; //La enfermera n trabaja
dvar boolean WH[n in N, h in H];

minimize sum(n in N) Wn[n];

subject to {
/*
	// Constraint 0
	// Accelerate the solver reducing the combinatorial explosion due to the idle nurses
	forall(n in N)
	  if(n > 1)
	  	Wn[n-1] >= Wn[n];
*/
	//Constraint 1
	//For each hour h, that at least demandh nurses should be working at the hospital
	forall(h in H)
	  sum(n in N)
	    WH[n,h] >= demand[h];

	//Constraint 2
	//Each nurse should work at least minHours hours.
	forall(n in N)
	  sum(h in H)
	    WH[n,h] >= minHours * Wn[n];

	//Constraint 3
	//Each nurse should work at most maxHours hours.
	forall(n in N)
	  sum(h in H)
	    WH[n,h] <= maxHours;

	//Constraint 4
	//Each nurse should work at most maxConsec consecutive hours.
	forall(n in N)
		forall(start in StartM)
	  		sum(h in rangeMaxC)
	  		  WH[n,h+start] <= maxConsec;

	//Constraint 5
	//No nurse can stay at the hospital for more than maxPresence hours
	forall(n in N)
	  forall(h1 in (1..(nHoras - maxPresence)))
	    forall(h2 in ((h1+maxPresence)..nHoras))
	      WH[n,h1] + WH[n,h2] <= 1;

	//Constraint 6
	forall(n in N)
		sum(h in H)
	  		WH[n,h] >= Wn[n];

	//Constraint 7
	forall(n in N)
		sum(h in H)
	  		WH[n,h] <= Wn[n]*nHoras;

	//Constraint 8
	//No nurse can rest for more than one consecutive hour
	forall(n in N)
	  forall(h in H)
		if (h < nHoras-2)
			WH[n,h] <= (WH[n,h+1] + WH[n,h+2]) + (sum(k in ((h+3)..nHoras)) (1-WH[n,k]))/(nHoras-h-2);
			//DJ[n,h]+DJ[n,h+1] <= WH[n,h] + WH[n,h+1]+ 1;

}

execute {
	for (var n=1;n<=nNurses;n++) {
		for (var h=1; h<=nHoras; h++) {
			write("" + WH[n][h]);
 		}
		write('\n');
	}
};
 