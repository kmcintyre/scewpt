function ball() {
	this.x = 0;
	this.y = 0;
	this.direction = 0;
	this.length = 1;
}

function team(name) {
	this.name = name;
	this.hail = '';
	this.players = [];
	this.formations = [];
}

function position(name) {
	this.name = name; 
}

function player(name) {
	this.name = name;
	this.number = '-1';	
	this.position = null;
	player.status = null;
	player.height = null;
	player.weight = null;	
	player.profile = null;	
}

status_types = {};

status_types.ACT = "Active";
status_types.RES = "Injured Reserve";
status_types.NON = "Non Football Related Injured Reserve"
status_types.SUS = "Suspended"
status_types.PUP = "Physically Unable to Perform"
status_types.UDF = "Unsigned Draft Pick"
status_types.EXE = "Exempt" 

formation_types = {}

formation_types.O = "offense";
formation_types.D = "defense";
formation_types.ST = "special teams";

var positions = {};

positions.C = new position('Center');
positions.B = new position('Back');
positions.QB = new position('Quarterback');
positions.RB = new position('Running Back');
positions.HB = new position('Half Back');
positions.G = new position('Guard');
positions.OG = new position('Offensive Guard');
positions.RG = new position('Right Guard');
positions.LG = new position('Left Guard');
positions.T = new position('Tackle');
positions.RT = new position('Right Tackle');
positions.LT = new position('Left Tackle');
positions.TE = new position('Tight End');
positions.WR = new position('Wide Receiver');

positions.DE = new position('Defesive End');
positions.DT = new position('Defesive Tackle');
positions.LB = new position('Linebacker');
positions.ILB = new position('Inside Linebacker');
positions.MLB = new position('Middle Linebacker');
positions.OLB = new position('Outerside Linebacker');
positions.CB = new position('Cornerback');
positions.S = new position('Safety');
positions.FS = new position('Free Safety');
positions.SS = new position('Strong Safety');

positions.K = new position('Kicker');
positions.H = new position('Holder');
positions.P = new position('Punter');
positions.LS = new position('Long Snapper');
positions.R = new position('Returner');
positions.KR = new position('Kick Returner');
positions.PR = new position('Punt Returner');

function formation(name) {
	this.name = name;
	this.alignment = [];
	
	this.align = function (p, x, y) {
		this.alignment[this.alignment.length] = [p, x, y];	
	}	
}

formations = {}

var offense = new formation("Offense");
offense.type = formation_types.O;
offense.align(positions.C, 0, 0);
offense.align(positions.RG, 1, 0);
offense.align(positions.LG, -1, 0);
offense.align(positions.RT, 2, 0);
offense.align(positions.LT, -2, 0);
offense.align(positions.QB, 0, 1);
offense.align(positions.RB, 0, 2);
offense.align(positions.RB, 0, 3);
offense.align(positions.TE, 3, 0);
offense.align(positions.WR, 5, 0);
offense.align(positions.WR, -5, 0);

formations.O = offense;

var defense = new formation("Defense");
defense.type = formation_types.D;
defense.align(positions.DT, .5, 0);
defense.align(positions.DT, -.5, 0);
defense.align(positions.DE, 2, 0);
defense.align(positions.DE, -2, 0);
defense.align(positions.LB, 0, 1);
defense.align(positions.LB, 2, 1);
defense.align(positions.LB, -2, 1);
defense.align(positions.CB, 5, 0);
defense.align(positions.CB, -5, 0);
defense.align(positions.S, 0, 5);
defense.align(positions.FS, 5, 5);
formations.D = defense;

var kickoff = new formation("Kickoff");
kickoff.type = formation_types.ST;
kickoff.align(positions.K, 0, 1);
kc = new position('Kick Coverage');
for (x = 0; x < 10; x++) {	
	kickoff.align(kc, 5 - x, 0);
}
formations.K = kickoff;

var kick_return = new formation("Kick Return");
kick_return.type = formation_types.ST;
kub = new position('Kick Up Back');
for (x = 0; x < 5; x++) {
	kick_return.align(kub, 2 - x, 0);
}
kick_return.align(kub, -3, 1);
kick_return.align(kub, 3, 1);
kick_return.align(kub, -3, 3);
kick_return.align(kub, 3, 3);
kick_return.align(positions.KR, 3, 5);
kick_return.align(positions.KR, -3, 5);

formations.KR = kick_return;


var punt = new formation("Punt");
punt.type = formation_types.ST;
punt.alignment = offense.alignment.slice(0,5);
punt.align(positions.P, 0, 3);
punt.align(new position('Punt Coverage'), 5, 0);
punt.align(new position('Punt Coverage'), -5, 0);
ub = new position('Up Back');
for (x = 0; x < 3; x++) {
	punt.align(ub, 1 - x, 2);
}
formations.P = punt;

