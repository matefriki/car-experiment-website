mdp

const int street_length = 100;
const int sidewalk_height = 2;

const int crosswalk_pos = 80;
const int crosswalk_width = 10;
const int crosswalk_height = 11;

const int world_height = (sidewalk_height * 2) + crosswalk_height;

const int max_dist = (street_length * street_length) + (world_height * world_height) + 100;

const int max_speed = 3;

const double neutral = 0.5;
const double change_prob1 = 0.7;
const double change_prob2 = 1 - change_prob1;

// block properties
const int block_height = 2;
const int block_width = 5;
const int block_x1 = crosswalk_pos - 5; // {bottom_corner_x}
const int block_y1 = sidewalk_height; // {bottom_corner_y}
const int block_x2 = block_x1 + block_width; // {top_corner_x}
const int block_y2 = sidewalk_height + block_height; //{top_corner_y}

// car properties
const int car_height = 2;
const int car_width = max_speed;
const int car_y = 5;

global turn : [0..2];

// simple bubble of ped and car within a certain distance of each other
formula crash = ((ped_x >= car_x) & (ped_x <= car_x + car_width)) & ((ped_y >= car_y) & (ped_y <= car_y + car_height));

label "crash" = crash;
label "givereward" = ((finished=0) & (car_x = street_length));

// checks distances of pedestrian to car and vis line intersections from the car to the block
label "blocked_vis" = (dist_ped >= min(dist_s1, dist_s2, dist_s3, dist_s4));

formula dist = max(ped_x-car_x, car_x - ped_x) + max(ped_y - car_y, car_y - ped_y);	
formula safe_dist = dist > 15;
formula is_on_sidewalk = (ped_y < sidewalk_height) | (ped_y > sidewalk_height + crosswalk_height);
formula wait_prob = (crosswalk_pos - ped_x) / 10;

// for calculating if pedestrian is blocked from car view
formula x1 = car_x + car_width;
formula y1 = car_y;
formula x2 = ped_x;
formula y2 = ped_y;

formula int_s1 = (((y2 -  y1)/(x2 - x1))*(block_x1 - x1) + y1); // x = block_x1
formula int_s2 = (((x2 - x1)/(y2 - y1))*(block_y2 - y1) + x1); // y = block_y2
formula int_s3 = (((y2 -  y1)/(x2 - x1))*(block_x2 - x1) + y1); // x = block_x2
formula int_s4 = (((x2 - x1)/(y2 - y1))*(block_y1 - y1) + x1); // y = block_y1

// checks if there are intersections of the visibility line from car to pedestrian at each side of the block
formula s1 = (int_s1 > block_y1) & (int_s1 < block_y2); // (block_x1, int_s1)
formula s2 = (int_s2 > block_x1) & (int_s2 < block_x2); // (int_s2, block_y2)
formula s3 = (int_s3 > block_y1) & (int_s3 < block_y2); // (block_x2, int_s3)
formula s4 = (int_s4 > block_x1) & (int_s4 < block_x2); // (int_s4, block_y1)

// distance formulas for car to pedestrian and each intersection (above)
formula dist_ped = ((x2 - x1)*(x2 - x1)) + ((y2 - y1)*(y2 - y1));
formula dist_s1 =  s1 ? ((block_x1 - x1)*(block_x1 - x1)) + ((int_s1 - y1)*(int_s1 - y1)) : max_dist;
formula dist_s2 = s2 ? ((int_s2 - x1)*(int_s2 - x1)) + ((block_y2 - y1)*(block_y2 - y2)) : max_dist;
formula dist_s3 = s3 ? ((block_x2 - x1)*(block_x2 - x1)) + ((int_s3 - y1)*(int_s3 - y1)) : max_dist;
formula dist_s4 = s4 ? ((int_s4 - x1)*(int_s4 - x1)) + ((int_s4 - y1)*(int_s4 - y1)) : max_dist;

formula car_fast = (dist_ped <= ((car_v*car_v) + car_v)/2);
formula ped_vis = (dist_ped < min(dist_s1, dist_s2, dist_s3, dist_s4));

