dtmc

const int street_length = 100;
const int min_street_length = 50;
const int sidewalk_height = 2;

const int crosswalk_pos = 80;
const int crosswalk_width = 10;
const int crosswalk_height = 11;

const int world_height = (sidewalk_height * 2) + crosswalk_height;

const int max_dist = (street_length * street_length) + (world_height * world_height) + 100;

const int max_speed = 5;

const double neutral = 0.5;
const double change_prob1 = 0.7;
const double change_prob2 = 1 - change_prob1;

// block properties
const int block_height = 2;
const int block_width = 5;
const int block_x1 = 69;
const int block_y1 = 2;
const int block_x2 = 76;
const int block_y2 = 4;

// car properties
const int car_height = 2;
const int car_width = 3;
const int car_y = 5;

// pedestrian properties
const int min_ped_x = 0;

global turn : [0..2] init 0;

// simple bubble of ped and car within a certain distance of each other
formula crash = ((ped_x >= car_x) & (ped_x <= car_x + car_width)) & ((ped_y >= car_y) & (ped_y <= car_y + car_height));

label "crash" = crash;
label "givereward" = ((finished=0) & (car_x = street_length));

// checks distances of pedestrian to car and vis line intersections from the car to the block
label "blocked_vis" = (dist_ped >= min(dist_s1, dist_s2, dist_s3, dist_s4));

formula dist = max(ped_x-car_x, car_x - ped_x) + max(ped_y - car_y, car_y - ped_y);
formula safe_dist = dist > 15;
formula is_on_sidewalk = (ped_y <= sidewalk_height) | (ped_y >= sidewalk_height + crosswalk_height);
formula wait_prob = (crosswalk_pos - ped_x) / 10;

// for calculating if pedestrian is blocked from car view
formula x1 = car_x + car_width;
formula y1 = car_y;
formula x2 = ped_x;
formula y2 = ped_y;

formula dist_ped = ((x2 - x1)*(x2 - x1)) + ((y2 - y1)*(y2 - y1));

// block dist to ped
formula b1 = block_x2 - block_x1;
formula b2 = block_y2 - block_y1;

formula ped_to_block = ((x2 - b1)*(x2 - b1)) + ((y2 - b2)*(y2 - b2));
formula car_to_block = ((x1 - b1)*(x1 - b1)) + ((y1 - b2)*(y1 - b2));

formula vis_blocked = car_to_block > ped_to_block;

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
formula dist_s1 =  s1 ? ((block_x1 - x1)*(block_x1 - x1)) + ((int_s1 - y1)*(int_s1 - y1)) : max_dist;
formula dist_s2 = s2 ? ((int_s2 - x1)*(int_s2 - x1)) + ((block_y2 - y1)*(block_y2 - y2)) : max_dist;
formula dist_s3 = s3 ? ((block_x2 - x1)*(block_x2 - x1)) + ((int_s3 - y1)*(int_s3 - y1)) : max_dist;
formula dist_s4 = s4 ? ((int_s4 - x1)*(int_s4 - x1)) + ((block_y1 - y1)*(block_y1 - y1)) : max_dist;

formula car_fast = (dist_ped <= ((car_v*car_v) + car_v)/2);
formula ped_vis = (dist_ped < min(dist_s1, dist_s2, dist_s3, dist_s4));

formula intersection = (s1 | s2 | s3 | s4);

formula betweencb = (ped_to_block < car_to_block) & (ped_vis);

formula vis_is_blocked = (dist_ped > ped_to_block)&(dist_ped > car_to_block);
formula vis_not_blocked = (dist_ped < ped_to_block)&(car_to_block < ped_to_block);

// new visibility criteria
formula car_left = (car_x < block_x1);
formula block_line = ((block_y2 - block_y1)/(block_x2 - block_x1))*(ped_x - block_x1) + block_y1;
//formula ped_right = block_line > ped_y;
formula ped_right = ((y2 - block_y2)*(block_x2 - block_x1) <= (x2 - block_x2)*(block_y2 - block_y1));
formula car_line1 = ((block_y1 - y1)/(block_x1 - x1))*(ped_x - x1) + y1;
formula car_line2 = ((block_y2 - y1)/(block_x2 - x1))*(ped_x - x1) + y1;
formula same_side1 = ((car_line1 > ped_y) & (car_line2 > ped_y)) | ((car_line1 < ped_y) & (car_line2 < ped_y));
//formula same_side1 = (((((y2 - block_y2)*(block_y2 - y1) - (x2 - block_x2)*(block_x2 - x1)) >= 0) & (((y2 - block_y1)*(block_y1 - y1) - (x2 - block_x1)*(block_x1 - x1)) >= 0)) | (((y2 - block_y2)*(block_y2 - y1) - (x2 - block_x2)*(block_x2 - x1)) < 0) & (((y2 - block_y1)*(block_y1 - y1) - (x2 - block_x1)*(block_x1 - x1)) < 0));
formula left_blocked = car_left & ped_right & !same_side1;

