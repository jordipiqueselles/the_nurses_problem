/*********************************************
 * OPL 12.7.1.0 Model
 * Author: pique
 * Creation Date: 24/10/2017 at 11.39.24
 *********************************************/

int nEnfermeras=...;
int nHoras=...;
int demand_h=...;
int minHours=...;
int maxHours=...;
int maxConsec=...;
int maxPresence=...;

range N=1..nEnfermeras;
range H=1..nHoras;
range StartM=1..(nHoras-maxConsec);
range rangeMaxC=1..maxConsec;

//Variables
dvar boolean Wn; //La enfermera n trabaja

dvar float+ WH[n in N, h in H];
dvar float+ E[n in N,h in H];
dvar float+ S[n in N, h in H];
dvar float+ DJ[n in N,h in H];
dvar int comienzo_n; 
dvar int final_n;

minimize sum(n in N) Wn;

subject to{
	
	//Constraint 1
	forall(h in H)
	  sum(n in N)
	    WH[n,h] >= demand_h;
	    
	//Constraint 2
	forall(n in N)
	  sum(h in H)
	    WH[n,h] >= minHours;
	    
	//Constraint 3
	forall(n in N)
	  sum(h in H)
	    WH[n,h] <= maxHours;    
	    
	//Constraint 4
	forall(n in N)
		forall(start in StartM)
	  		sum(h in rangeMaxC)
	  		  WH[n,h+start] <=maxConsec; 
	  		  
	//Constraint 5
	forall(n in N)  
		final_n-comienzo_n <= maxPresence;	
		
	//Constraint 6
	forall(n in N)
		sum(h in H)
	  		WH[n,h] >= Wn;
	
	//Constraint 7
	forall(n in N)
		sum(h in H)
	  		WH[n,h] <= Wn*nHoras;	
	  		
	//Constraint 8
	forall(n in N)
	  forall(h in H)
		DJ[n,h]+DJ[n,h+1] <= WH[n,h] +WH[n,h+1]+ 1;
		
	//Constraint 9
	forall(n in N)
		S[n,1] == WH[n,1];
	
	//Constraint 10
	forall(n in N)
	  forall(h in H)
	    S[n,h-1]+WH[n,h] >= S[n,h];
	
	//Constraint 11
	forall(n in N)
	  forall(h in H)
	    S[n,h-1]+WH[n,h] <= 2*S[n,h];
	    
	//Constraint 12
	forall(n in N)
	  E[n,nHoras]== WH[n,nHoras];
	  
	//Constraint 13
	forall(n in N)
	  forall(h in H)
	    E[n,h+1]+WH[n,h]>= E[n,h];
	
	//Constraint 14
	forall(n in N)
	  forall(h in H)
	    E[n,h+1]+WH[n,h] <= 2*E[n,h];
	    
	//Constraint 15
	forall(n in N)
	  forall(h in H)
	    S[n,h]+E[n,h] >= 2*DJ[n,h];
	
	//Constraint 16
	forall(n in N)
	  forall(h in H)
	    S[n,h]+E[n,h] <= DJ[n,h]+1;
	    
	//Constraint 17
	forall(n in N)
		comienzo_n == nHoras - sum(h in H)S[n,h];
		
	//Constraint 18
	forall(n in N)
	  	final_n == sum(h in H)E[n,h];
}
