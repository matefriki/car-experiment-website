mdp

const int street_length = 100;
const int sidewalk_height = 2;

const int crosswalk_pos = 80;
const int crosswalk_width = 10;
const int crosswalk_height = 11;

const int max_speed = 3;

const double neutral = 0.5;
const double change_prob1 = 0.7;
const double change_prob2 = 1 - change_prob1;

// block properties
const int block_height = 2;
const int block_width = 5;
const int block_x1 = {bottom_corner_x};
const int block_y1 = {bottom_corner_y};
const int block_x2 = {top_corner_x};
const int block_y2 = {top_corner_y};
 
// car properties
const int car_height = 2;
const int car_width = max_speed;

const int world_height = (sidewalk_height * 2) + crosswalk_height;

global turn : [0..2] init 0;

// simple bubble of ped and car within a certain distance of each other
label "crash" = ((ped_x >= car_x) & (ped_x <= ped_x + car_width)) & ((ped_y >= car_y) & (ped_y <= car_y + car_height));

// checks distances of pedestrian to car and vis line intersections from the car to the block
label "blocked_vis" = blocked_view & ped_behind_block;

formula dist = max(ped_x-car_x, car_x - ped_x) + max(ped_y - car_y, car_y - ped_y);	
formula safe_dist = dist > 15;
formula is_on_sidewalk = (ped_y < sidewalk_height) | (ped_y > sidewalk_height + crosswalk_height);
formula wait_prob = (crosswalk_pos - ped_x) / 10;
formula crash_over = ((ped_x >= car_x) & (ped_x <= ped_x + car_width)) & ((ped_y >= car_y) & (ped_y <= car_y + car_height));

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
formula dist_s1 =  s1 ? ((block_x1 - x1)*(block_x1 - x1)) + ((int_s1 - y1)*(int_s1 - y1)) : 20000;
formula dist_s2 = s2 ? ((int_s2 - x1)*(int_s2 - x1)) + ((block_y2 - y1)*(block_y2 - y2)) : 20000;
formula dist_s3 = s3 ? ((block_x2 - x1)*(block_x2 - x1)) + ((int_s3 - y1)*(int_s3 - y1)) : 20000;
formula dist_s4 = s4 ? ((int_s4 - x1)*(int_s4 - x1)) + ((int_s4 - y1)*(int_s4 - y1)) : 20000;

//block in Q4 in realtion to car as origin. -- NOT Scalable
formula blocked_view = (((((y2 -  y1)/(x2 - x1))*(block_x1 - x1) + y1) > block_y1) & ((((y2 -  y1)/(x2 - x1))*(block_x1 - x1) + y1) < block_y2)) | (((((x2 - x1)/(y2 - y1))*(block_y2 - y1) + x1) > block_x1) & ((((x2 - x1)/(y2 - y1))*(block_y2 - y1) + x1) < block_x2));
formula ped_behind_block = ped_x > block_x1;
//formula block_q1 = (((((y2 -  y1)/(x2 - x1))*(block_x1 - x1) + y1) > block_y1) & ((((y2 -  y1)/(x2 - x1))*(block_x1 - x1) + y1) < block_y2)) | (((((x2 - x1)/(y2 - y1))*(block_y1 - y1) + x1) > block_x1) & ((((x2 - x1)/(y2 - y1))*(block_y1 - y1) + x1) < block_x2));
//formula blocked_view = block_q4 | block_q1;

module Car
	car_x : [0..street_length] init {car_x};
	car_v : [0..max_speed] init 0;
	car_y : [0..world_height] init {car_y};
	visibility : [0..1] init 1;
	crashed : [0..1] init 0;

	[] (turn = 0) & safe_dist -> // Accelerate
		// change_prob/neutral/... etc. based on type of driver
		0.5: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 1) +
		0.5: (car_v' = min(max_speed, car_v + 2))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 2)))&(turn' = 1);
	[] (turn = 0)  -> // Brake
		// probability changes based on type of driver e.g. aggressive: +/- 2 then higher probability, cautious: then lower probability
		0.5: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 1) +
		0.5: (car_v' = max(0, car_v - 2))&(car_x' = min(street_length, car_x + max(0, car_v - 2)))&(turn' = 1);
	[] (turn = 0) -> // Stays the same speed
		(car_x' = min(street_length, car_x + max(0, car_v)))&(turn' = 1);

	// changes the visibility variable so we know when the car is able/unable to see ped
	[] (turn = 1)&(dist_ped < min(dist_s1, dist_s2, dist_s3, dist_s4)) ->
		(visibility' = 1)&(turn' = 2);
	[] (turn = 1)&(dist_ped >= min(dist_s1, dist_s2, dist_s3, dist_s4)) ->
		(visibility' = 0)&(turn' = 2);
	
	[] (turn = 1)&(crash_over) -> (crashed' = 1);
	
endmodule

module Pedestrian
	ped_x : [0..street_length] init {person_x};
	ped_y : [0..world_height] init {person_y};
	
	[] (is_on_sidewalk)&(ped_x > crosswalk_pos)&(ped_x < (crosswalk_pos + crosswalk_width))&(turn = 2) -> // pedestrian choices from the sidewalk
		0.25: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		0.25: (ped_y' = max(ped_y - 1, 0))&(turn' = 0) + // Down
		0.25: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		0.25: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right
	[] (is_on_sidewalk)&(ped_x < crosswalk_pos)&(ped_x > (crosswalk_pos + crosswalk_width))&(turn = 2) ->
		1/3: (ped_y' = max(ped_y - 1, 0))&(turn' = 0) + // Down
		1/3: (ped_x' = max(ped_x - 1, 0))&(turn' = 0) + // Left
		1/3: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right
//	[] (!is_on_sidewalk)&(turn = 2) -> // pedestrian choices from the crosswalk
//		0.9: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
//		0.1: (ped_y' = max(ped_y - 1, 0))&(turn' = 0); // Down

	// trying to increase probability that ped is hidden from view of car
	// ped crosses when car is close to crosswalk
	[] (!is_on_sidewalk)&(turn = 2) -> // pedestrian choices from the crosswalk
		0.5: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		0.5: (ped_y' = max(ped_y - 1, 0))&(turn' = 0); // Down
	[] (!is_on_sidewalk)&(!safe_dist)&(turn = 2) -> // pedestrian choices from the crosswalk
		0.9: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
		0.1: (ped_y' = max(ped_y - 1, 0))&(turn' = 0); // Down
	
	// uncomment this to end path simulation
//	[] (turn = 2)&(crash_over) -> true;
endmodule

