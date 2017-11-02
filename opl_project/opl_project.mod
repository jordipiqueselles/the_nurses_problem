/*********************************************
 * OPL 12.7.1.0 Model
 * Author: pique
 * Creation Date: 24/10/2017 at 11.39.24
 *********************************************/
int nHoras=24;
int nNurses=...;
int minHours=...;
int maxHours=...;
int maxConsec=...;
int maxPresence=...;

range N=1..nNurses;
range H=1..nHoras;
int demand[d in H]=...;

range StartM=1..(nHoras-maxConsec-1);
range rangeMaxC=1..(maxConsec+1);

//Variables
dvar boolean Wn[n in N]; //La enfermera n trabaja

dvar boolean WH[n in N, h in H];
dvar boolean E[n in N, h in H];
dvar boolean S[n in N, h in H];
dvar boolean DJ[n in N, h in H];
dvar int comienzo[n in N]; 
dvar int final[n in N];

minimize sum(n in N) Wn[n];

subject to{
	
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
	  		  WH[n,h+start] <=maxConsec; 
	  		  
	//Constraint 5
	//No nurse can stay at the hospital for more than maxPresence hours
	forall(n in N)  
		final[n]-comienzo[n] <= maxPresence;	
		
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
		if (h < nHoras)
			DJ[n,h]+DJ[n,h+1] <= WH[n,h] +WH[n,h+1]+ 1;
		
	//Relación S y WH	
	//Constraint 9
	forall(n in N)
		S[n,1] == WH[n,1];
	
	//Constraint 10
	forall(n in N)
	  forall(h in H)
	    if (h > 1)
	    	S[n,h-1]+WH[n,h] >= S[n,h];
	
	//Constraint 11
	forall(n in N)
	  forall(h in H)
	    if (h > 1)
	    	S[n,h-1]+WH[n,h] <= 2*S[n,h];
	    
	//Relación E y WH
	//Constraint 12
	forall(n in N)
	  E[n,nHoras]== WH[n,nHoras];
	  
	//Constraint 13
	forall(n in N)
	  forall(h in H)
	    if (h < nHoras)
	    	E[n,h+1]+WH[n,h]>= E[n,h];
	
	//Constraint 14
	forall(n in N)
	  forall(h in H)
	    if (h < nHoras)
	    	E[n,h+1]+WH[n,h] <= 2*E[n,h];
	    
	//Relación DJ con S y E
	//Constraint 15
	forall(n in N)
	  forall(h in H)
	    S[n,h]+E[n,h] >= 2*DJ[n,h];
	
	//Constraint 16
	forall(n in N)
	  forall(h in H)
	    S[n,h]+E[n,h] <= DJ[n,h]+1;
	    
	//Constraint 17
	//Comienzo_n
	forall(n in N)
		comienzo[n] == nHoras - sum(h in H)S[n,h];
		
	//Constraint 18
	//Final_n
	forall(n in N)
	  	final[n] == sum(h in H)E[n,h];

}

execute {
	
	for (var n=1;n<=nNurses;n++)
		for (var h=1; h<=nHoras; h++)
			writeln("" + WH[n][h]);
		writeln('\n');
};
