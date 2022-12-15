mdp

const int street_length = 75;
const int min_street_length = 25;
const int sidewalk_height = 2;

const int crosswalk_pos = 45;
const int crosswalk_width = 10;
const int crosswalk_height = 11;

const int world_height = (sidewalk_height * 2) + crosswalk_height;

const int max_speed = 5;

// block properties, don't eliminate for no visiblity, used in some strategies as for nov 22
const int block_height = 2;
const int block_width = 5;
const int block_x1 = crosswalk_pos - 5; // {bottom_corner_x}
const int block_y1 = sidewalk_height; // {bottom_corner_y}
const int block_x2 = block_x1 + block_width; // {top_corner_x}
const int block_y2 = sidewalk_height + block_height; //{top_corner_y}
 
// car properties
const int car_height = 1; // was two
const int car_width = 3;
const int car_y = 5; // {car_y}

global turn : [0..2] init 0;

// simple bubble of ped and car within a certain distance of each other
formula crash = ((ped_x >= car_x) & (ped_x <= car_x + car_width)) & ((ped_y >= car_y) & (ped_y <= car_y + car_height));

label "crash" = crash;
label "givereward" = ((finished=0) & (car_x = street_length));

formula dist = max(ped_x-car_x, car_x - ped_x) + max(ped_y - car_y, car_y - ped_y);	
formula safe_dist = dist > 15;

formula wait_prob = (crosswalk_pos - ped_x) / 10;


formula car_close_crosswalk = ((car_x > crosswalk_pos - 10) & (car_x < crosswalk_pos + crosswalk_width));
formula car_close_block = ((car_x > block_x1 - 5) & (car_x < block_x2));
formula car_close_ped = (ped_x - car_x < 2*car_v);

module Car
car_x : [min_street_length..street_length] init 25; //{car_x};
car_v : [0..max_speed] init max_speed-1;
finished : [0..1] init 0;

    // changes the visibility variable so we know when the car is able/unable to see ped
    [] (turn = 0) -> (turn'=1);

	[accelerate] (turn = 1) & (finished=0) & (car_x < street_length) & (!crash) -> // Accelerate
	0.45: (car_v' = min(max_speed, car_v + 2))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 2)))&(turn' = 2) +
	0.45: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 2) +
	0.10: (car_x' = min(street_length, car_x + car_v + 0))&(turn' = 2);

	[brake] (turn = 1) & (finished=0) & (car_x < street_length) & (!crash) -> //& (car_v > 0) -> // Brake
	0.45: (car_v' = max(0, car_v - 2))&(car_x' = min(street_length, car_x + max(0, car_v - 2)))&(turn' = 2) + 
	0.45: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 2) +
	0.10: (car_x' = min(street_length, car_x + car_v + 0))&(turn' = 2);
	
	[nop] (turn = 1) & (finished=0) & (car_x < street_length) & (!crash) -> // Stays the same speed
	0.80: (car_x' = min(street_length, car_x + max(0, car_v)))&(turn' = 2) +
	0.10: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 2) +  //breaks
	0.10: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 2); //accelerates

	[] (turn = 1) & (finished = 0) & ((car_x = street_length) | (crash)) -> (finished'=1);
	[] (turn = 1) & (finished = 1) -> true;
	
	 
	 
endmodule

// formula move_xx_yy_zz = xx: (ped_x' = min(street_length, ped_x+1))&(turn'=0) + yy: (ped_y'=min(world_height, ped_y+1))&(turn'=0) + zz: (turn'=0);
formula is_on_sidewalk = (ped_y <= sidewalk_height) | (ped_y >= sidewalk_height + crosswalk_height);
formula on_crosswalk = (ped_x >= crosswalk_pos) & (ped_x <= crosswalk_pos+crosswalk_height);

module Pedestrian
	ped_x : [min_street_length..street_length] init (crosswalk_pos - 5); // {person_x}
	ped_y : [0..world_height] init 0; // {person_y}

	[] (turn = 2)&(!is_on_sidewalk) -> 0.7: (ped_y'=min(world_height, ped_y+1))&(turn'=0) + 0.3: (turn'=0);
	
//	[] (turn=2)&(is_on_sidewalk)&(blocked_path) ->	0.5: (ped_x' = min(street_length, ped_x+1))&(turn'=0) + 0.3: (ped_x' = max(0, ped_x-1))&(turn'=0) + 0.2: (turn'=0);

	[] (turn=2)&(is_on_sidewalk)&(on_crosswalk) ->
	0.45: (ped_x' = min(street_length, ped_x+1))&(turn'=0) + 0.45: (ped_y'=min(world_height, ped_y+1))&(turn'=0) + 0.1: (turn'=0);

	[] (turn=2)&(is_on_sidewalk)&(!on_crosswalk) ->
	0.8: (ped_x' = min(street_length, ped_x+1))&(turn'=0) + 0.1: (ped_y'=min(world_height, ped_y+1))&(turn'=0) + 0.1: (turn'=0);

endmodule