formula car_top = car_x >= block_x1 & car_x <= block_x2;
formula ped_down = y2 <= block_y2;
formula same_side2 = (((((y2 - block_y2)*(block_y2 - y1) - (x2 - block_x2)*(block_x2 - x1)) >= 0) & (((y2 - block_y2)*(block_y2 - y1) - (x2 - block_x1)*(block_x1 - x1)) >= 0)) | (((y2 - block_y2)*(block_y2 - y1) - (x2 - block_x2)*(block_x2 - x1)) < 0) & (((y2 - block_y2)*(block_y2 - y1) - (x2 - block_x1)*(block_x1 - x1)) < 0));
formula top_blocked = car_top & ped_down & !same_side2;

formula no_vis = left_blocked | top_blocked;

module Car
car_x : [min_street_length..street_length] init 55;
car_v : [0..max_speed] init 0;
visibility : [0..1] init 1;
finished : [0..1] init 0;
seen_ped : [0..1] init 0;

// changes the visibility variable so we know when the car is able/unable to see ped
[] (turn = 0)&(!no_vis) ->
(visibility' = 1)&(seen_ped' = 1)&(turn' = 1);
[] (turn = 0)&(no_vis) ->
(visibility' = 0)&(turn' = 1);

[] (
        (
            (
             (seen_ped = 1) & (visibility = 1)
            ) &
            (
                (
                    (
                        is_on_sidewalk
                    ) & (
                        (car_x - ped_x) > (2*car_v)
                    )
                ) | (
                    (
                        (car_x - ped_x) <= (2*car_v)
                    ) & (
                        car_v < 2
                    )
                )
            )
        ) |
        (
            (
                (seen_ped = 1) & (visibility = 0)
            ) & 
            (
                (
                    (
                        is_on_sidewalk
                    ) & (
                        (car_x - block_x2) > (2*car_v)
                    )
                ) | (
                    (
                        (car_x - block_x2) <= (2*car_v)
                    ) & (
                        car_v < 2
                    )
                )
            )
        )
    | (
            (seen_ped = 0) & (visibility = 0)
        )
       )  &  (turn = 1) & (finished=0) & (car_x < street_length) & (!crash) -> // Accelerate
// change probabilities based on type of driver and/or environment
0.45: (car_v' = min(max_speed, car_v + 2))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 2)))&(turn' = 2) +
0.45: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 2) +
0.09: (car_x' = min(street_length, car_x + car_v + 0))&(turn' = 2) +
0.01: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 2);

[] (
        (
            (
                (seen_ped = 1) & (visibility = 1)
            ) &    (
                (
                    car_v > 0
                ) & (
                    (
                        (car_x - ped_x) <= (2*car_v)
                    ) & (
                        car_v > 2
                    )
                ) | (
                    (
                        !is_on_sidewalk
                    ) & (
                        car_x < ped_x
                    )
                )
            )
        ) | (
            (
                (seen_ped = 1) & (visibility = 0)
            ) & (
                (
                    car_v > 0
                ) & (
                    (
                        (car_x - block_x2) <= (2*car_v)
                    ) & (
                        car_v > 2
                    )
                ) | (
                    (
                        !is_on_sidewalk
                    ) & (
                        car_x < block_x2
                    )
                )
            )
        )
    )  &  (turn = 1) & (finished=0) & (car_x < street_length) & (!crash) -> //& (car_v > 0) -> // Brake
// change probabilities based on type of driver and/or environment
0.45: (car_v' = max(0, car_v - 2))&(car_x' = min(street_length, car_x + max(0, car_v - 2)))&(turn' = 2) +
0.45: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 2) +
0.09: (car_x' = min(street_length, car_x + car_v + 0))&(turn' = 2) +
0.01: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 2);

