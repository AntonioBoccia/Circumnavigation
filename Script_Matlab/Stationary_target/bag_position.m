%% DYNAMICAL NETWORK WITH STATIONARY TARGET
bag = rosbag('/home/antonio/catkin_ws/src/circumnavigation_moving_target/bagfiles/Stationary_switching.bag');

agent1_y = select(bag, 'Time', [bag.StartTime bag.EndTime], 'Topic', '/agent1/y');
agent2_y = select(bag, 'Time', [bag.StartTime bag.EndTime], 'Topic', '/agent2/y');
agent3_y = select(bag, 'Time', [bag.StartTime bag.EndTime], 'Topic', '/agent3/y');
agent4_y = select(bag, 'Time', [bag.StartTime bag.EndTime], 'Topic', '/agent4/y');
agent5_y = select(bag, 'Time', [bag.StartTime bag.EndTime], 'Topic', '/agent5/y');

%%
msgsy1= readMessages(agent1_y);
msgsy2= readMessages(agent2_y);
msgsy3= readMessages(agent3_y);
msgsy4= readMessages(agent4_y);
msgsy5= readMessages(agent5_y);

%%
leny1 = length(msgsy1);
leny2 = length(msgsy2);
leny3 = length(msgsy3);
leny4 = length(msgsy4);
leny5 = length(msgsy5);

 
y1_x = zeros(leny1,1);
for i=1:leny1
    y1_x(i) =double(msgsy1{i,1}.Point.X);
end

y1_y = zeros(leny1,1);
for i=1:leny1
    y1_y(i) =double(msgsy1{i,1}.Point.Y);
end


y2_x = zeros(leny2,1);
for i=1:leny2
    y2_x(i) =double(msgsy2{i,1}.Point.X);
end

y2_y = zeros(leny2,1);
for i=1:leny2
    y2_y(i) =double(msgsy2{i,1}.Point.Y);
end

y3_x = zeros(leny3,1);
for i=1:leny3
    y3_x(i) =double(msgsy3{i,1}.Point.X);
end

y3_y = zeros(leny3,1);
for i=1:leny3
    y3_y(i) =double(msgsy3{i,1}.Point.Y);
end

y4_x = zeros(leny4,1);
for i=1:leny4
    y4_x(i) =double(msgsy4{i,1}.Point.X);
end

y4_y = zeros(leny4,1);
for i=1:leny4
    y4_y(i) =double(msgsy4{i,1}.Point.Y);
end

y5_x = zeros(leny5,1);
for i=1:leny5
    y5_x(i) =double(msgsy5{i,1}.Point.X);
end

y5_y = zeros(leny5,1);
for i=1:leny5
    y5_y(i) =double(msgsy5{i,1}.Point.Y);
end