module Car
	car_x : [0..street_length] init 0; // {car_x}
	car_v : [0..max_speed] init 0;
	visibility : [0..1] init 1;
	finished : [0..1] init 0;
	[] (turn = 0) & (finished=0) & (car_x < street_length) & (!crash) -> // Accelerate
	// change probabilities based on type of driver and/or environment
	0.45: (car_v' = min(max_speed, car_v + 2))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 2)))&(turn' = 1) +
	0.45: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 1) +
	0.09: (car_x' = min(street_length, car_x + car_v + 0))&(turn' = 1)+
	0.01: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 1);

	[] (turn = 0) & (finished=0) & (car_x < street_length) & (!crash) & (car_v > 0) -> // Brake
	// change probabilities based on type of driver and/or environment
	0.45: (car_v' = max(0, car_v - 2))&(car_x' = min(street_length, car_x + max(0, car_v - 2)))&(turn' = 1) + 
	0.45: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 1) +
	0.09: (car_x' = min(street_length, car_x + car_v + 0))&(turn' = 1) +
	0.01: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 1);

	// aggressive car -> would accelerate randomly more likely (0.03) than it would brake (0.02)
	[] (turn = 0) & (finished=0) & (car_x < street_length) & (!crash) -> // Stays the same speed
	0.95: (car_x' = min(street_length, car_x + max(0, car_v)))&(turn' = 1) +
	0.02: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 1) +  //breaks
	0.03: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 1); //accelerates

	[] (turn = 0) & (finished = 0) & (car_x = street_length) -> (finished'=1);
	[] (turn = 0) & (finished = 0) & (crash) -> (finished'=1);
	[] (turn=0) & (finished = 1) -> true;


	// changes the visibility variable so we know when the car is able/unable to see ped
	[] (turn = 1)&(ped_vis) ->
	(visibility' = 1)&(turn' = 2);
	[] (turn = 1)&(!ped_vis) ->
	(visibility' = 0)&(turn' = 2);
	 
endmodule

module Pedestrian
	ped_x : [0..street_length] init (crosswalk_pos + 5); // {person_x}
	ped_y : [0..world_height] init 0; //{person_y}

   // assumptions:
		// 1. pedestrian goal is to cross the street
		// 2. pedestrian can only cross from the bottom of the screen to the top of the screen
	
	// 1. made two options, assuming the pedestrian is wanting to walk toward the crosswalk
	// with the goal of crossing the street (forward = walk toward cross walk)
	[] (turn = 2)&(is_on_sidewalk)&(ped_x < crosswalk_pos) ->
		0.9: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0) + // Right
		0.08: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.02: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0); // Up
	[] (turn = 2)&(is_on_sidewalk)&(ped_x > (crosswalk_pos + crosswalk_width)) ->
		0.9: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.08: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0) + // Right
		0.02: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0); // Up

// conditions for ped to start crossing the street
	// 2.a 40% probability of crossing street when at the crosswalk
	// SUBJECT TO CHANGE
	// 30% chance of walking left or right is it doesn't cross the street
	[] (turn = 2)&(!ped_vis | !car_fast)&(ped_x > crosswalk_pos)&(ped_x < (crosswalk_pos + crosswalk_width)) ->
		0.4: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		0.3: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.3: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

	// 2.b 10% chance of crossing the street given the ped can see the car and is a certain distance away from the car
	// and is at the crosswalk
	// SUBJECT TO CHANGE
	// 90% chance of doing other things
	[] (turn = 2)&(ped_vis)&(car_fast)&(ped_x > crosswalk_pos)&(ped_x < (crosswalk_pos + crosswalk_width)) ->
		0.1: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		0.45: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.45: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

// if ped crossing, keep crossing
	// 3.a condition for if pedestrian is crossing, then ...keep crossing, etx
	[] (turn = 2)&(ped_y > sidewalk_height) ->
		0.9: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		0.08: (ped_y' = max(ped_y - 1, 0))&(turn' = 0) + // Down
		0.01: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.01: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

// ped avoids car
	// 3.b. if ped crossing and car at a certain distance then the ped tries to avoid the car
	[] (turn = 2)&(ped_y > sidewalk_height)&(car_fast) ->
		// how to show that pedestrian is avoiding the car
		// adding 40% probability that the pedestrian acts like "normal" like in action 4.
//		0.6: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
//		0.4: (ped_y' = max(ped_y - 1, 0))&(turn' = 0); // Down
		(0.3 + (0.4*0.9)):(ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		(0.3 + (0.4*0.08)): (ped_y' = max(ped_y - 1, 0))&(turn' = 0) + // Down
		0.4*0.01: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.4*0.01: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

endmodule

rewards

//    [] true : -3;
//    [] true : -2;
//    [] true : -1;
//    [] true : 10;
	[] (finished=0) & (car_x = street_length) : 10;

endrewards