// aggressive car -> would accelerate randomly more likely (0.03) than it would brake (0.02)
[] (
        (
            (
                (seen_ped = 1) & (visibility = 1)
            ) &    (
                (
                    (
                        (car_x - ped_x) <= (2*car_v)
                    ) & (
                        car_v = 2
                    )
                ) | (
                    !is_on_sidewalk & (car_x >= ped_x)
                )
            )
        ) | (
            (
                (seen_ped = 1) & (visibility = 0)
            ) & (
                (
                    (
                        (car_x - block_x2) <= (2*car_v)
                    ) & (
                        car_v = 2
                    )
                ) | (
                    !is_on_sidewalk & (car_x >= block_x2)
                )
            )
        ) 
    )  &  (turn = 1) & (finished=0) & (car_x < street_length) & (!crash) -> // Stays the same speed
0.95: (car_x' = min(street_length, car_x + max(0, car_v)))&(turn' = 2) +
0.02: (car_v' = max(0, car_v - 1))&(car_x' = min(street_length, car_x + max(0, car_v - 1)))&(turn' = 2) +  //breaks
0.03: (car_v' = min(max_speed, car_v + 1))&(car_x' = min(street_length, car_x + min(max_speed, car_v + 1)))&(turn' = 2); //accelerates

[] (turn = 1) & (finished = 0) & (car_x = street_length) -> (finished'=1);
[] (turn = 1) & (finished = 0) & (crash) -> (finished'=1);
[] (turn = 1) & (finished = 1) -> true;


endmodule

module Pedestrian
ped_x : [min_street_length..street_length] init 79;
ped_y : [0..world_height] init 1;

// assumptions:
// 1. pedestrian goal is to cross the street
// 2. pedestrian can only cross from the bottom of the screen to the top of the screen

// 1. made two options, assuming the pedestrian is wanting to walk toward the crosswalk
// with the goal of crossing the street (forward = walk toward cross walk)
[] (turn = 2)&(is_on_sidewalk)&(ped_x < crosswalk_pos) ->
0.9: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0) + // Right
0.08: (ped_x' = max(ped_x - 1, min_street_length))&(turn' = 0) + // Left
0.02: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0); // Up
[] (turn = 2)&(is_on_sidewalk)&(ped_x > (crosswalk_pos + crosswalk_width)) ->
0.9: (ped_x' = max(ped_x - 1, min_street_length))&(turn' = 0) + // Left
0.08: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0) + // Right
0.02: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0); // Up

// conditions for ped to start crossing the street
// 2.a 40% probability of crossing street when at the crosswalk
// 30% chance of walking left or right is it doesn't cross the street
[] (turn = 2)&(!ped_vis)&(ped_x >= crosswalk_pos)&(ped_x <= (crosswalk_pos + crosswalk_width))&(is_on_sidewalk) -> // !car_fast)&
0.4: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
0.3: (ped_x' = max(ped_x - 1, min_street_length))&(turn' = 0) + // Left
0.3: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

// 2.b 10% chance of crossing the street given the ped can see the car and is a certain distance away from the car
// and is at the crosswalk
// 90% chance of doing other things
[] (turn = 2)&(ped_vis)&(ped_x >= crosswalk_pos)&(ped_x <= (crosswalk_pos + crosswalk_width))&(is_on_sidewalk) -> //(car_fast)
0.1: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
0.45: (ped_x' = max(ped_x - 1, min_street_length))&(turn' = 0) + // Left
0.45: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

// if ped crossing, keep crossing
// 3.a condition for if pedestrian is crossing, then ...keep crossing, etx
[] (turn = 2)&(!is_on_sidewalk)&(!car_fast) -> //&(ped_y >= sidewalk_height) ->
0.9: (ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
0.08: (ped_y' = max(ped_y - 1, 0))&(turn' = 0) + // Down
0.01: (ped_x' = max(ped_x - 1, min_street_length))&(turn' = 0) + // Left
0.01: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

// ped avoids car
// 3.b. if ped crossing and car at a certain distance then the ped tries to avoid the car
[] (turn = 2)&(!is_on_sidewalk)&(car_fast) ->//&(ped_y >= sidewalk_height)&(car_fast) ->
// how to show that pedestrian is avoiding the car
// adding 40% probability that the pedestrian acts like "normal" like in action 4.
(0.3 + (0.4*0.9)):(ped_y' = min(ped_y + 1, world_height))&(turn' = 0) + // Up
(0.3 + (0.4*0.08)): (ped_y' = max(ped_y - 1, 0))&(turn' = 0) + // Down
0.4*0.01: (ped_x' = max(ped_x - 1, min_street_length))&(turn' = 0) + // Left
0.4*0.01: (ped_x' = min(ped_x + 1, street_length))&(turn' = 0); // Right

endmodule

rewards
[] (finished=0) & (car_x = street_length) : 10;
endrewards